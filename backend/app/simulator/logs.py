from datetime import datetime


def get_service_logs():
    now = datetime.utcnow().isoformat()

    return [
        {
            "service": "payment-service",
            "logs": [
                {
                    "timestamp": now,
                    "level": "INFO",
                    "message": "Payment request received for checkout session.",
                },
                {
                    "timestamp": now,
                    "level": "WARN",
                    "message": "Object cache size increased beyond expected threshold.",
                },
                {
                    "timestamp": now,
                    "level": "ERROR",
                    "message": "Memory pressure detected while processing payment queue.",
                },
                {
                    "timestamp": now,
                    "level": "WARN",
                    "message": "Checkout requests are experiencing increased latency.",
                },
            ],
        },
        {
            "service": "inventory-service",
            "logs": [
                {
                    "timestamp": now,
                    "level": "INFO",
                    "message": "Inventory sync job started.",
                },
                {
                    "timestamp": now,
                    "level": "WARN",
                    "message": "Worker queue saturation detected.",
                },
                {
                    "timestamp": now,
                    "level": "ERROR",
                    "message": "CPU usage exceeded safe operating threshold.",
                },
                {
                    "timestamp": now,
                    "level": "INFO",
                    "message": "No recent deployment change detected for inventory-service.",
                },
            ],
        },
        {
            "service": "checkout-service",
            "logs": [
                {
                    "timestamp": now,
                    "level": "INFO",
                    "message": "Checkout API healthy.",
                },
                {
                    "timestamp": now,
                    "level": "WARN",
                    "message": "Downstream payment-service latency increased.",
                },
                {
                    "timestamp": now,
                    "level": "INFO",
                    "message": "Retry policy activated for payment requests.",
                },
            ],
        },
        {
            "service": "auth-service",
            "logs": [
                {
                    "timestamp": now,
                    "level": "INFO",
                    "message": "Token validation completed successfully.",
                },
                {
                    "timestamp": now,
                    "level": "INFO",
                    "message": "Auth service operating within normal limits.",
                },
            ],
        },
    ]


def get_logs_for_service(service_name: str):
    services = get_service_logs()

    for service in services:
        if service["service"] == service_name:
            return service["logs"]

    return []