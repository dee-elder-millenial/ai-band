from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_band.generate import build_tracks
from ai_band.midi import write_midi


class GenerateMidiTests(unittest.TestCase):
    def test_generated_midi_has_expected_header(self) -> None:
        ticks_per_beat, tempo_bpm, tracks = build_tracks()

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sketch.mid"
            write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)
            data = output.read_bytes()

        self.assertEqual(data[:4], b"MThd")
        self.assertEqual(int.from_bytes(data[8:10], "big"), 1)
        self.assertEqual(int.from_bytes(data[10:12], "big"), 8)
        self.assertEqual(int.from_bytes(data[12:14], "big"), 480)


if __name__ == "__main__":
    unittest.main()

