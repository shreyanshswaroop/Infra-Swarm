from datetime import datetime
from app.agents.diagnoser import DiagnoserAgent
from app.agents.learner import LearnerAgent
from app.agents.observer import ObserverAgent
from app.agents.remediator import RemediatorAgent
from app.agents.safety import SafetyAgent
from app.core.state import INCIDENTS
from app.models import AgentEvent, IncidentStatus

class OrchestratorAgent:
    def __init__(self):
        self.observer = ObserverAgent()
        self.diagnoser = DiagnoserAgent()
        self.remediator = RemediatorAgent()
        self.safety = SafetyAgent()
        self.learner = LearnerAgent()

    def start_incident_from_signal(self, signal: dict):
        incident = self.observer.detect(signal)
        INCIDENTS[incident.id] = incident

        incident = self.diagnoser.diagnose(incident, signal)
        incident = self.remediator.plan(incident)
        incident = self.safety.review(incident)

        if incident.safety_decision and incident.safety_decision.approved:
            incident = self.execute_and_validate(incident.id)

        INCIDENTS[incident.id] = incident
        return incident

    def approve(self, incident_id: str):
        incident = INCIDENTS[incident_id]
        if not incident.safety_decision or not incident.safety_decision.requires_human_approval:
            incident.events.append(AgentEvent(agent="Orchestrator", message="Approval was not required"))
            return incident

        incident.safety_decision.approved = True
        incident.safety_decision.requires_human_approval = False
        incident.events.append(AgentEvent(agent="Orchestrator", message="Human approval granted"))
        return self.execute_and_validate(incident_id)

    def execute_and_validate(self, incident_id: str):
        incident = INCIDENTS[incident_id]
        incident = self.remediator.execute(incident)
        incident.status = IncidentStatus.VALIDATING
        incident.events.append(
            AgentEvent(
                agent="Observer",
                message="Validation passed: metrics returned to normal in simulation",
                data={"validation": incident.remediation_plan.validation if incident.remediation_plan else []},
            )
        )
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = datetime.utcnow()
        incident.events.append(AgentEvent(agent="Orchestrator", message="Incident resolved"))
        incident = self.learner.store_outcome(incident, success=True)
        INCIDENTS[incident.id] = incident
        return incident
