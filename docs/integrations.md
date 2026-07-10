# Integrations

How the dashboard connects to external supervision/ITSM tools today, and what
"today" actually means: **every integration in this repository is currently
simulated or stubbed** — there is no live Zabbix/Nagios/Centreon/NetXMS/iTop
instance behind this demo. This document is both the integration contract
(what the real thing must satisfy) and a map of exactly what to swap when a
real instance becomes reachable.

## Table of Contents

- [Summary](#summary)
- [Supervision tools → incident ingestion](#supervision-tools--incident-ingestion)
- [The ETL pipeline (simulator)](#the-etl-pipeline-simulator)
- [iTop (ITSM / CMDB)](#itop-itsm--cmdb)
- [Webhook authentication](#webhook-authentication)
- [Swapping a simulator for the real thing](#swapping-a-simulator-for-the-real-thing)

---

## Summary

| System | Protocol (real) | Status in this repo | Config vars |
|---|---|---|---|
| **Zabbix** | JSON-RPC `event.get` | Simulated (`etl/extract/simulators.py`) | `ZABBIX_API_URL`, `ZABBIX_USER`, `ZABBIX_PASSWORD` |
| **Nagios** | `statusjson.cgi` | Simulated | `NAGIOS_API_URL`, `NAGIOS_API_KEY` |
| **NetXMS** | REST API | Simulated | — (no dedicated env vars yet) |
| **Centreon** | Broker webhook / REST | Simulated | `CENTREON_API_URL`, `CENTREON_API_KEY` |
| **iTop** | REST webservice (`core/create`) | Stubbed (`backend/app/services/itop_service.py`) | `ITOP_URL`, `ITOP_USER`, `ITOP_PASS` |
| **Twilio (SMS)** | REST API (`Messages.json`) | **Implemented** (`backend/app/services/notification_service.py`) — disabled until configured | `NOTIFICATIONS_ENABLED`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `NOC_SMS_RECIPIENTS` |
| **SMTP (email)** | SMTP + STARTTLS | **Implemented** (same service) — disabled until configured | `SMTP_HOST/PORT/USER/PASSWORD/FROM`, `SMTP_USE_TLS`, `NOC_EMAIL_RECIPIENTS` |

The supervision-tool `*_API_URL`/`*_API_KEY`/`*_USER`/`*_PASSWORD` variables
are already wired into `.env`/`.env.example` and `docker-compose.yml`'s
`backend` environment block, but nothing in the codebase reads them yet —
they're placeholders for the real integration work described below. The
**notification** variables, by contrast, are live: real HTTP/SMTP calls exist
and fire on critical-incident ingest as soon as `NOTIFICATIONS_ENABLED=true`
(see [architecture.md#notifications-smsemail](architecture.md#notifications-smsemail)).

## Supervision tools → incident ingestion

In production, each supervision tool would push (webhook) or be polled for
new alerts, which get normalized and POSTed to
`POST /api/incidents/ingest` (see [api-reference.md](api-reference.md#post-apiincidentsingest)).
`dim_node.source_tool` records which tool owns each node, and
`fact_incident.source_tool` denormalizes it onto every incident.

Per the cahier des charges:
- **§6.1 Zabbix** — poll `event.get` via JSON-RPC at `ZABBIX_API_URL`.
- **§6.2 Nagios** — poll `GET .../statusjson.cgi?query=hostlist`.
- **§6.3 Centreon** — receive broker webhook payloads.
- **NetXMS** — its own REST event query (no section reference in code comments).

None of these calls exist yet in `backend/` or `etl/` — see
[Swapping a simulator for the real thing](#swapping-a-simulator-for-the-real-thing).

## The ETL pipeline (simulator)

`etl/` is a Celery-based service (see [architecture.md](architecture.md#components))
that stands in for the four supervision tools until they're reachable:

1. **`etl-beat`** enqueues `etl.collect_incident` every `ETL_COLLECT_INTERVAL_S`
   seconds (default 30).
2. **`etl-worker`** runs the task:
   - `pipelines/collector.py::load_active_nodes` — reads every `is_active =
     TRUE` node directly from Postgres (bypassing the API — this is the one
     place the ETL talks to the DB instead of the backend).
   - `extract/simulators.py::simulate_event` — picks the per-tool simulator
     (`poll_zabbix`/`poll_nagios`/`poll_netxms`/`poll_centreon`) matching the
     node's `source_tool`, and fabricates one plausible event: a random
     severity (weighted toward medium/high) and a cause drawn from a
     per-tool table (e.g. Zabbix skews toward power/énergie causes, Centreon
     toward link/VSAT causes).
   - `transform/normalize.py::to_ingest_payload` — reshapes the raw event into
     the ingest payload, and decides `itop_auto_ticket=True` for
     `critical`/`high` severity (the only place that decision is made).
   - `load/api_client.py::NocApiClient.ingest_incident` — POSTs to
     `$NOC_API_URL/api/incidents/ingest` with the static bearer key, 5s
     timeout, and returns `None` (rather than raising) on any request
     exception.
3. On a `None` result, the Celery task retries up to 3 times with a 10s delay
   (`etl/pipelines/tasks.py`); Celery drops a tick entirely rather than piling
   up backlog if the API is down (`task_time_limit=60`, `expires` on the beat
   schedule).

This whole pipeline exists purely to make the dashboard feel alive without
requiring real infrastructure — it approximates the "always-on webhook flow"
from cahier des charges §2.2/§7.1.

## iTop (ITSM / CMDB)

`backend/app/services/itop_service.py` is a stub:

```python
def create_ticket(incident_id: int, node_code: str, description: str | None) -> str:
    year = datetime.now(timezone.utc).year
    return f"TKT-{year}-{incident_id:05d}"
```

It deterministically mints a reference in exactly the shape the real iTop
REST webservice (`core/create` on class `Incident`) would return, so the rest
of the app (ingestion response, dashboard display) already exercises the real
data shape — only the network call is missing. It's invoked from
`incident_service.ingest_incident` whenever a payload sets
`itop_auto_ticket: true` (which the ETL simulator sets for `critical`/`high`
severity events; real supervision webhooks would set it the same way, or the
backend could decide based on severity server-side instead).

`dim_node.itop_ci_id` exists in the schema for linking a node to its iTop CMDB
CI record, but nothing currently populates or reads it outside seed data.

## Webhook authentication

All external systems calling into this API (real or simulated) authenticate
with a single static bearer key, not per-tool credentials:

```
Authorization: Bearer $NOC_API_KEY
```

checked by `verify_api_key` (`backend/app/core/security.py`) against
`POST /api/incidents/ingest` only. This matches cahier des charges §10.1
("clé API statique pour les webhooks"). The `ZABBIX_USER`/`ZABBIX_PASSWORD`,
`CENTREON_API_KEY`, `NAGIOS_API_KEY` etc. env vars are for the **outbound**
direction — i.e. what this backend would use to *poll* those tools' own APIs
(Zabbix/Nagios) — separate from the shared inbound `NOC_API_KEY` tools would
use to push webhooks to `/ingest` (Centreon-style push).

## Swapping a simulator for the real thing

Each simulator function carries a docstring naming its real equivalent — start
there:

| File | Function | Real equivalent |
|---|---|---|
| `etl/extract/simulators.py` | `poll_zabbix` | `POST` JSON-RPC `event.get` on `ZABBIX_API_URL` |
| `etl/extract/simulators.py` | `poll_nagios` | `GET {NAGIOS_API_URL}/cgi-bin/statusjson.cgi?query=hostlist` |
| `etl/extract/simulators.py` | `poll_netxms` | NetXMS REST event query |
| `etl/extract/simulators.py` | `poll_centreon` | Receive Centreon broker webhook payload (may invert the flow: Centreon pushes to a new endpoint rather than being polled) |
| `backend/app/services/itop_service.py` | `create_ticket` | `requests.post(ITOP_URL, ...)` calling iTop's `core/create` REST operation with `ITOP_USER`/`ITOP_PASS` |

For the three poll-based tools (Zabbix, Nagios, NetXMS), the natural place to
add real calls is inside the corresponding `poll_*` function in
`etl/extract/simulators.py` — keep the return shape (`node_code, source_tool,
external_id, severity, detected_at, cause_category, cause_label,
description`) so `transform/normalize.py` doesn't need to change. For
Centreon's webhook-push model, add a new inbound endpoint (or reuse
`/api/incidents/ingest` directly from Centreon, which already accepts
`source_tool: "centreon"`) instead of polling it from the ETL worker.
