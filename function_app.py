import json
import logging
import os
import uuid
from datetime import datetime, timezone

import azure.functions as func


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

MAX_REQUEST_BYTES = int(os.getenv("MAX_REQUEST_BYTES", "49152"))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def json_response(payload: dict, status_code: int) -> func.HttpResponse:
    return func.HttpResponse(
        body=json.dumps(payload, ensure_ascii=False),
        status_code=status_code,
        mimetype="application/json",
        charset="utf-8",
    )


@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    request_id = req.headers.get("x-request-id") or str(uuid.uuid4())
    logging.info("Health check succeeded. request_id=%s", request_id)

    return json_response(
        {
            "status": "ok",
            "service": "azure-function-sample",
            "timestampUtc": utc_now_iso(),
            "requestId": request_id,
        },
        200,
    )


@app.route(route="results", methods=["POST"])
@app.queue_output(
    arg_name="queue_message",
    queue_name="%RESULT_QUEUE_NAME%",
    connection="AzureWebJobsStorage",
)
def submit_result(
    req: func.HttpRequest,
    queue_message: func.Out[str],
) -> func.HttpResponse:
    request_id = req.headers.get("x-request-id") or str(uuid.uuid4())

    raw_body = req.get_body()
    if len(raw_body) > MAX_REQUEST_BYTES:
        return json_response(
            {
                "status": "rejected",
                "error": "Request body is too large.",
                "requestId": request_id,
            },
            413,
        )

    try:
        payload = req.get_json()
    except ValueError:
        return json_response(
            {
                "status": "rejected",
                "error": "Request body must be valid JSON.",
                "requestId": request_id,
            },
            400,
        )

    if not isinstance(payload, dict):
        return json_response(
            {
                "status": "rejected",
                "error": "JSON root must be an object.",
                "requestId": request_id,
            },
            400,
        )

    source = payload.get("source")
    if not isinstance(source, str) or not source.strip():
        return json_response(
            {
                "status": "rejected",
                "error": "The 'source' field is required.",
                "requestId": request_id,
            },
            400,
        )

    envelope = {
        "schemaVersion": "1.0",
        "requestId": request_id,
        "receivedAtUtc": utc_now_iso(),
        "source": source.strip(),
        "payload": payload,
    }

    queue_message.set(json.dumps(envelope, ensure_ascii=False))
    logging.info(
        "Result accepted. request_id=%s source=%s",
        request_id,
        source.strip(),
    )

    return json_response(
        {
            "status": "accepted",
            "requestId": request_id,
        },
        202,
    )
