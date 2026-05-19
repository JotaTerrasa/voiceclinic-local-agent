FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends ffmpeg curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY web /app/web

RUN pip install --no-cache-dir ".[voice]"

EXPOSE 8000 9092

CMD ["uvicorn", "voiceclinic.api:app", "--host", "0.0.0.0", "--port", "8000"]
