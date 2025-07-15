# AikidoSecureSync

Port's Aikido integration allows you to model Aikido security resources in your software catalog and ingest data into them.

⚠️ **Aikido Cloud only**
This integration supports [Aikido Cloud](https://app.aikido.dev) only.

---

## Overview

This integration allows you to:

* Watch for security issues and repository changes in Aikido in real-time and apply them to your Port software catalog.
* Define automations and actions based on synced vulnerabilities or repositories.
* Model your Aikido entities such as `code_repository` and `vulnerability` as native Port resources.

---

## Supported Resources

The following Aikido resources can be ingested into Port:

| Aikido Resource   | Port Kind         |
| ----------------- | ----------------- |
| Code Repositories | `code_repository` |
| Vulnerabilities   | `vulnerability`   |

Each field available from the Aikido API can be referenced in the integration's mapping configuration.

---

## Setup

### Prerequisites

* [Port account](https://app.port.io)
* Aikido Cloud account with access to:

  * OAuth2 Client ID & Client Secret
  * HMAC Signing Secret
* Ngrok or any reverse proxy if developing locally
* Python 3.10+ with `venv` (recommended)
* [Ocean CLI](https://ocean.getport.io/install-ocean/) installed

---

### Environment Variables

You’ll need to configure the following environment variables:

```env
OCEAN__PORT__CLIENT_ID=<your_port_client_id>
OCEAN__PORT__CLIENT_SECRET=<your_port_client_secret>
OCEAN__PORT__HMAC_SIGNING_SECRET=<your_aikido_hmac_secret>
OCEAN__BASE_URL=https://<your-ngrok-subdomain>.ngrok-free.app
```

---

### Configuration

In `integration.yaml`:

```yaml
type: aikidosecuresync
title: Aikido Security Sync
description: |
  Fetches code repositories and vulnerability issues from Aikido
  and syncs them into Port for unified visibility and tracking.
icon: GitBranch

features:
  - type: exporter
    section: Security
    resources:
      - kind: code_repository
      - kind: vulnerability

configurations:
  - name: aikidoHost
    required: false
    type: url
    default: https://app.aikido.dev
    description: "Base URL of your Aikido API"
  - name: clientId
    required: true
    type: string
    description: "OAuth2 Client ID"
  - name: clientSecret
    required: true
    type: string
    sensitive: true
    description: "OAuth2 Client Secret"
  - name: hmacSigningSecret
    required: true
    type: string
    sensitive: true
    description: "HMAC Client Secret"

eventListener:
  type: WEBHOOKS_ONLY
  appHost: "${OCEAN__BASE_URL}"
```

---

### Running Locally

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -e .
   ```

3. Start the integration:

   ```bash
   ocean sail
   ```

You should see logs indicating successful startup and webhook handling.

---

## Webhook Support

This integration supports the following event types:

| Event Type             | Description                        |
| ---------------------- | ---------------------------------- |
| `issue.open.created`   | A new issue was opened             |
| `issue.snoozed`        | An issue was snoozed               |
| `issue.ignored.manual` | An issue was manually ignored      |
| `issue.closed`         | An issue was resolved or dismissed |

Webhook requests must be sent to:

```
POST https://<your-ngrok-subdomain>.ngrok-free.app/integration/webhook
```

---

### Filtering Events

In `AikidoIntegration.should_process_event`, only relevant events are processed:

```python
async def should_process_event(self, event: WebhookEvent) -> bool:
    return event.payload.get("event_type", "").startswith("issue.")
```

---

## Advanced Configuration

You can override or extend the default mapping logic using Ocean’s mapping config file to:

* Normalize severity scores
* Link code repositories to vulnerabilities
* Filter based on custom attributes or statuses

To learn more, see: [Port Mapping Guide](https://docs.port.io/build-your-software-catalog/sync-data-to-catalog/#mapping)

---

## Development

To develop or debug this integration:

1. Clone the repo and install in editable mode:

   ```bash
   pip install -e .
   ```

2. Set required environment variables.

3. Use tools like [Postman](https://www.postman.com/) or `curl` to simulate Aikido webhook events.

---

## Troubleshooting

* `ValidationError: hmac_signing_secret missing`: ensure your `.env` or shell environment includes `OCEAN__PORT__HMAC_SIGNING_SECRET`.
* `Webhook not received`: make sure your ngrok tunnel is active and `OCEAN__BASE_URL` is set to its HTTPS endpoint.
* `Print statements not appearing`: confirm your code path is not skipping `should_process_event`.

---

## Related Links

* [Ocean SDK Docs](https://ocean.getport.io)
* [Aikido API Reference](https://docs.aikido.dev)
* [Port Integration Docs](https://docs.port.io)
