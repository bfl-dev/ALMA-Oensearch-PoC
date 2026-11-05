ARG PYTHON_IMAGE
FROM ${PYTHON_IMAGE}
ARG SOURCE_REVISION=unrecorded
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/app/src SOURCE_REVISION=${SOURCE_REVISION}
WORKDIR /app
COPY requirements.lock /app/requirements.lock
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.lock
COPY src /app/src
COPY docs/contracts /app/docs/contracts
COPY deployment /app/deployment
COPY scripts /app/scripts
COPY tests /app/tests
RUN groupadd --gid 10001 poc && useradd --uid 10001 --gid 10001 --create-home poc && mkdir -p /data/corpus /data/adapter /data/worker /data/artifacts && chown -R poc:poc /data
USER poc
ENTRYPOINT ["python", "-m", "alma_poc"]
