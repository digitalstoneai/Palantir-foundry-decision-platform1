import asyncio
import json

from anthropic import AsyncAnthropic

from core.config import TaskComplexity, resolve_model
from models.decision import Constraint, RecommendationResponse

SYSTEM_PROMPT = """You are an operational decision advisor. Given a list of response options and \
user-defined constraints with weights, evaluate each option and recommend the best choice. Explain \
your reasoning and identify which constraint tradeoffs most affect the decision.

Respond with ONLY a JSON object matching this exact schema, no other text and no markdown code fences:
{
  "recommended_option_id": "<option_id>",
  "rationale": "<2-4 sentence explanation of why this option was chosen>",
  "confidence": <float between 0.0 and 1.0>,
  "tradeoff_summary": "<1-3 sentences on which constraint tradeoff most drove the decision and what would change the answer>",
  "constraint_scores": {"<constraint_name>": <float between 0.0 and 1.0>, ...}
}"""

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


def _build_user_prompt(event: dict, options: list[dict], constraints: list[Constraint]) -> str:
    payload = {
        "event": event,
        "options": options,
        "constraints": [c.model_dump() for c in constraints],
    }
    return json.dumps(payload, default=str)


def _fallback_recommendation(options: list[dict], constraints: list[Constraint]) -> dict:
    """Deterministic weighted-penalty scoring, used when the AI call fails."""
    weights = {c.name: c.weight for c in constraints}
    cost_w = weights.get("cost", 1.0)
    service_w = weights.get("service", 1.0)
    risk_w = weights.get("risk", 1.0)

    max_cost = max((o.get("cost_impact") or 0 for o in options), default=1) or 1
    max_service_drop = max((abs(o.get("service_impact") or 0) for o in options), default=1) or 1

    scored = []
    for option in options:
        norm_cost = (option.get("cost_impact") or 0) / max_cost
        norm_service = abs(option.get("service_impact") or 0) / max_service_drop
        norm_risk = option.get("risk_score") or 0
        penalty = cost_w * norm_cost + service_w * norm_service + risk_w * norm_risk
        scored.append((option, penalty, norm_cost, norm_service, norm_risk))

    best, penalty, norm_cost, norm_service, norm_risk = min(scored, key=lambda s: s[1])

    return {
        "recommended_option_id": best["id"],
        "rationale": (
            f"Logic-only fallback: '{best['label']}' has the lowest weighted penalty across cost, "
            "service, and risk constraints. AI reasoning was unavailable, so no qualitative tradeoff "
            "explanation is provided."
        ),
        "confidence": 0.4,
        "tradeoff_summary": "Fallback scoring used a fixed weighted-penalty formula, not constraint-aware reasoning.",
        "constraint_scores": {
            "cost": round(1 - norm_cost, 2),
            "service": round(1 - norm_service, 2),
            "risk": round(1 - norm_risk, 2),
        },
    }


async def recommend_option(
    event: dict,
    options: list[dict],
    constraints: list[Constraint],
) -> RecommendationResponse:
    model = resolve_model(TaskComplexity.REASONING)
    user_prompt = _build_user_prompt(event, options, constraints)
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
            result = _fallback_recommendation(options, constraints)
            degraded_mode = True

    return RecommendationResponse(
        recommended_option_id=result["recommended_option_id"],
        rationale=result["rationale"],
        confidence=result["confidence"],
        tradeoff_summary=result["tradeoff_summary"],
        constraint_scores=result["constraint_scores"],
        ai_model=model,
        degraded_mode=degraded_mode,
    )
