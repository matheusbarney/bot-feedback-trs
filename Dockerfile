# Servico do bot do Telegram. Roda separado do whisper-server (outro
# servico no mesmo projeto Railway) — conversa com ele via rede privada,
# configurada em WHISPER_SERVER_URL.

FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py ciclo_atual.json docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "bot.py"]
