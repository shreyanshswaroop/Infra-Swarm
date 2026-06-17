from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.simulator.metrics import get_service_metrics

from app.core.state import LEARNED_OUTCOMES
from app.database import (
    init_db,
    save_incident,
    list_incidents as db_list_incidents,
    get_incident as db_get_incident,
    find_existing_active_incident,
    find_recent_incident,
)

app = FastAPI(title="Infra Swarm")

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Infra Swarm API", "status": "running"}


@app.get("/incidents")
def get_all_incidents():
    return db_list_incidents()


@app.get("/incidents/{incident_id}")
def get_single_incident(incident_id: str):
    incident = db_get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@app.post("/incidents/{incident_id}/approve")
def approve_incident(incident_id: str):
    incident = db_get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident["status"] != "AWAITING_APPROVAL":
        return incident

    incident["status"] = "RESOLVED"
    incident["updated_at"] = datetime.utcnow().isoformat()

    incident["timeline"].append(
        {
            "agent": "Human",
            "message": "Approved remediation action.",
        }
    )

    incident["timeline"].append(
        {
            "agent": "Remediator",
            "message": "Executed rollback deployment.",
        }
    )

    incident["timeline"].append(
        {
            "agent": "Observer",
            "message": "Validated recovery after remediation.",
        }
    )

    incident["timeline"].append(
        {
            "agent": "Learner",
            "message": "Stored successful memory leak remediation outcome.",
        }
    )

    save_incident(incident)
    return incident


@app.post("/simulate/memory-leak")
def simulate_memory_leak():
    now = datetime.utcnow().isoformat()

    incident = {
        "id": f"INC-{datetime.utcnow().strftime('%H%M%S')}",
        "title": "payment-service memory leak detected",
       "service": "payment-service",
        "affected_services": ["payment-service", "checkout-service"],
        "severity": "SEV-2",
        "status": "AWAITING_APPROVAL",
        "incident_type": "MEMORY_LEAK",
                "signals": [
            "memory_growth",
            "latency_spike",
            "timeout_errors",
        ],
        "diagnosis": {
            "agent": "Diagnoser",
            "root_cause": "Memory leak likely introduced after recent payment-service deployment.",
            "confidence": 0.88,
            "evidence": [
                "Memory usage increased continuously",
                "Issue started after latest deployment",
                "Checkout timeout errors increased",
                "Payment-service logs show object cache growth",
            ],
        },
        "remediation": {
            "agent": "Remediator",
            "action": "ROLLBACK_DEPLOYMENT",
            "command": "kubectl rollout undo deployment/payment-service",
            "reason": "Rollback should remove the suspected faulty deployment.",
        },
        "safety": {
            "agent": "Safety",
            "risk": "medium",
            "approval_required": True,
            "decision": "Human approval required because payment-service is production-critical.",
        },
        "timeline": [
            {
                "agent": "Observer",
                "message": "Detected continuous memory growth on payment-service.",
            },
            {
                "agent": "Diagnoser",
                "message": "Linked memory growth to recent deployment.",
            },
            {
                "agent": "Remediator",
                "message": "Recommended rollback deployment.",
            },
            {
                "agent": "Safety",
                "message": "Requested human approval before rollback.",
            },
        ],
        "created_at": now,
        "updated_at": now,
    }

    save_incident(incident)
    return db_get_incident(incident["id"])
    


@app.post("/simulate/cpu-spike")
def simulate_cpu_spike():
    now = datetime.utcnow().isoformat()

    incident = {
        "id": f"INC-{datetime.utcnow().strftime('%H%M%S')}",
        "title": "inventory-service CPU spike detected",
        "service": "inventory-service",
        "affected_services": ["inventory-service"],
        "severity": "SEV-3",
        "status": "RESOLVED",
        "incident_type": "CPU_SPIKE",
        "signals": [
        "cpu_spike",
        "latency_spike",

    ],
        "diagnosis": {
            "agent": "Diagnoser",
            "root_cause": "Sudden CPU saturation on inventory-service caused by traffic burst.",
            "confidence": 0.82,
            "evidence": [
                "CPU usage crossed 90%",
                "Request volume increased suddenly",
                "No deployment change detected",
            ],
        },
        "remediation": {
            "agent": "Remediator",
            "action": "SCALE_SERVICE",
            "command": "kubectl scale deployment/inventory-service --replicas=4",
            "reason": "Scaling replicas should reduce CPU pressure.",
        },
        "safety": {
            "agent": "Safety",
            "risk": "low",
            "approval_required": False,
            "decision": "Auto-approved because scaling is within safe policy limits.",
        },
        "timeline": [
            {
                "agent": "Observer",
                "message": "Detected CPU spike on inventory-service.",
            },
            {
                "agent": "Diagnoser",
                "message": "Identified traffic burst as likely root cause.",
            },
            {
                "agent": "Remediator",
                "message": "Selected scale service remediation.",
            },
            {
                "agent": "Safety",
                "message": "Approved low-risk scaling action.",
            },
            {
                "agent": "Orchestrator",
                "message": "Incident resolved after simulated scaling.",
            },
            {
                "agent": "Learner",
                "message": "Stored successful CPU spike remediation outcome.",
            },
        ],
        "created_at": now,
        "updated_at": now,
    }

    save_incident(incident)
    return db_get_incident(incident["id"])  


