import os
import time
import json
import logging
from datetime import datetime
import requests
import boto3
from botocore.client import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin123')
FETCH_INTERVAL_SECONDS = int(os.environ.get('FETCH_INTERVAL_SECONDS', '600'))
BUCKET = 'datalake'

def s3_client():
    endpoint = f'http://{MINIO_ENDPOINT}'
    return boto3.client('s3',
                        endpoint_url=endpoint,
                        aws_access_key_id=MINIO_ACCESS_KEY,
                        aws_secret_access_key=MINIO_SECRET_KEY,
                        config=Config(signature_version='s3v4'))

def ensure_bucket(client):
    try:
        client.head_bucket(Bucket=BUCKET)
        logging.info('Bucket exists: %s', BUCKET)
    except Exception:
        logging.info('Creating bucket: %s', BUCKET)
        client.create_bucket(Bucket=BUCKET)

def fetch_and_store():
    client = s3_client()
    ensure_bucket(client)
    url = 'https://fakestoreapi.com/products'
    logging.info('Fetching data from %s', url)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    key = f'bronze/products_{ts}.json'
    body = json.dumps(data).encode('utf-8')
    client.put_object(Bucket=BUCKET, Key=key, Body=body)
    logging.info('Uploaded %s (%d bytes)', key, len(body))

def main_loop():
    logging.info('Fetcher started (interval %s seconds)', FETCH_INTERVAL_SECONDS)
    while True:
        try:
            fetch_and_store()
        except Exception as e:
            logging.exception('Failed to fetch and store: %s', e)
        time.sleep(FETCH_INTERVAL_SECONDS)

if __name__ == '__main__':
    main_loop()
