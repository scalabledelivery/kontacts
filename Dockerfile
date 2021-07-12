FROM python:3-alpine
COPY requirements.txt .
RUN apk add --no-cache curl openssl bash && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
    
WORKDIR /usr/src
COPY src /usr/src

ENV FLASK_ENV=production

ENTRYPOINT python /usr/src/main.py
