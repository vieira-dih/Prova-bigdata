import os
import time
import json
import logging
from io import BytesIO
import pandas as pd
import boto3
from botocore.client import Config
import psycopg2
import psycopg2.extras

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin123')
PROCESS_INTERVAL_SECONDS = int(os.environ.get('PROCESS_INTERVAL_SECONDS', '900'))
BUCKET = 'datalake'

def s3_client():
    endpoint = f'http://{MINIO_ENDPOINT}'
    return boto3.client('s3',
                        endpoint_url=endpoint,
                        aws_access_key_id=MINIO_ACCESS_KEY,
                        aws_secret_access_key=MINIO_SECRET_KEY,
                        config=Config(signature_version='s3v4'))

def list_bronze_objects(client):
    resp = client.list_objects_v2(Bucket=BUCKET, Prefix='bronze/')
    for o in resp.get('Contents', []):
        yield o['Key']

def read_json_from_s3(client, key):
    obj = client.get_object(Bucket=BUCKET, Key=key)
    data = obj['Body'].read()
    return json.loads(data)

def preprocess_records(records):
    df = pd.json_normalize(records)
    df = df.drop_duplicates(subset=['id'])
    df['title'] = df.get('title', pd.Series(dtype='object')).fillna('').str.strip()
    df['category'] = df.get('category', pd.Series(dtype='object')).fillna('unknown')
    df['price'] = pd.to_numeric(df.get('price', 0.0), errors='coerce').fillna(0.0)
    if 'rating.rate' in df.columns:
        df['rating_rate'] = pd.to_numeric(df['rating.rate'], errors='coerce')
    elif 'rating' in df.columns:
        df['rating_rate'] = df['rating'].apply(lambda r: r.get('rate') if isinstance(r, dict) else None)
        df['rating_rate'] = pd.to_numeric(df['rating_rate'], errors='coerce').fillna(0.0)
    else:
        df['rating_rate'] = 0.0
    return df

def write_parquet_to_s3(df, key):
    buf = BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    client = s3_client()
    client.put_object(Bucket=BUCKET, Key=key, Body=buf.read())
    logging.info('Wrote parquet %s (%d rows)', key, len(df))

def write_json_to_s3(obj, key):
    client = s3_client()
    body = json.dumps(obj).encode('utf-8')
    client.put_object(Bucket=BUCKET, Key=key, Body=body)
    logging.info('Wrote json %s', key)

def write_aggregates_to_postgres(aggregates):
    # aggregates: dict
    pg_host = os.environ.get('POSTGRES_HOST', 'postgres')
    pg_db = os.environ.get('POSTGRES_DB', 'metabase_db')
    pg_user = os.environ.get('POSTGRES_USER', 'metabase')
    pg_pass = os.environ.get('POSTGRES_PASSWORD', 'metabase123')
    try:
        conn = psycopg2.connect(host=pg_host, dbname=pg_db, user=pg_user, password=pg_pass)
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS aggregates (
            processed_at TIMESTAMP PRIMARY KEY,
            data JSONB
        )
        ''')
        # insert as upsert
        processed_at = aggregates.get('processed_at')
        cur.execute('INSERT INTO aggregates (processed_at, data) VALUES (%s, %s) ON CONFLICT (processed_at) DO UPDATE SET data = EXCLUDED.data', (processed_at, json.dumps(aggregates)))
        conn.commit()
        cur.close()
        conn.close()
        logging.info('Wrote aggregates to Postgres (processed_at=%s)', processed_at)
    except Exception as e:
        logging.exception('Failed to write aggregates to Postgres: %s', e)

def process_once():
    client = s3_client()
    keys = list(list_bronze_objects(client))
    if not keys:
        logging.info('No bronze objects to process')
        return
    all_records = []
    for k in keys:
        try:
            data = read_json_from_s3(client, k)
            if isinstance(data, list):
                all_records.extend(data)
            else:
                all_records.append(data)
        except Exception as e:
            logging.exception('Error reading %s: %s', k, e)
    if not all_records:
        logging.info('No records after reading bronze files')
        return
    df = preprocess_records(all_records)
    silver_key = f'silver/products_clean.parquet'
    write_parquet_to_s3(df, silver_key)
    total_products = int(df['id'].nunique())
    products_per_category = df.groupby('category').size().to_dict()
    avg_price_per_category = df.groupby('category')['price'].mean().round(2).to_dict()
    avg_rating_per_category = df.groupby('category')['rating_rate'].mean().round(2).to_dict()
    gold = {
        'total_products': total_products,
        'products_per_category': products_per_category,
        'avg_price_per_category': avg_price_per_category,
        'avg_rating_per_category': avg_rating_per_category,
        'processed_at': pd.Timestamp.utcnow().isoformat()
    }
    gold_key = 'gold/aggregates.json'
    write_json_to_s3(gold, gold_key)
    # also persist to Postgres so Metabase can query it
    write_aggregates_to_postgres(gold)
    logging.info('Processing complete: %d products', total_products)

def main_loop():
    logging.info('Processor started (interval %s seconds)', PROCESS_INTERVAL_SECONDS)
    while True:
        try:
            process_once()
        except Exception as e:
            logging.exception('Processing failed: %s', e)
        time.sleep(PROCESS_INTERVAL_SECONDS)

if __name__ == '__main__':
    main_loop()
