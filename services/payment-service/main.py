from fastapi import FastAPI
from datetime import datetime
import random

app = FastAPI(title="payment-service")

service_state = {
    "name": "payment-service",
    "mode": "healthy",
    "request_count": 0,
    "error_count": 0,
    "memory_usage": 42,
    "cpu_usage": 35,
    "latency_ms": 120,
}


@app.get("/")
def root():
    return {
        "service": service_state["name"],
        "status": "running",
    }


@app.get("/health")
def health():
    if service_state["mode"] == "down":
        return {
            "service": service_state["name"],
            "status": "unhealthy",
        }

    return {
        "service": service_state["name"],
        "status": "healthy" if service_state["mode"] == "healthy" else "degraded",
        "mode": service_state["mode"],
    }


@app.get("/metrics")
def metrics():
    service_state["request_count"] += 1

    if service_state["mode"] == "healthy":
        service_state["cpu_usage"] = random.randint(25, 45)
        service_state["memory_usage"] = random.randint(35, 55)
        service_state["latency_ms"] = random.randint(80, 180)

    elif service_state["mode"] == "memory_leak":
        service_state["memory_usage"] = min(service_state["memory_usage"] + random.randint(4, 9), 98)
        service_state["cpu_usage"] = random.randint(45, 65)
        service_state["latency_ms"] = random.randint(800, 2500)
        service_state["error_count"] += random.randint(1, 4)

    elif service_state["mode"] == "cpu_spike":
        service_state["cpu_usage"] = random.randint(90, 99)
        service_state["memory_usage"] = random.randint(45, 60)
        service_state["latency_ms"] = random.randint(600, 1600)
        service_state["error_count"] += random.randint(0, 2)

    error_rate = min(
        round(
            (service_state["error_count"] / max(service_state["request_count"], 1)) * 100,
            2,
        ),
        100,
    )

    return {
        "service": service_state["name"],
        "cpu": service_state["cpu_usage"],
        "memory": service_state["memory_usage"],
        "latency_ms": service_state["latency_ms"],
        "error_rate": error_rate,
        "request_count": service_state["request_count"],
        "mode": service_state["mode"],
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/logs")
def logs():
    if service_state["mode"] == "memory_leak":
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "WARN",
                "message": "Object cache size increasing continuously.",
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "ERROR",
                "message": "Payment request timeout caused by memory pressure.",
            },
        ]

    if service_state["mode"] == "cpu_spike":
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "WARN",
                "message": "CPU saturation detected during payment processing.",
            }
        ]

    return [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "message": "Payment service operating normally.",
        }
    ]


@app.post("/simulate/memory-leak")
def simulate_memory_leak():
    service_state["mode"] = "memory_leak"
    return {
        "message": "payment-service memory leak simulation started",
        "mode": service_state["mode"],
    }


@app.post("/simulate/cpu-spike")
def simulate_cpu_spike():
    service_state["mode"] = "cpu_spike"
    return {
        "message": "payment-service CPU spike simulation started",
        "mode": service_state["mode"],
    }


@app.post("/recover")
def recover():
    service_state["mode"] = "healthy"
    service_state["error_count"] = 0
    service_state["request_count"] = 0
    service_state["memory_usage"] = 42
    service_state["cpu_usage"] = 35
    service_state["latency_ms"] = 120

    return {
        "message": "payment-service recovered",
        "mode": service_state["mode"],
    }