@app.get("/learned-outcomes")
def learned_outcomes():
    return LEARNED_OUTCOMES

@app.get("/metrics")
def get_metrics():
    return get_service_metrics()

@app.post("/observer/scan")
def observer_scan():
    metrics = get_service_metrics()
    created_incidents = []
    skipped_incidents = []

    for metric in metrics:
        service = metric["service"]
        now = datetime.utcnow().isoformat()

        if metric["memory"] >= 85:
            existing = find_existing_active_incident(service, "MEMORY_LEAK")

            if existing:
                skipped_incidents.append(
                    {
                        "service": service,
                        "incident_type": "MEMORY_LEAK",
                        "reason": "Active memory incident already exists",
                        "existing_incident_id": existing["id"],
                    }
                )
                continue

            incident = {
                "id": f"INC-MEM-{datetime.utcnow().strftime('%H%M%S')}",
                "title": f"{service} memory anomaly detected",
                "service": service,
                "affected_services": [service],
                "severity": "SEV-2",
                "status": "AWAITING_APPROVAL",
                "incident_type": "MEMORY_LEAK",
                "signals": [
                    "memory_growth",
                    "latency_spike",
                    "error_rate_increase",
                ],
                "diagnosis": {
                    "agent": "Diagnoser",
                    "root_cause": f"Memory pressure detected on {service}. Possible memory leak or inefficient cache growth.",
                    "confidence": 0.84,
                    "evidence": [
                        f"Memory usage reached {metric['memory']}%",
                        f"Latency is {metric['latency_ms']}ms",
                        f"Error rate is {metric['error_rate']}%",
                    ],
                },
                "remediation": {
                    "agent": "Remediator",
                    "action": "ROLLBACK_OR_RESTART",
                    "command": f"kubectl rollout restart deployment/{service}",
                    "reason": "Restarting or rolling back can clear memory pressure and restore service stability.",
                },
                "safety": {
                    "agent": "Safety",
                    "risk": "medium",
                    "approval_required": True,
                    "decision": "Human approval required because memory remediation may impact active traffic.",
                },
                "timeline": [
                    {
                        "agent": "Observer",
                        "message": f"Detected memory anomaly on {service}.",
                    },
                    {
                        "agent": "Diagnoser",
                        "message": f"Analyzed metrics and identified memory pressure on {service}.",
                    },
                    {
                        "agent": "Remediator",
                        "message": "Prepared restart or rollback remediation plan.",
                    },
                    {
                        "agent": "Safety",
                        "message": "Requested human approval before executing remediation.",
                    },
                ],
                "created_at": now,
                "updated_at": now,
            }

            save_incident(incident)
            created_incidents.append(db_get_incident(incident["id"]))

        elif metric["cpu"] >= 90:
            existing = find_existing_active_incident(service, "CPU_SPIKE")

            if existing:
                skipped_incidents.append(
                    {
                        "service": service,
                        "incident_type": "CPU_SPIKE",
                        "reason": "Active CPU incident already exists",
                        "existing_incident_id": existing["id"],
                    }
                )
                continue

            recent = find_recent_incident(service, "CPU_SPIKE", minutes=5)

            if recent:
                skipped_incidents.append(
                    {
                        "service": service,
                        "incident_type": "CPU_SPIKE",
                        "reason": "CPU incident already created within cooldown window",
                        "existing_incident_id": recent["id"],
                    }
                )
                continue

            incident = {
                "id": f"INC-CPU-{datetime.utcnow().strftime('%H%M%S')}",
                "title": f"{service} CPU spike detected",
                "service": service,
                "affected_services": [service],
                "severity": "SEV-3",
                "status": "RESOLVED",
                "incident_type": "CPU_SPIKE",
                "signals": [
                    "cpu_spike",
                    "latency_spike",
                ],
                "diagnosis": {
                    "agent": "Diagnoser",
                    "root_cause": f"High CPU saturation detected on {service}.",
                    "confidence": 0.80,
                    "evidence": [
                        f"CPU usage reached {metric['cpu']}%",
                        f"Latency is {metric['latency_ms']}ms",
                        "Service is stateless and safe to scale",
                    ],
                },
                "remediation": {
                    "agent": "Remediator",
                    "action": "SCALE_SERVICE",
                    "command": f"kubectl scale deployment/{service} --replicas=4",
                    "reason": "Scaling replicas should reduce CPU pressure.",
                },
                "safety": {
                    "agent": "Safety",
                    "risk": "low",
                    "approval_required": False,
                    "decision": "Auto-approved because scaling a stateless service is low risk.",
                },
                "timeline": [
                    {
                        "agent": "Observer",
                        "message": f"Detected CPU spike on {service}.",
                    },
                    {
                        "agent": "Diagnoser",
                        "message": f"Confirmed CPU saturation on {service}.",
                    },
                    {
                        "agent": "Remediator",
                        "message": "Selected scale service remediation.",
                    },
                    {
                        "agent": "Safety",
                        "message": "Auto-approved low-risk scaling action.",
                    },
                    {
                        "agent": "Orchestrator",
                        "message": "Incident resolved after simulated scaling.",
                    },
                    {
                        "agent": "Learner",
                        "message": "Stored successful CPU spike remediation outcome.",
                    },
                ],
                "created_at": now,
                "updated_at": now,
            }

            save_incident(incident)
            created_incidents.append(db_get_incident(incident["id"]))

    return {
        "scanned_services": len(metrics),
        "created_incidents": created_incidents,
        "skipped_incidents": skipped_incidents,
    }
    
    metrics = get_service_metrics()
    created_incidents = []

    for metric in metrics:
        service = metric["service"]
        now = datetime.utcnow().isoformat()

        if metric["memory"] >= 85:
            incident = {
                "id": f"INC-MEM-{datetime.utcnow().strftime('%H%M%S')}",
                "title": f"{service} memory anomaly detected",
                "service": service,
                "affected_services": [service],
                "severity": "SEV-2",
                "status": "AWAITING_APPROVAL",
                "incident_type": "MEMORY_LEAK",
                "signals": [
                    "memory_growth",
                    "latency_spike",
                    "error_rate_increase",
                ],
                "diagnosis": {
                    "agent": "Diagnoser",
                    "root_cause": f"Memory pressure detected on {service}. Possible memory leak or inefficient cache growth.",
                    "confidence": 0.84,
                    "evidence": [
                        f"Memory usage reached {metric['memory']}%",
                        f"Latency is {metric['latency_ms']}ms",
                        f"Error rate is {metric['error_rate']}%",
                    ],
                },
                "remediation": {
                    "agent": "Remediator",
                    "action": "ROLLBACK_OR_RESTART",
                    "command": f"kubectl rollout restart deployment/{service}",
                    "reason": "Restarting or rolling back can clear memory pressure and restore service stability.",
                },
                "safety": {
                    "agent": "Safety",
                    "risk": "medium",
                    "approval_required": True,
                    "decision": "Human approval required because memory remediation may impact active traffic.",
                },
                "timeline": [
                    {
                        "agent": "Observer",
                        "message": f"Detected memory anomaly on {service}.",
                    },
                    {
                        "agent": "Diagnoser",
                        "message": f"Analyzed metrics and identified memory pressure on {service}.",
                    },
                    {
                        "agent": "Remediator",
                        "message": "Prepared restart or rollback remediation plan.",
                    },
                    {
                        "agent": "Safety",
                        "message": "Requested human approval before executing remediation.",
                    },
                ],
                "created_at": now,
                "updated_at": now,
            }

            save_incident(incident)
            created_incidents.append(db_get_incident(incident["id"]))

        elif metric["cpu"] >= 90:
            incident = {
                "id": f"INC-CPU-{datetime.utcnow().strftime('%H%M%S')}",
                "title": f"{service} CPU spike detected",
                "service": service,
                "affected_services": [service],
                "severity": "SEV-3",
                "status": "RESOLVED",
                "incident_type": "CPU_SPIKE",
                "signals": [
                    "cpu_spike",
                    "latency_spike",
                ],
                "diagnosis": {
                    "agent": "Diagnoser",
                    "root_cause": f"High CPU saturation detected on {service}.",
                    "confidence": 0.80,
                    "evidence": [
                        f"CPU usage reached {metric['cpu']}%",
                        f"Latency is {metric['latency_ms']}ms",
                        "Service is stateless and safe to scale",
                    ],
                },
                "remediation": {
                    "agent": "Remediator",
                    "action": "SCALE_SERVICE",
                    "command": f"kubectl scale deployment/{service} --replicas=4",
                    "reason": "Scaling replicas should reduce CPU pressure.",
                },
                "safety": {
                    "agent": "Safety",
                    "risk": "low",
                    "approval_required": False,
                    "decision": "Auto-approved because scaling a stateless service is low risk.",
                },
                "timeline": [
                    {
                        "agent": "Observer",
                        "message": f"Detected CPU spike on {service}.",
                    },
                    {
                        "agent": "Diagnoser",
                        "message": f"Confirmed CPU saturation on {service}.",
                    },
                    {
                        "agent": "Remediator",
                        "message": "Selected scale service remediation.",
                    },
                    {
                        "agent": "Safety",
                        "message": "Auto-approved low-risk scaling action.",
                    },
                    {
                        "agent": "Orchestrator",
                        "message": "Incident resolved after simulated scaling.",
                    },
                    {
                        "agent": "Learner",
                        "message": "Stored successful CPU spike remediation outcome.",
                    },
                ],
                "created_at": now,
                "updated_at": now,
            }

            save_incident(incident)
            created_incidents.append(db_get_incident(incident["id"]))

    return {
        "scanned_services": len(metrics),
        "created_incidents": created_incidents,
    }