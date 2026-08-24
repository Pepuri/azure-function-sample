# Azure Function Sample

A Python 3.12 sample project for validating an end-to-end development workflow using iPad, GitHub, Codex, GitHub Actions, and Azure Functions.

## Current Features

- `GET /api/health`: Checks the Function App health status.
- `POST /api/results`: Validates a JSON request and writes it to an Azure Storage Queue.
- Uses UTF-8 for all JSON responses and queue messages.
- Generates a `requestId` for Application Insights correlation.
- Limits the request body to 48 KiB by default.
- Protects HTTP endpoints with Function Key authentication.

## Request Example

```json
{
  "source": "intune",
  "deviceName": "SAMPLE-PC-01",
  "result": "Succeeded",
  "message": "This is a sample result."
}
```

When the request is accepted, the function returns HTTP `202 Accepted` with a `requestId`. It writes a message to the `intune-results` queue using the following structure:

```json
{
  "schemaVersion": "1.0",
  "requestId": "...",
  "receivedAtUtc": "2026-08-24T00:00:00Z",
  "source": "intune",
  "payload": {}
}
```

## Local Configuration

Copy `local.settings.sample.json` to `local.settings.json`, then update the values for your development environment. The actual `local.settings.json` file is excluded from Git.

Required application settings:

| Name | Purpose |
|---|---|
| `AzureWebJobsStorage` | Connects the Functions host and Storage Queue |
| `RESULT_QUEUE_NAME` | Specifies the destination queue name |
| `MAX_REQUEST_BYTES` | Sets the maximum accepted request size |

## Security Principles

- Never commit connection strings, Function Keys, certificates, or passwords.
- Store production secrets in Azure App Settings or Azure Key Vault.
- Exclude `local.settings.json` through both `.gitignore` and `.funcignore`.
- Never commit actual device information or customer logs as test data.
- Use OpenID Connect (OIDC), rather than a publish profile, for GitHub Actions authentication to Azure.

## Next Steps

1. Create a Python 3.12 Function App and Storage Account in Azure.
2. Configure `RESULT_QUEUE_NAME=intune-results`.
3. Connect GitHub Actions deployment using OIDC.
4. Call the deployed `/api/health` endpoint from an iPad.
5. Submit a request to `/api/results`, then verify the Storage Queue and Application Insights logs.

## Extension Ideas

This sample can be extended to collect Intune device-script results, automate Microsoft Sentinel incidents, or process Microsoft Purview evidence.
