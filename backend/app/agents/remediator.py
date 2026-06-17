from app.core.state import RUNBOOKS
from app.models import AgentEvent, Incident, IncidentStatus, RemediationPlan

class RemediatorAgent:
    name = "Remediator"

    def _score_runbook(self, runbook: dict, incident: Incident) -> int:
        score = 0
        diagnosis_text = ""
        if incident.diagnosis:
            diagnosis_text = (incident.diagnosis.root_cause + " " + incident.diagnosis.recommended_action).lower()
        for symptom in runbook["symptoms"]:
            if symptom in incident.signals:
                score += 2
        for root in runbook["root_causes"]:
            if root in diagnosis_text:
                score += 3
        return score

    def plan(self, incident: Incident) -> Incident:
        service = incident.affected_services[0]
        best = max(RUNBOOKS, key=lambda rb: self._score_runbook(rb, incident))
        plan = RemediationPlan(
            action_type=best["action_type"],
            target=best["target_template"].format(service=service),
            command=best["command_template"].format(service=service),
            reason=f"Matched runbook: {best['title']}",
            risk=best["risk"],
            validation=best["validation"],
        )
        incident.status = IncidentStatus.REMEDIATION_PLANNED
        incident.remediation_plan = plan
        incident.events.append(
            AgentEvent(
                agent=self.name,
                message=f"Prepared remediation plan: {plan.action_type} on {plan.target}",
                data=plan.model_dump(),
            )
        )
        return incident

    def execute(self, incident: Incident) -> Incident:
        incident.status = IncidentStatus.EXECUTING
        incident.events.append(
            AgentEvent(
                agent=self.name,
                message="Executed remediation in simulation mode",
                data={"command": incident.remediation_plan.command if incident.remediation_plan else None},
            )
        )
        return incident
