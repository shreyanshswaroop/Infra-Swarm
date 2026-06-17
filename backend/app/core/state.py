from typing import Dict, List, Any
from app.models import Incident

INCIDENTS: Dict[str, Incident] = {}
LEARNED_OUTCOMES: List[dict] = []
CURRENT_SIGNALS: List[dict] = []

RUNBOOKS = [
    {
        "id": "rb-memory-leak-rollback",
        "title": "Memory leak after deployment",
        "symptoms": ["memory_growth", "pod_restart", "timeout_errors", "latency_spike"],
        "root_causes": ["memory leak", "bad deployment", "cache growth"],
        "action_type": "ROLLBACK_DEPLOYMENT",
        "target_template": "{service}",
        "command_template": "kubectl rollout undo deployment/{service}",
        "risk": "medium",
        "requires_approval": True,
        "validation": ["memory usage stabilizes", "5xx rate decreases", "p95 latency returns to baseline"],
    },
    {
        "id": "rb-cpu-spike-scale",
        "title": "CPU spike on stateless service",
        "symptoms": ["cpu_spike", "latency_spike"],
        "root_causes": ["traffic surge", "high cpu"],
        "action_type": "SCALE_SERVICE",
        "target_template": "{service}",
        "command_template": "kubectl scale deployment/{service} --replicas=4",
        "risk": "low",
        "requires_approval": False,
        "validation": ["cpu normalizes", "latency decreases"],
    },
    {
        "id": "rb-restart-single-pod",
        "title": "Restart unhealthy non-critical pod",
        "symptoms": ["health_check_failed", "pod_crashloop"],
        "root_causes": ["stuck process", "crash loop"],
        "action_type": "RESTART_POD",
        "target_template": "{service}",
        "command_template": "kubectl rollout restart deployment/{service}",
        "risk": "low",
        "requires_approval": False,
        "validation": ["health check passes", "pod ready state restored"],
    },
]
