from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai_band.api_budget import budget_status, estimate_response_cost_usd, read_usage, record_response_usage
from ai_band.ai_feedback import (
    CONTROL_SCHEMA,
    OpenAiCallResult,
    _call_openai,
    _extract_response_text,
    controls_from_cue_with_ai,
    result_to_dict,
    result_to_json,
)
from ai_band.live_cue import LiveCue


class AiFeedbackTests(unittest.TestCase):
    def test_missing_api_key_uses_keyword_fallback(self) -> None:
        cue = LiveCue("live-cue", "make bass simpler", "bandleader", 0.7, 12, "")

        with patch.dict(os.environ, {}, clear=True):
            result = controls_from_cue_with_ai(cue)

        self.assertEqual(result.source, "fallback")
        self.assertTrue(result.controls.bass_simplify)
        self.assertEqual(result.model, "gpt-5.4-mini")

    def test_model_payload_maps_to_generation_controls(self) -> None:
        cue = LiveCue("live-cue", "keys and lead need to leave space", "bandleader", 0.8, 20, "")
        model_payload = _model_payload(
            keys_leave_space=True,
            lead_sparse=True,
            target_member="bandleader",
            musician_reply="We'll open a pocket around the vocal.",
            musical_plan="Thin keys and make lead answer phrases only.",
            section_scope="whole song",
            rationale="Open space for the vocal.",
        )

        with tempfile.TemporaryDirectory() as tmp:
            usage_path = str(Path(tmp) / "usage.json")
            with patch("ai_band.ai_feedback._call_openai", return_value=OpenAiCallResult(model_payload, _sample_usage())), patch.dict(
                os.environ,
                {"OPENAI_API_KEY": "test-key", "AI_BAND_API_USAGE_PATH": usage_path},
                clear=True,
            ):
                result = controls_from_cue_with_ai(cue, model="gpt-5.4-mini")

        self.assertEqual(result.source, "openai")
        self.assertEqual(result.model, "gpt-5.4-mini")
        self.assertTrue(result.controls.keys_leave_space)
        self.assertTrue(result.controls.lead_sparse)
        self.assertIn("open a pocket", result.controls.cue_summary or "")
        self.assertEqual(result.musician_reply, "We'll open a pocket around the vocal.")
        self.assertEqual(result.musical_plan, "Thin keys and make lead answer phrases only.")
        self.assertIn("$", result.budget_message or "")

    def test_model_payload_maps_natural_bass_player_language_to_run(self) -> None:
        cue = LiveCue("live-cue", "walk me up into that chorus, but keep it classy", "bass player", 0.9, 13.8, "")
        model_payload = _model_payload(
            bass_run=True,
            target_member="bass",
            musician_reply="Got it. I'll walk up into the chorus and stay out of your way.",
            musical_plan="Add chorus walk-ups at phrase turns; keep verse bass simple.",
            section_scope="chorus transitions",
            rationale="Natural bassist cue maps to tasteful walk-ups.",
            confidence=0.91,
        )

        with tempfile.TemporaryDirectory() as tmp:
            usage_path = str(Path(tmp) / "usage.json")
            with patch("ai_band.ai_feedback._call_openai", return_value=OpenAiCallResult(model_payload, _sample_usage())), patch.dict(
                os.environ,
                {"OPENAI_API_KEY": "test-key", "AI_BAND_API_USAGE_PATH": usage_path},
                clear=True,
            ):
                result = controls_from_cue_with_ai(cue, model="gpt-5.4-mini")

        self.assertEqual(result.source, "openai")
        self.assertTrue(result.controls.bass_run)
        self.assertEqual(result.target_member, "bass")
        self.assertIn("walk up", result.musician_reply)
        self.assertEqual(result.section_scope, "chorus transitions")

    def test_api_failure_falls_back_unless_forced(self) -> None:
        cue = LiveCue("live-cue", "drums louder", "drums", 0.8, 0, "")

        with patch("ai_band.ai_feedback._call_openai", side_effect=ValueError("bad json")), patch.dict(
            os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True
        ):
            result = controls_from_cue_with_ai(cue)

        self.assertEqual(result.source, "fallback")
        self.assertTrue(result.controls.drums_bigger)
        self.assertEqual(result.error, "bad json")

    def test_force_ai_raises_when_key_missing(self) -> None:
        cue = LiveCue("live-cue", "simplify bass", "bass", 0.5, 0, "")

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
                controls_from_cue_with_ai(cue, force_ai=True)

    def test_extract_response_text_accepts_output_content_shape(self) -> None:
        response = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    **_model_payload(
                                        bass_simplify=True,
                                        target_member="bass",
                                        musician_reply="I'll lay back.",
                                        musical_plan="Simplify the bass line.",
                                        section_scope="whole song",
                                        rationale="Make room.",
                                    ),
                                }
                            ),
                        }
                    ]
                }
            ]
        }

        self.assertIn("bass_simplify", _extract_response_text(response))

    def test_result_json_does_not_include_api_key(self) -> None:
        cue = LiveCue("live-cue", "drums louder", "drums", 0.8, 0, "")

        with patch("ai_band.ai_feedback._call_openai", side_effect=ValueError("no network")), patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "secret-value"},
            clear=True,
        ):
            result = controls_from_cue_with_ai(cue, api_key=None)

        self.assertNotIn("secret-value", result_to_json(result))

    def test_result_to_dict_exposes_controls_for_response_loop(self) -> None:
        cue = LiveCue("live-cue", "simplify bass", "bass", 0.5, 0, "")

        result = controls_from_cue_with_ai(cue)
        data = result_to_dict(result)

        self.assertEqual(data["source"], "fallback")
        self.assertTrue(data["controls"]["bass_simplify"])  # type: ignore[index]

    def test_control_schema_requires_all_model_fields(self) -> None:
        self.assertEqual(
            set(CONTROL_SCHEMA["required"]),
            {
                "bass_simplify",
                "bass_run",
                "drums_bigger",
                "drum_fill",
                "drum_solo",
                "keys_leave_space",
                "lead_sparse",
                "target_member",
                "musician_reply",
                "musical_plan",
                "section_scope",
                "confidence",
                "rationale",
            },
        )

    def test_openai_request_uses_small_nonstored_structured_response(self) -> None:
        cue = LiveCue("live-cue", "lead should leave space", "lead", 0.5, 0, "")
        captured: dict[str, object] = {}

        class FakeResponse:
            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            def read(self) -> bytes:
                return json.dumps(
                    {
                        "output_text": json.dumps(
                            {
                                **_model_payload(
                                    lead_sparse=True,
                                    target_member="lead",
                                    musician_reply="I'll answer you, not cover you.",
                                    musical_plan="Sparse lead answers after vocal lines.",
                                    section_scope="vocal phrases",
                                    rationale="Lead should answer only.",
                                ),
                            }
                        )
                    }
                ).encode("utf-8")

        def fake_urlopen(request: object, timeout: float) -> FakeResponse:
            captured["timeout"] = timeout
            captured["body"] = json.loads(request.data.decode("utf-8"))  # type: ignore[attr-defined]
            return FakeResponse()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = _call_openai(cue, "test-model", "test-key", 3.0)

        payload = result.payload
        self.assertTrue(payload["lead_sparse"])
        self.assertEqual(captured["timeout"], 3.0)
        body = captured["body"]
        self.assertIsInstance(body, dict)
        self.assertIs(body["store"], False)
        self.assertEqual(body["max_output_tokens"], 300)
        self.assertEqual(body["text"]["format"]["type"], "json_schema")  # type: ignore[index]

    def test_budget_estimate_and_ledger_record_usage(self) -> None:
        usage = _sample_usage()
        cost = estimate_response_cost_usd("gpt-5.4-mini", usage)

        self.assertGreater(cost, 0)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "usage.json"
            status = record_response_usage(model="gpt-5.4-mini", usage=usage, path=path, cue_instruction="test cue")
            ledger = read_usage(path)

        self.assertEqual(status.call_count, 1)
        self.assertEqual(len(ledger["calls"]), 1)
        self.assertGreater(ledger["total_estimated_usd"], 0)

    def test_budget_status_warns_when_exhausted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "usage.json"
            path.write_text(json.dumps({"version": 1, "total_estimated_usd": 5.01, "calls": []}), encoding="utf-8")

            status = budget_status(path=path, budget_usd=5.0)

        self.assertTrue(status.exhausted)
        self.assertIn("exhausted", status.warning or "")


def _sample_usage() -> dict[str, object]:
    return {
        "input_tokens": 1000,
        "output_tokens": 100,
        "total_tokens": 1100,
        "input_tokens_details": {"cached_tokens": 100},
    }


def _model_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "bass_simplify": False,
        "bass_run": False,
        "drums_bigger": False,
        "drum_fill": False,
        "drum_solo": False,
        "keys_leave_space": False,
        "lead_sparse": False,
        "target_member": "bandleader",
        "musician_reply": "I hear it.",
        "musical_plan": "Make the closest conservative arrangement change.",
        "section_scope": "whole song",
        "confidence": 0.8,
        "rationale": "Conservative cue mapping.",
    }
    payload.update(overrides)
    return payload


if __name__ == "__main__":
    unittest.main()
