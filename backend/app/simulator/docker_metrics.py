import requests

DOCKER_SERVICES = [
    {
        "service": "payment-service",
        "metrics_url": "http://localhost:9001/metrics",
        "logs_url": "http://localhost:9001/logs",
    }
]


def get_docker_service_metrics():
    metrics = []

    for service in DOCKER_SERVICES:
        try:
            response = requests.get(service["metrics_url"], timeout=2)
            response.raise_for_status()

            data = response.json()

            status = "HEALTHY"

            if data["memory"] >= 85 or data["cpu"] >= 90 or data["error_rate"] >= 5:
                status = "DEGRADED"

            metrics.append(
                {
                    "service": data["service"],
                    "cpu": data["cpu"],
                    "memory": data["memory"],
                    "latency_ms": data["latency_ms"],
                    "error_rate": data["error_rate"],
                    "status": status,
                    "source": "docker",
                    "mode": data.get("mode", "unknown"),
                }
            )

        except Exception:
            metrics.append(
                {
                    "service": service["service"],
                    "cpu": 0,
                    "memory": 0,
                    "latency_ms": 0,
                    "error_rate": 100,
                    "status": "DOWN",
                    "source": "docker",
                    "mode": "unreachable",
                }
            )

    return metrics


def get_docker_logs_for_service(service_name: str):
    for service in DOCKER_SERVICES:
        if service["service"] != service_name:
            continue

        try:
            response = requests.get(service["logs_url"], timeout=2)
            response.raise_for_status()
            return response.json()

        except Exception:
            return [
                {
                    "level": "ERROR",
                    "message": f"{service_name} is unreachable.",
                }
            ]

    return []

def trigger_docker_memory_leak(service_name: str):
    for service in DOCKER_SERVICES:
        if service["service"] != service_name:
            continue

        response = requests.post(
            service["metrics_url"].replace("/metrics", "/simulate/memory-leak"),
            timeout=2,
        )
        response.raise_for_status()
        return response.json()

    return {"error": f"{service_name} not found"}


def trigger_docker_recovery(service_name: str):
    for service in DOCKER_SERVICES:
        if service["service"] != service_name:
            continue

        response = requests.post(
            service["metrics_url"].replace("/metrics", "/recover"),
            timeout=2,
        )
        response.raise_for_status()
        return response.json()

    return {"error": f"{service_name} not found"}