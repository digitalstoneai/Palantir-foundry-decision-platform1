import asyncio
import json
from datetime import datetime, timezone

from anthropic import AsyncAnthropic

from core.config import TaskComplexity, resolve_model
from models.brief import BriefingResponse

BRIEFING_SYSTEM_PROMPT = """You are an operational briefing assistant. Given a role and the current \
state of operational objects and events, write a focused briefing for that role: what matters to them \
right now, in plain language. Then list the IDs of the events that matter most.

Respond with ONLY a JSON object matching this exact schema, no other text and no markdown code fences:
{
  "content": "<markdown-formatted briefing, 3-6 sentences>",
  "top_exceptions": ["<event_id>", ...]
}"""

ACTION_RATIONALE_SYSTEM_PROMPT = """You are an operational action copilot. Given a proposed action \
type and the object it targets, write a one-paragraph rationale explaining why this action is \
appropriate given the object's current state. Respond with plain text only, no JSON, no markdown."""

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic()
    return _client


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


def _fallback_briefing(role: str, events: list[dict]) -> dict:
    urgent = [e for e in events if e["severity"] in ("urgent", "high") and not e["resolved"]]
    return {
        "content": (
            f"Logic-only fallback briefing for {role}: {len(urgent)} unresolved high-priority "
            "event(s) require attention. AI summarization was unavailable."
        ),
        "top_exceptions": [e["id"] for e in urgent[:3]],
    }


async def generate_briefing(role: str, objects: list[dict], events: list[dict]) -> BriefingResponse:
    model = resolve_model(TaskComplexity.FAST)
    client = _get_client()
    user_prompt = json.dumps({"role": role, "objects": objects, "events": events}, default=str)

    result: dict | None = None
    for attempt in range(2):
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=1024,
                system=BRIEFING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            result = _extract_json(response.content[0].text)
            break
        except Exception:
            if attempt == 0:
                await asyncio.sleep(2)
                continue
            result = _fallback_briefing(role, events)

    return BriefingResponse(
        role=role,
        content=result["content"],
        top_exceptions=result["top_exceptions"],
        generated_at=datetime.now(timezone.utc).isoformat(),
        ai_model=model,
    )


async def generate_action_rationale(action_type: str, object_data: dict) -> str:
    model = resolve_model(TaskComplexity.FAST)
    client = _get_client()
    user_prompt = json.dumps({"action_type": action_type, "object": object_data}, default=str)

    for attempt in range(2):
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=512,
                system=ACTION_RATIONALE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text.strip()
        except Exception:
            if attempt == 0:
                await asyncio.sleep(2)
                continue
            return (
                f"Logic-only fallback: '{action_type}' proposed for object "
                f"'{object_data.get('id')}' (status: {object_data.get('status')}). "
                "AI rationale was unavailable."
            )
