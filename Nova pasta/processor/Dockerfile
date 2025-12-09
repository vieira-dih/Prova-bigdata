FROM python:3.11-slim
WORKDIR /app

# Install OS-level build deps (needed for packages like pyarrow) and upgrade pip
RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc build-essential libssl-dev libpq-dev pkg-config curl \
	&& pip install --upgrade pip setuptools wheel \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY processor.py .
CMD ["python","processor.py"]
