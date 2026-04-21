FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir requests python-dotenv requests-oauthlib

CMD ["python", "post_to_x.py"]
