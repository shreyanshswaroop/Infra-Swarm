from app.models import AgentEvent, Diagnosis, Incident, IncidentStatus

class DiagnoserAgent:
    name = "Diagnoser"

    def diagnose(self, incident: Incident, signal: dict) -> Incident:
        service = signal.get("service", incident.affected_services[0])
        issue_type = signal.get("type")

        if issue_type == "memory_leak":
            diagnosis = Diagnosis(
                root_cause=f"Likely memory leak in {service} after latest deployment",
                confidence=0.87,
                affected_services=[service, "checkout-service"],
                recommended_action="Rollback latest deployment or restart service if rollback is unavailable",
                evidence=[
                    "Memory usage is continuously increasing",
                    "Latency increased after memory pressure started",
                    "Logs show cache/object growth warnings",
                    "Deployment timestamp is close to incident start time",
                ],
            )
        elif issue_type == "cpu_spike":
            diagnosis = Diagnosis(
                root_cause=f"High CPU saturation on {service}",
                confidence=0.78,
                affected_services=[service],
                recommended_action="Scale service replicas within policy limit",
                evidence=["CPU above 90%", "p95 latency increased", "No deployment regression found"],
            )
        else:
            diagnosis = Diagnosis(
                root_cause=f"Unknown anomaly in {service}",
                confidence=0.45,
                affected_services=[service],
                recommended_action="Escalate to human SRE with collected evidence",
                evidence=["Signals are insufficient for confident diagnosis"],
            )

        incident.status = IncidentStatus.DIAGNOSING
        incident.diagnosis = diagnosis
        incident.affected_services = diagnosis.affected_services
        incident.events.append(
            AgentEvent(
                agent=self.name,
                message=f"Diagnosis completed: {diagnosis.root_cause}",
                data=diagnosis.model_dump(),
            )
        )
        return incident
