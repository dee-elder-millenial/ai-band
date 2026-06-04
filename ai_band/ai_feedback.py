from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ai_band.api_budget import budget_status, format_budget_status, record_response_usage
from ai_band.controls import GenerationControls, controls_from_cue
from ai_band.live_cue import LiveCue, read_live_cue

DEFAULT_MODEL = "gpt-5.4-mini"
RESPONSES_URL = "https://api.openai.com/v1/responses"
CONTROL_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "bass_simplify": {"type": "boolean"},
        "drums_bigger": {"type": "boolean"},
        "keys_leave_space": {"type": "boolean"},
        "lead_sparse": {"type": "boolean"},
        "target_member": {"type": "string"},
        "rationale": {"type": "string"},
    },
    "required": ["bass_simplify", "drums_bigger", "keys_leave_space", "lead_sparse", "target_member", "rationale"],
}


@dataclass(frozen=True)
class AiFeedbackResult:
    controls: GenerationControls
    source: str
    model: str | None = None
    rationale: str = ""
    error: str | None = None
    budget_message: str | None = None


@dataclass(frozen=True)
class OpenAiCallResult:
    payload: dict[str, Any]
    usage: dict[str, Any]


def controls_from_cue_with_ai(
    cue: LiveCue | None,
    *,
    model: str | None = None,
    api_key: str | None = None,
    timeout_seconds: float = 20.0,
    force_ai: bool = False,
) -> AiFeedbackResult:
    fallback = controls_from_cue(cue)
    if cue is None:
        return AiFeedbackResult(fallback, source="none")

    selected_model = model or os.getenv("AI_BAND_OPENAI_MODEL", DEFAULT_MODEL)
    selected_key = api_key or os.getenv("OPENAI_API_KEY")
    if not selected_key:
        if force_ai:
            raise RuntimeError("AI feedback failed: OPENAI_API_KEY is not set")
        return AiFeedbackResult(fallback, source="fallback", model=selected_model)

    try:
        current_budget = budget_status()
        if current_budget.exhausted:
            raise RuntimeError(format_budget_status(current_budget))
        call_result = _call_openai(cue, selected_model, selected_key, timeout_seconds)
        payload = call_result.payload
        updated_budget = record_response_usage(model=selected_model, usage=call_result.usage, cue_instruction=cue.instruction)
        controls = _controls_from_model_payload(cue, payload)
        return AiFeedbackResult(
            controls=controls,
            source="openai",
            model=selected_model,
            rationale=str(payload.get("rationale", "")),
            budget_message=format_budget_status(updated_budget),
        )
    except (OSError, RuntimeError, ValueError, KeyError, urllib.error.URLError) as exc:
        if force_ai:
            raise RuntimeError(f"AI feedback failed: {exc}") from exc
        return AiFeedbackResult(fallback, source="fallback", model=selected_model, error=str(exc))


def _call_openai(cue: LiveCue, model: str, api_key: str, timeout_seconds: float) -> OpenAiCallResult:
    body = {
        "model": model,
        "store": False,
        "max_output_tokens": 300,
        "instructions": (
            "You are the bandleader for AI Band, a REAPER MIDI backing-band generator. "
            "Interpret the musician's cue into conservative generation controls. "
            "Use booleans for the four controls. Keep rationale under 140 characters."
        ),
        "input": json.dumps(_cue_context(cue), indent=2),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "ai_band_generation_controls",
                "strict": True,
                "schema": CONTROL_SCHEMA,
            }
        },
    }
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        RESPONSES_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        response_body = json.loads(response.read().decode("utf-8"))
    text = _extract_response_text(response_body)
    usage = response_body.get("usage", {})
    if not isinstance(usage, dict):
        usage = {}
    return OpenAiCallResult(payload=json.loads(text), usage=usage)


def _cue_context(cue: LiveCue) -> dict[str, object]:
    return {
        "cue": {
            "instruction": cue.instruction,
            "target": cue.target,
            "intensity": cue.intensity,
            "play_position_seconds": cue.play_position_seconds,
            "project_path": cue.project_path,
        },
        "available_controls": {
            "bass_simplify": "Make bass part sparser and less busy.",
            "drums_bigger": "Increase drum confidence/intensity in choruses.",
            "keys_leave_space": "Thin keyboard support so vocals/guitar have room.",
            "lead_sparse": "Make lead guitar answer phrases instead of playing too much.",
        },
    }


def _extract_response_text(response_body: dict[str, Any]) -> str:
    if isinstance(response_body.get("output_text"), str):
        return response_body["output_text"]
    output = response_body.get("output", [])
    for item in output:
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                return content["text"]
    raise ValueError("OpenAI response did not include output text")


def _controls_from_model_payload(cue: LiveCue, payload: dict[str, Any]) -> GenerationControls:
    return GenerationControls(
        bass_simplify=bool(payload.get("bass_simplify", False)),
        drums_bigger=bool(payload.get("drums_bigger", False)),
        keys_leave_space=bool(payload.get("keys_leave_space", False)),
        lead_sparse=bool(payload.get("lead_sparse", False)),
        cue_summary=f"AI {cue.target}: {cue.instruction} (intensity={cue.intensity:.2f})",
    )


def result_to_json(result: AiFeedbackResult) -> str:
    data = {
        "source": result.source,
        "model": result.model,
        "rationale": result.rationale,
        "error": result.error,
        "budget": result.budget_message,
        "controls": asdict(result.controls),
    }
    return json.dumps(data, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Interpret an AI Band live cue with optional real AI feedback.")
    parser.add_argument("--cue", default="state/live_cue.json", help="Cue JSON path")
    parser.add_argument("--model", default=None, help=f"OpenAI model. Defaults to {DEFAULT_MODEL} or AI_BAND_OPENAI_MODEL.")
    parser.add_argument("--output-json", help="Optional path for interpreted controls JSON")
    parser.add_argument("--force-ai", action="store_true", help="Fail instead of falling back when the AI call cannot run")
    args = parser.parse_args()

    result = controls_from_cue_with_ai(read_live_cue(args.cue), model=args.model, force_ai=args.force_ai)
    text = result_to_json(result)
    if args.output_json:
        Path(args.output_json).write_text(text, encoding="utf-8")
    print(text, end="")
    if result.budget_message:
        print(result.budget_message)


if __name__ == "__main__":
    main()
