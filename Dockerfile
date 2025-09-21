# Используем официальный Python 3.12 образ
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV BOT_TOKEN="8375687840:AAGYL4HcxkVP2HYTlz3sMjh6g8YafJQslgM"

CMD ["python", "main.py"]
