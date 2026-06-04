from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai_band.ai_feedback import AiFeedbackResult
from ai_band.controls import GenerationControls
from ai_band.midi_read import read_midi_summary
from ai_band.respond import write_feedback_response


class FeedbackResponseTests(unittest.TestCase):
    def test_write_feedback_response_creates_decision_json_and_midi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cue_path = root / "live_cue.json"
            decision_path = root / "decision.json"
            midi_path = root / "response.mid"
            cue_path.write_text(
                json.dumps(
                    {
                        "mode": "live-cue",
                        "instruction": "keys and lead are stepping on my vocal",
                        "target": "bandleader",
                        "intensity": 0.8,
                        "play_position_seconds": 12.0,
                        "project_path": "",
                    }
                ),
                encoding="utf-8",
            )
            feedback = AiFeedbackResult(
                controls=GenerationControls(keys_leave_space=True, lead_sparse=True, cue_summary="AI test cue"),
                source="openai",
                model="test-model",
                rationale="Make room for vocal.",
                budget_message="AI Band estimated API spend: $0.0001 / $5.00",
            )

            with patch("ai_band.respond.controls_from_cue_with_ai", return_value=feedback):
                response = write_feedback_response(
                    cue_path=cue_path,
                    midi_output=midi_path,
                    decision_output=decision_path,
                    preset="bluesy-alt-country",
                    key="D",
                    scale="major",
                    tempo_bpm=96,
                )

            decision = json.loads(decision_path.read_text(encoding="utf-8"))
            summary = read_midi_summary(midi_path)

        self.assertEqual(response.feedback.source, "openai")
        self.assertEqual(decision["source"], "openai")
        self.assertEqual(decision["cue"]["instruction"], "keys and lead are stepping on my vocal")
        self.assertTrue(decision["controls"]["keys_leave_space"])
        self.assertEqual(summary.format, 1)
        self.assertIn("AI Bandleader", [track.name for track in summary.tracks])
        self.assertIn("Live cue applied", " ".join(summary.tracks[1].text))


if __name__ == "__main__":
    unittest.main()
