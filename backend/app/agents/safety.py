from app.models import AgentEvent, Incident, IncidentStatus, SafetyDecision

class SafetyAgent:
    name = "Safety"

    def review(self, incident: Incident) -> Incident:
        plan = incident.remediation_plan
        if not plan:
            decision = SafetyDecision(
                approved=False,
                requires_human_approval=False,
                blocked=True,
                reason="No remediation plan exists",
                blast_radius="unknown",
            )
        elif plan.action_type in ["DELETE_DATABASE", "DELETE_RESOURCE"]:
            decision = SafetyDecision(
                approved=False,
                requires_human_approval=False,
                blocked=True,
                reason="Destructive actions are blocked by policy",
                blast_radius="high",
            )
        elif plan.risk == "medium" or plan.action_type == "ROLLBACK_DEPLOYMENT":
            decision = SafetyDecision(
                approved=False,
                requires_human_approval=True,
                blocked=False,
                reason="Production rollback requires human approval",
                blast_radius="affected service and dependent services",
            )
            incident.status = IncidentStatus.AWAITING_APPROVAL
        else:
            decision = SafetyDecision(
                approved=True,
                requires_human_approval=False,
                blocked=False,
                reason="Low-risk action allowed by policy",
                blast_radius="single stateless service",
            )
            incident.status = IncidentStatus.SAFETY_REVIEW

        incident.safety_decision = decision
        incident.events.append(
            AgentEvent(
                agent=self.name,
                message=f"Safety decision: {decision.reason}",
                data=decision.model_dump(),
            )
        )
        return incident
