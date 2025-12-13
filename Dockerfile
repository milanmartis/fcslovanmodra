# 1) Základný image
FROM python:3.11-slim

# 2) Nech sa nepíšu .pyc a buffer ide von
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3) Pracovný priečinok v kontajneri
WORKDIR /app

# 4) System balíky (Postgres client libs, kompilátory)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5) Najprv requirements (lepšie cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 6) Skopíruj zvyšok projektu
COPY . .

# 7) Nastavenia pre Flask (CLI používaš vo entrypointe)
ENV FLASK_APP=run.py \
    FLASK_ENV=production

# 8) Sprav entrypoint spustiteľný
RUN chmod +x entrypoint.sh

# 9) Port, na ktorom appka beží
EXPOSE 5000

# 10) Spúšťací bod kontajnera
ENTRYPOINT ["./entrypoint.sh"]
