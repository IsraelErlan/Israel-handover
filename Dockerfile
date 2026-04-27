FROM python:3.12-slim

WORKDIR /app

# gcc is required to compile pymavlink's C extensions
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8080

ENV DATA_FILE=/app/data/log_file_test_01.bin
ENV FLET_ENV=docker

CMD ["python", "src/gui/map_component.py"]
