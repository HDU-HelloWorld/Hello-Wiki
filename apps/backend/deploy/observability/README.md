# Hello Wiki Observability Stack

This directory contains the local observability stack for the backend.

## Services

- Phoenix: OpenTelemetry trace viewer for LLM and application spans.
- Loki: log aggregation backend.
- Promtail: log shipper that reads backend log files.
- Grafana: dashboard UI with Loki as the default datasource.

## Start

```bash
cd deploy/observability
docker compose up -d
```

If you are using `podman-compose`, use:

```bash
cd deploy/observability
podman-compose up -d
```

Note: on some macOS setups, host proxy variables may be injected into containers and break in-network DNS (for example Grafana -> Loki showing `Connection Closed` / `DNS Failed`). The compose file already clears proxy variables for observability services.

## Backend Environment

The backend writes logs to a file so Promtail can scrape them.

```bash
export LOG_TO_FILE=true
export LOG_FILE_PATH=./data/logs/backend.log
export OBSERVABILITY_ENABLED=true
export OTEL_ENABLED=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:6006/v1/traces
```

## Entry Points

- Phoenix: http://localhost:6006
- Grafana: http://localhost:3000
- Loki: http://localhost:3100

## Grafana Dashboard

The dashboard is provisioned automatically as "Hello Wiki Observability".
It shows backend logs and simple field-presence checks for trace and workspace labels.
