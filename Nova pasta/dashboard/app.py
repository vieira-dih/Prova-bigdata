import os
import json
from flask import Flask, render_template_string
import boto3
from botocore.client import Config

app = Flask(__name__)

MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin123')
BUCKET = 'datalake'

def s3_client():
    endpoint = f'http://{MINIO_ENDPOINT}'
    return boto3.client('s3',
                        endpoint_url=endpoint,
                        aws_access_key_id=MINIO_ACCESS_KEY,
                        aws_secret_access_key=MINIO_SECRET_KEY,
                        config=Config(signature_version='s3v4'))

def read_aggregates():
    client = s3_client()
    try:
        obj = client.get_object(Bucket=BUCKET, Key='gold/aggregates.json')
        return json.loads(obj['Body'].read())
    except Exception:
        return None

TEMPLATE = '''
<html>
  <head><title>Pipeline Dashboard</title></head>
  <body>
    <h1>Pipeline KPIs</h1>
    {% if agg %}
      <p><strong>Total products:</strong> {{ agg.total_products }}</p>
      <h2>Products per category</h2>
      <ul>
        {% for k,v in agg.products_per_category.items() %}
          <li>{{ k }}: {{ v }}</li>
        {% endfor %}
      </ul>
      <h2>Average price per category</h2>
      <ul>
        {% for k,v in agg.avg_price_per_category.items() %}
          <li>{{ k }}: {{ v }}</li>
        {% endfor %}
      </ul>
      <p>Processed at: {{ agg.processed_at }}</p>
    {% else %}
      <p>No aggregates found yet. Run processor.</p>
    {% endif %}
  </body>
</html>
'''

@app.route('/')
def index():
    agg = read_aggregates()
    if agg:
        # convert keys for template access
        class A: pass
        a = A()
        a.total_products = agg.get('total_products')
        a.products_per_category = agg.get('products_per_category', {})
        a.avg_price_per_category = agg.get('avg_price_per_category', {})
        a.avg_rating_per_category = agg.get('avg_rating_per_category', {})
        a.processed_at = agg.get('processed_at')
        return render_template_string(TEMPLATE, agg=a)
    return render_template_string(TEMPLATE, agg=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
