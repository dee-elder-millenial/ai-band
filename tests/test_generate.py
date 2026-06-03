from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_band.bandleader import create_default_song
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

    def test_bandleader_progression_follows_key_and_scale(self) -> None:
        major_song = create_default_song(key="C", scale="major")
        minor_song = create_default_song(key="A", scale="minor")

        self.assertEqual([chord.symbol for chord in major_song.sections[0].chords], ["C", "Am", "F", "G"])
        self.assertEqual([chord.symbol for chord in minor_song.sections[0].chords], ["Am", "F", "C", "G"])

    def test_tracks_include_phase1_band_members(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks()

        self.assertEqual(
            [track.name for track in tracks],
            [
                "AI Bandleader",
                "AI Drummer",
                "AI Bass Player",
                "AI Guitar Player",
                "AI Keyboard Player",
                "AI Lead Player",
                "AI Percussion Extras",
            ],
        )

    def test_ehaye_mode_defaults_to_backing_band_without_ai_rhythm_guitar(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks(mode="ehaye")

        self.assertEqual(
            [track.name for track in tracks],
            [
                "AI Bandleader",
                "AI Drummer",
                "AI Bass Player",
                "AI Keyboard Player",
                "AI Lead Player",
                "AI Percussion Extras",
            ],
        )

    def test_ehaye_mode_can_force_ai_rhythm_guitar_back_on(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks(mode="ehaye", include_ai_rhythm_guitar=True)

        self.assertIn("AI Guitar Player", [track.name for track in tracks])


if __name__ == "__main__":
    unittest.main()
