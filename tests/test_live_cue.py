from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ai_band.live_cue import read_live_cue


class LiveCueTests(unittest.TestCase):
    def test_read_live_cue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "live_cue.json"
            path.write_text(
                json.dumps(
                    {
                        "mode": "live-cue",
                        "instruction": "simplify bass",
                        "target": "bass",
                        "intensity": 0.7,
                        "play_position_seconds": 12.5,
                        "project_path": "song.rpp",
                    }
                ),
                encoding="utf-8",
            )

            cue = read_live_cue(path)

        self.assertEqual(cue.instruction, "simplify bass")
        self.assertEqual(cue.target, "bass")
        self.assertEqual(cue.intensity, 0.7)
        self.assertEqual(cue.play_position_seconds, 12.5)
        self.assertEqual(cue.project_path, "song.rpp")


if __name__ == "__main__":
    unittest.main()

