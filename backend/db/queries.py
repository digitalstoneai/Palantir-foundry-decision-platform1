import json
import uuid
from datetime import datetime, timezone
from typing import Optional

import aiosqlite

from core.config import DB_PATH


async def _connect() -> aiosqlite.Connection:
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    return conn


def _object_row(row: aiosqlite.Row) -> dict:
    data = dict(row)
    data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else None
    return data


async def get_objects() -> list[dict]:
    conn = await _connect()
    try:
        rows = await conn.execute_fetchall("SELECT * FROM objects ORDER BY id")
        return [_object_row(r) for r in rows]
    finally:
        await conn.close()


async def get_object(object_id: str) -> Optional[dict]:
    conn = await _connect()
    try:
        cursor = await conn.execute("SELECT * FROM objects WHERE id = ?", (object_id,))
        row = await cursor.fetchone()
        return _object_row(row) if row else None
    finally:
        await conn.close()


async def get_links(source_id: Optional[str] = None, target_id: Optional[str] = None) -> list[dict]:
    conn = await _connect()
    try:
        query = "SELECT * FROM links WHERE 1=1"
        params: list[str] = []
        if source_id:
            query += " AND source_id = ?"
            params.append(source_id)
        if target_id:
            query += " AND target_id = ?"
            params.append(target_id)
        rows = await conn.execute_fetchall(query + " ORDER BY id", params)
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def get_events(severity: Optional[str] = None, resolved: Optional[bool] = None) -> list[dict]:
    conn = await _connect()
    try:
        query = "SELECT * FROM events WHERE 1=1"
        params: list = []
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if resolved is not None:
            query += " AND resolved = ?"
            params.append(1 if resolved else 0)
        rows = await conn.execute_fetchall(query + " ORDER BY id", params)
        return [dict(r) | {"resolved": bool(r["resolved"])} for r in rows]
    finally:
        await conn.close()


async def get_event(event_id: str) -> Optional[dict]:
    conn = await _connect()
    try:
        cursor = await conn.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = await cursor.fetchone()
        return dict(row) | {"resolved": bool(row["resolved"])} if row else None
    finally:
        await conn.close()


async def get_decision_options(event_id: str) -> list[dict]:
    conn = await _connect()
    try:
        rows = await conn.execute_fetchall(
            "SELECT * FROM decision_options WHERE event_id = ? ORDER BY id", (event_id,)
        )
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def create_decision_record(event_id: str, option_id: str, rationale: str, decided_by: str) -> dict:
    conn = await _connect()
    try:
        record_id = f"rec-{uuid.uuid4().hex[:8]}"
        decided_at = datetime.now(timezone.utc).isoformat()
        await conn.execute(
            "INSERT INTO decision_records (id, event_id, option_id, rationale, decided_by, decided_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (record_id, event_id, option_id, rationale, decided_by, decided_at),
        )
        await conn.commit()
        return {
            "id": record_id,
            "event_id": event_id,
            "option_id": option_id,
            "rationale": rationale,
            "decided_by": decided_by,
            "decided_at": decided_at,
            "outcome_notes": None,
            "ai_model": None,
        }
    finally:
        await conn.close()


async def get_decision_records(event_id: Optional[str] = None) -> list[dict]:
    conn = await _connect()
    try:
        query = "SELECT * FROM decision_records WHERE 1=1"
        params: list[str] = []
        if event_id:
            query += " AND event_id = ?"
            params.append(event_id)
        rows = await conn.execute_fetchall(query + " ORDER BY decided_at DESC", params)
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def create_action(
    action_type: str, object_id: str, requested_by: str, payload: Optional[dict], ai_rationale: str
) -> dict:
    conn = await _connect()
    try:
        action_id = f"act-{uuid.uuid4().hex[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()
        await conn.execute(
            "INSERT INTO actions (id, type, object_id, requested_by, status, payload, ai_rationale, "
            "created_at) VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)",
            (action_id, action_type, object_id, requested_by, json.dumps(payload), ai_rationale, created_at),
        )
        await conn.commit()
        return {"id": action_id, "status": "pending", "ai_rationale": ai_rationale}
    finally:
        await conn.close()


async def get_action(action_id: str) -> Optional[dict]:
    conn = await _connect()
    try:
        cursor = await conn.execute("SELECT * FROM actions WHERE id = ?", (action_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()


async def resolve_action(action_id: str, approved_by: str, approved: bool) -> Optional[dict]:
    conn = await _connect()
    try:
        status = "executed" if approved else "rejected"
        executed_at = datetime.now(timezone.utc).isoformat() if approved else None
        cursor = await conn.execute(
            "UPDATE actions SET status = ?, approved_by = ?, executed_at = ? WHERE id = ?",
            (status, approved_by, executed_at, action_id),
        )
        await conn.commit()
        if cursor.rowcount == 0:
            return None
        return await get_action(action_id)
    finally:
        await conn.close()


async def get_actions(status: Optional[str] = None, object_id: Optional[str] = None) -> list[dict]:
    conn = await _connect()
    try:
        query = "SELECT * FROM actions WHERE 1=1"
        params: list[str] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if object_id:
            query += " AND object_id = ?"
            params.append(object_id)
        rows = await conn.execute_fetchall(query + " ORDER BY created_at DESC", params)
        return [dict(r) for r in rows]
    finally:
        await conn.close()
