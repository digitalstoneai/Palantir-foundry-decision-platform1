import asyncio
import json

from anthropic import AsyncAnthropic

from core.config import TaskComplexity, resolve_model
from models.ontology import ImpactAnalysisResponse

SYSTEM_PROMPT = """You are an operational awareness assistant for a Palantir Foundry-style \
ontology of facilities, assets, orders, incidents, and teams. Given a set of ontology objects \
and the relationship links between them, identify every object affected by a disruption to the \
specified object, and explain the dependency path that connects them.

Respond with ONLY a JSON object matching this exact schema, no other text and no markdown code fences:
{
  "affected_objects": ["<object_id>", ...],
  "dependency_path": [{"from": "<object_id>", "to": "<object_id>", "relation": "<link type>"}, ...],
  "summary": "<2-4 sentence explanation of what is affected and why>",
  "confidence": <float between 0.0 and 1.0>
}"""

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic()
    return _client


def _extract_json(text: str) -> dict:
    """Strip an optional ```json ... ``` markdown fence before parsing."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


def _build_user_prompt(object_id: str, objects: list[dict], links: list[dict], event: dict | None) -> str:
    payload = {
        "target_object_id": object_id,
        "objects": objects,
        "links": links,
        "event": event,
    }
    return json.dumps(payload, default=str)


def _fallback_impact(object_id: str, links: list[dict]) -> dict:
    """Logic-only impact trace via breadth-first graph walk, used when the AI call fails."""
    affected: set[str] = set()
    path: list[dict] = []
    frontier = {object_id}
    for _ in range(2):
        next_frontier: set[str] = set()
        for link in links:
            if link["source_id"] in frontier and link["target_id"] not in affected | {object_id}:
                next_frontier.add(link["target_id"])
                path.append({"from": link["source_id"], "to": link["target_id"], "relation": link["type"]})
            if link["target_id"] in frontier and link["source_id"] not in affected | {object_id}:
                next_frontier.add(link["source_id"])
                path.append({"from": link["target_id"], "to": link["source_id"], "relation": link["type"]})
        affected |= next_frontier
        frontier = next_frontier
    return {
        "affected_objects": sorted(affected),
        "dependency_path": path,
        "summary": (
            f"Logic-only fallback: traced direct and indirect graph links from '{object_id}' up to "
            "two hops. AI reasoning was unavailable, so no causal explanation is provided."
        ),
        "confidence": 0.4,
    }


async def analyze_impact(
    object_id: str,
    objects: list[dict],
    links: list[dict],
    event: dict | None,
) -> ImpactAnalysisResponse:
    model = resolve_model(TaskComplexity.REASONING)
    user_prompt = _build_user_prompt(object_id, objects, links, event)
    client = _get_client()

    result: dict | None = None
    degraded_mode = False

    for attempt in range(2):
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            result = _extract_json(response.content[0].text)
            break
        except Exception:
            if attempt == 0:
                await asyncio.sleep(2)
                continue
            result = _fallback_impact(object_id, links)
            degraded_mode = True

    return ImpactAnalysisResponse(
        object_id=object_id,
        affected_objects=result["affected_objects"],
        dependency_path=result["dependency_path"],
        summary=result["summary"],
        confidence=result["confidence"],
        ai_model=model,
        degraded_mode=degraded_mode,
    )
