from datetime import datetime

from app.simulator.docker_metrics import get_docker_service_metrics


def get_service_metrics():
    docker_metrics = get_docker_service_metrics()

    docker_services = {
        metric["service"]: metric
        for metric in docker_metrics
    }

    services = []

    if "payment-service" in docker_services:
        services.append(
            {
                **docker_services["payment-service"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    else:
        services.append(
            {
                "service": "payment-service",
                "cpu": 0,
                "memory": 0,
                "latency_ms": 0,
                "error_rate": 100,
                "status": "DOWN",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    services.extend(
        [
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
    )

    return services