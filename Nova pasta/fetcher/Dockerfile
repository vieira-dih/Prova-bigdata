FROM python:3.11-slim
WORKDIR /app

# Install OS-level build deps and upgrade pip to ensure binary wheels can be used
RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc build-essential libpq-dev \
	&& pip install --upgrade pip setuptools wheel \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fetcher.py .
CMD ["python","fetcher.py"]
