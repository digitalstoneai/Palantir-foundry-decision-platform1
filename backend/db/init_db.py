import json
import sqlite3
from datetime import datetime, timezone

from core.config import DB_PATH

DDL = """
CREATE TABLE IF NOT EXISTS objects (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL,
    name        TEXT NOT NULL,
    status      TEXT NOT NULL,
    owner_id    TEXT,
    metadata    TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS links (
    id          TEXT PRIMARY KEY,
    source_id   TEXT NOT NULL REFERENCES objects(id),
    target_id   TEXT NOT NULL REFERENCES objects(id),
    type        TEXT NOT NULL,
    weight      REAL DEFAULT 1.0,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id          TEXT PRIMARY KEY,
    object_id   TEXT NOT NULL REFERENCES objects(id),
    type        TEXT NOT NULL,
    severity    TEXT NOT NULL,
    description TEXT NOT NULL,
    resolved    INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_options (
    id              TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES events(id),
    label           TEXT NOT NULL,
    description     TEXT NOT NULL,
    cost_impact     REAL,
    service_impact  REAL,
    risk_score      REAL,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_records (
    id              TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES events(id),
    option_id       TEXT REFERENCES decision_options(id),
    rationale       TEXT,
    decided_by      TEXT NOT NULL,
    decided_at      TEXT NOT NULL,
    outcome_notes   TEXT,
    ai_model        TEXT
);

CREATE TABLE IF NOT EXISTS actions (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    object_id       TEXT NOT NULL REFERENCES objects(id),
    requested_by    TEXT NOT NULL,
    approved_by     TEXT,
    status          TEXT NOT NULL,
    payload         TEXT,
    ai_rationale    TEXT,
    created_at      TEXT NOT NULL,
    executed_at     TEXT
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_data(conn: sqlite3.Connection) -> None:
    ts = now()

    objects = [
        ("fac-dc-east", "facility", "Distribution Center East", "nominal", None, {"region": "east"}),
        ("fac-dc-west", "facility", "Distribution Center West", "nominal", None, {"region": "west"}),
        ("ast-conveyor-3", "asset", "Conveyor Line 3", "critical", None, {"facility": "fac-dc-east"}),
        ("ast-forklift-a", "asset", "Forklift Fleet A", "nominal", None, {"facility": "fac-dc-east", "units": 6}),
        ("ord-48217", "order", "Order #48217 — Regional Retail Restock", "at_risk", None, {"sla_hours": 6}),
        ("inc-conveyor-fail", "incident", "Conveyor Line 3 Motor Failure", "critical", None, {"detected_by": "sensor"}),
    ]
    conn.executemany(
        "INSERT INTO objects (id, type, name, status, owner_id, metadata, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [(o[0], o[1], o[2], o[3], o[4], json.dumps(o[5]), ts, ts) for o in objects],
    )

    links = [
        ("lnk-001", "ast-conveyor-3", "fac-dc-east", "located_at", 1.0),
        ("lnk-002", "ast-forklift-a", "fac-dc-east", "located_at", 1.0),
        ("lnk-003", "ord-48217", "ast-conveyor-3", "depends_on", 0.9),
        ("lnk-004", "ord-48217", "fac-dc-east", "depends_on", 0.8),
        ("lnk-005", "fac-dc-east", "ord-48217", "serves", 1.0),
        ("lnk-006", "fac-dc-west", "ord-48217", "serves", 0.4),
        ("lnk-007", "inc-conveyor-fail", "ast-conveyor-3", "affects", 1.0),
        ("lnk-008", "inc-conveyor-fail", "ord-48217", "affects", 0.7),
    ]
    conn.executemany(
        "INSERT INTO links (id, source_id, target_id, type, weight, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        [(*l, ts) for l in links],
    )

    events = [
        ("evt-001", "ast-conveyor-3", "anomaly", "urgent",
         "Conveyor Line 3 motor temperature exceeded threshold; line stopped automatically.", 0),
        ("evt-002", "ord-48217", "exception", "high",
         "Order #48217 fulfillment at risk due to conveyor outage; SLA breach in 6 hours.", 0),
        ("evt-003", "fac-dc-west", "status_change", "normal",
         "DC West capacity increased to support potential reroute.", 1),
    ]
    conn.executemany(
        "INSERT INTO events (id, object_id, type, severity, description, resolved, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(*e, ts) for e in events],
    )

    decision_options = [
        ("opt-001", "evt-001", "Reroute to DC West",
         "Shift remaining order volume to Distribution Center West for the duration of the outage.",
         4200.0, -0.05, 0.2),
        ("opt-002", "evt-001", "Expedite repair crew",
         "Call in an after-hours technician to repair the conveyor motor on-site.",
         1800.0, -0.15, 0.35),
        ("opt-003", "evt-001", "Manual conveyor bypass",
         "Route packages manually around the failed segment using floor staff.",
         600.0, -0.25, 0.55),
        ("opt-004", "evt-001", "Delay order, notify customer",
         "Push the order fulfillment date and proactively notify the customer of the delay.",
         200.0, -0.6, 0.1),
    ]
    conn.executemany(
        "INSERT INTO decision_options (id, event_id, label, description, cost_impact, service_impact, "
        "risk_score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [(*o, ts) for o in decision_options],
    )


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(DDL)
        counts = conn.execute("SELECT COUNT(*) FROM objects").fetchone()[0]
        if counts == 0:
            seed_data(conn)
            conn.commit()
            print(f"Initialized {DB_PATH} — tables created and seed data inserted.")
        else:
            print(f"Initialized {DB_PATH} — tables already seeded ({counts} objects), skipped reseed.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
