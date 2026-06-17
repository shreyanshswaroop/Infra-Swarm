import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "infra_swarm.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            service TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            remediation TEXT NOT NULL,
            safety TEXT NOT NULL,
            timeline TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def normalize_incident_for_frontend(incident: dict[str, Any]) -> dict[str, Any]:
    if "affected_services" not in incident:
        incident["affected_services"] = [incident["service"]]

    if "signals" not in incident:
        if incident["incident_type"] == "MEMORY_LEAK":
            incident["signals"] = [
                "memory_growth",
                "latency_spike",
                "timeout_errors",
            ]
        elif incident["incident_type"] == "CPU_SPIKE":
            incident["signals"] = [
                "cpu_spike",
                "latency_spike",
            ]
        else:
            incident["signals"] = []

    return incident


def save_incident(incident: dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO incidents (
            id,
            title,
            service,
            severity,
            status,
            incident_type,
            diagnosis,
            remediation,
            safety,
            timeline,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            incident["id"],
            incident["title"],
            incident["service"],
            incident["severity"],
            incident["status"],
            incident["incident_type"],
            json.dumps(incident["diagnosis"]),
            json.dumps(incident["remediation"]),
            json.dumps(incident["safety"]),
            json.dumps(incident["timeline"]),
            incident["created_at"],
            incident["updated_at"],
        ),
    )

    conn.commit()
    conn.close()


def list_incidents() -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT * FROM incidents
        ORDER BY created_at DESC
        """
    ).fetchall()

    conn.close()

    incidents = []

    for row in rows:
        incident = {
            "id": row["id"],
            "title": row["title"],
            "service": row["service"],
            "severity": row["severity"],
            "status": row["status"],
            "incident_type": row["incident_type"],
            "diagnosis": json.loads(row["diagnosis"]),
            "remediation": json.loads(row["remediation"]),
            "safety": json.loads(row["safety"]),
            "timeline": json.loads(row["timeline"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

        incidents.append(normalize_incident_for_frontend(incident))

    return incidents


def get_incident(incident_id: str) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()

    row = cursor.execute(
        """
        SELECT * FROM incidents
        WHERE id = ?
        """,
        (incident_id,),
    ).fetchone()

    conn.close()

    if row is None:
        return None

    incident = {
        "id": row["id"],
        "title": row["title"],
        "service": row["service"],
        "severity": row["severity"],
        "status": row["status"],
        "incident_type": row["incident_type"],
        "diagnosis": json.loads(row["diagnosis"]),
        "remediation": json.loads(row["remediation"]),
        "safety": json.loads(row["safety"]),
        "timeline": json.loads(row["timeline"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

    return normalize_incident_for_frontend(incident)


def find_existing_active_incident(service: str, incident_type: str) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()

    row = cursor.execute(
        """
        SELECT * FROM incidents
        WHERE service = ?
        AND incident_type = ?
        AND status IN ('AWAITING_APPROVAL', 'ACTIVE', 'DETECTED')
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (service, incident_type),
    ).fetchone()

    conn.close()

    if row is None:
        return None

    incident = {
        "id": row["id"],
        "title": row["title"],
        "service": row["service"],
        "severity": row["severity"],
        "status": row["status"],
        "incident_type": row["incident_type"],
        "diagnosis": json.loads(row["diagnosis"]),
        "remediation": json.loads(row["remediation"]),
        "safety": json.loads(row["safety"]),
        "timeline": json.loads(row["timeline"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

    return normalize_incident_for_frontend(incident)

def find_recent_incident(
    service: str,
    incident_type: str,
    minutes: int = 5,
) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor()

    cutoff_time = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()

    row = cursor.execute(
        """
        SELECT * FROM incidents
        WHERE service = ?
        AND incident_type = ?
        AND created_at >= ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (service, incident_type, cutoff_time),
    ).fetchone()

    conn.close()

    if row is None:
        return None

    incident = {
        "id": row["id"],
        "title": row["title"],
        "service": row["service"],
        "severity": row["severity"],
        "status": row["status"],
        "incident_type": row["incident_type"],
        "diagnosis": json.loads(row["diagnosis"]),
        "remediation": json.loads(row["remediation"]),
        "safety": json.loads(row["safety"]),
        "timeline": json.loads(row["timeline"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

    return normalize_incident_for_frontend(incident)