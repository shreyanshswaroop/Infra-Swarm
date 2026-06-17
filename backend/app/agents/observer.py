from app.models import AgentEvent, Incident, IncidentStatus, Severity

class ObserverAgent:
    name = "Observer"

    def detect(self, signal: dict) -> Incident:
        service = signal.get("service", "unknown-service")
        issue = signal.get("type", "anomaly")
        severity = Severity.SEV2 if issue in ["memory_leak", "network_partition"] else Severity.SEV3

        incident = Incident(
            title=f"{service} {issue.replace('_', ' ')} detected",
            severity=severity,
            status=IncidentStatus.DETECTED,
            affected_services=[service],
            signals=signal.get("signals", [issue]),
        )
        incident.events.append(
            AgentEvent(
                agent=self.name,
                message=f"Detected anomaly in {service}",
                data=signal,
            )
        )
        return incident
