from datetime import datetime
from app.core.state import LEARNED_OUTCOMES
from app.models import AgentEvent, Incident

class LearnerAgent:
    name = "Learner"

    def store_outcome(self, incident: Incident, success: bool) -> Incident:
        outcome = {
            "incident_id": incident.id,
            "title": incident.title,
            "root_cause": incident.diagnosis.root_cause if incident.diagnosis else None,
            "action": incident.remediation_plan.action_type if incident.remediation_plan else None,
            "success": success,
            "stored_at": datetime.utcnow().isoformat(),
        }
        LEARNED_OUTCOMES.append(outcome)
        incident.events.append(
            AgentEvent(
                agent=self.name,
                message="Stored incident outcome for future recommendations",
                data=outcome,
            )
        )
        return incident
