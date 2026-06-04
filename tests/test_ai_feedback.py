from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from ai_band.ai_feedback import (
    CONTROL_SCHEMA,
    _call_openai,
    _extract_response_text,
    controls_from_cue_with_ai,
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
        model_payload = {
            "bass_simplify": False,
            "drums_bigger": False,
            "keys_leave_space": True,
            "lead_sparse": True,
            "target_member": "bandleader",
            "rationale": "Open space for the vocal.",
        }

        with patch("ai_band.ai_feedback._call_openai", return_value=model_payload), patch.dict(
            os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True
        ):
            result = controls_from_cue_with_ai(cue, model="test-model")

        self.assertEqual(result.source, "openai")
        self.assertEqual(result.model, "test-model")
        self.assertTrue(result.controls.keys_leave_space)
        self.assertTrue(result.controls.lead_sparse)
        self.assertIn("AI bandleader", result.controls.cue_summary or "")

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
                                    "bass_simplify": True,
                                    "drums_bigger": False,
                                    "keys_leave_space": False,
                                    "lead_sparse": False,
                                    "target_member": "bass",
                                    "rationale": "Make room.",
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

        with patch.dict(os.environ, {"OPENAI_API_KEY": "secret-value"}, clear=True):
            result = controls_from_cue_with_ai(cue, api_key=None)

        self.assertNotIn("secret-value", result_to_json(result))

    def test_control_schema_requires_all_model_fields(self) -> None:
        self.assertEqual(
            set(CONTROL_SCHEMA["required"]),
            {"bass_simplify", "drums_bigger", "keys_leave_space", "lead_sparse", "target_member", "rationale"},
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
                                "bass_simplify": False,
                                "drums_bigger": False,
                                "keys_leave_space": False,
                                "lead_sparse": True,
                                "target_member": "lead",
                                "rationale": "Lead should answer only.",
                            }
                        )
                    }
                ).encode("utf-8")

        def fake_urlopen(request: object, timeout: float) -> FakeResponse:
            captured["timeout"] = timeout
            captured["body"] = json.loads(request.data.decode("utf-8"))  # type: ignore[attr-defined]
            return FakeResponse()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            payload = _call_openai(cue, "test-model", "test-key", 3.0)

        self.assertTrue(payload["lead_sparse"])
        self.assertEqual(captured["timeout"], 3.0)
        body = captured["body"]
        self.assertIsInstance(body, dict)
        self.assertIs(body["store"], False)
        self.assertEqual(body["max_output_tokens"], 300)
        self.assertEqual(body["text"]["format"]["type"], "json_schema")  # type: ignore[index]


if __name__ == "__main__":
    unittest.main()
