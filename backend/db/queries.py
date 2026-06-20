import json
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


async def get_decision_options(event_id: str) -> list[dict]:
    conn = await _connect()
    try:
        rows = await conn.execute_fetchall(
            "SELECT * FROM decision_options WHERE event_id = ? ORDER BY id", (event_id,)
        )
        return [dict(r) for r in rows]
    finally:
        await conn.close()
