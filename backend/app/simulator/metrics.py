from datetime import datetime


def get_service_metrics():
    return [
        {
            "service": "payment-service",
            "cpu": 42,
            "memory": 91,
            "latency_ms": 2800,
            "error_rate": 8.5,
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
        },
        {
            "service": "checkout-service",
            "cpu": 65,
            "memory": 72,
            "latency_ms": 2100,
            "error_rate": 6.2,
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
        },
        {
            "service": "inventory-service",
            "cpu": 94,
            "memory": 55,
            "latency_ms": 900,
            "error_rate": 2.1,
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
        },
        {
            "service": "notification-service",
            "cpu": 28,
            "memory": 40,
            "latency_ms": 180,
            "error_rate": 0.2,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
        },
    ]