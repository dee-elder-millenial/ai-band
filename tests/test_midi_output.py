from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_band.generate import build_tracks
from ai_band.midi import write_midi
from ai_band.midi_read import read_midi_summary


class MidiOutputTests(unittest.TestCase):
    def test_generated_midi_reads_back_expected_band_structure(self) -> None:
        ticks_per_beat, tempo_bpm, tracks = build_tracks()

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sketch.mid"
            write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)
            summary = read_midi_summary(output)

        self.assertEqual(summary.format, 1)
        self.assertEqual(summary.track_count, 8)
        self.assertEqual(summary.ticks_per_beat, 480)

        track_names = [track.name for track in summary.tracks]
        self.assertEqual(
            track_names,
            [
                None,
                "AI Bandleader",
                "AI Drummer",
                "AI Bass Player",
                "AI Guitar Player",
                "AI Keyboard Player",
                "AI Lead Player",
                "AI Percussion Extras",
            ],
        )

        bandleader = summary.tracks[1]
        self.assertEqual(bandleader.markers, ["Intro", "Verse", "Chorus", "Outro"])
        self.assertGreaterEqual(len(bandleader.text), 4)

        playable_tracks = summary.tracks[2:]
        for track in playable_tracks:
            self.assertGreater(track.note_count, 0, track.name)

        self.assertEqual(summary.tracks[2].channels, {9})
        self.assertEqual(summary.tracks[3].channels, {0})
        self.assertEqual(summary.tracks[4].channels, {1})
        self.assertEqual(summary.tracks[5].channels, {2})
        self.assertEqual(summary.tracks[6].channels, {3})
        self.assertEqual(summary.tracks[7].channels, {9})

    def test_ehaye_mode_reads_back_without_ai_rhythm_guitar(self) -> None:
        ticks_per_beat, tempo_bpm, tracks = build_tracks(mode="ehaye")

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "ehaye.mid"
            write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)
            summary = read_midi_summary(output)

        self.assertEqual(summary.track_count, 7)
        self.assertEqual(
            [track.name for track in summary.tracks],
            [
                None,
                "AI Bandleader",
                "AI Drummer",
                "AI Bass Player",
                "AI Keyboard Player",
                "AI Lead Player",
                "AI Percussion Extras",
            ],
        )
        self.assertIn("The Ehaye Band mode", " ".join(summary.tracks[1].text))


if __name__ == "__main__":
    unittest.main()
