FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl nodejs npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright && playwright install chromium --with-deps

COPY package.json .
RUN npm install

COPY . .
RUN npm run build:css

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
