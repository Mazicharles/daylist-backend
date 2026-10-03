FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DB_PATH=/data/tasks.db

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 daylist \
    && mkdir /data && chown daylist:daylist /data

COPY main.py start.py ./
USER daylist
EXPOSE 8000
CMD ["python", "start.py"]
