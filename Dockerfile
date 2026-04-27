# ── Stage 1: compile wheels ───────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# gcc and python3-dev are only needed to compile pymavlink's C extensions.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl \
    && rm -rf /wheels

COPY src/ ./src/

EXPOSE 8080

ENV DATA_FILE=/app/data/log_file_test_01.bin
ENV FLET_ENV=docker

CMD ["python", "src/gui/map_component.py"]
