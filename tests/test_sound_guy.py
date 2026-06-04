from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_band.generate import build_tracks
from ai_band.midi import write_midi
from ai_band.midi_read import read_midi_summary
from ai_band.sound_guy import advise_sound_guy


class SoundGuyTests(unittest.TestCase):
    def test_sound_guy_protects_bass_and_simplifies_weird_rhythm_guitar(self) -> None:
        decision = advise_sound_guy(
            preset="heartland-rock",
            style="heartland hard rock",
            listening_note="bass is killing it, rhythm guitar sounds strange",
        )

        bass = decision.performance.track_presets["AI Bass Player"].mixer
        drums = decision.performance.track_presets["AI Drummer"].mixer
        keys = decision.performance.track_presets["AI Keyboard Player"].mixer
        lead = decision.performance.track_presets["AI Lead Player"].mixer

        self.assertEqual(decision.mix_profile, "bass-anchor")
        self.assertEqual(decision.rhythm_guitar_profile, "simple-blocks")
        self.assertGreaterEqual(bass.volume, 90)
        self.assertGreaterEqual(drums.volume, 100)
        self.assertLessEqual(keys.volume, 66)
        self.assertLessEqual(lead.volume, 70)
        self.assertGreater(decision.performance.groove_amount, 0)
        self.assertTrue(any("Protect the bass pocket" in note for note in decision.notes))

    def test_explicit_rhythm_guitar_profile_overrides_sound_guy_default(self) -> None:
        decision = advise_sound_guy(
            preset="heartland-rock",
            listening_note="rhythm guitar sounds strange",
            requested_rhythm_guitar_profile="internal-strum",
        )

        self.assertEqual(decision.rhythm_guitar_profile, "internal-strum")

    def test_build_tracks_can_include_non_playing_sound_guy_track(self) -> None:
        decision = advise_sound_guy(
            preset="heartland-rock",
            listening_note="bass is killing it, rhythm guitar sounds strange",
        )
        ticks, tempo, tracks = build_tracks(
            preset="heartland-rock",
            key="E",
            scale="major",
            tempo_bpm=118,
            sound_guy=decision,
        )

        self.assertEqual([track.name for track in tracks[:4]], ["AI Bandleader", "AI Sound Guy", "AI Drummer", "AI Bass Player"])
        sound_guy = next(track for track in tracks if track.name == "AI Sound Guy")
        guitar = next(track for track in tracks if track.name == "AI Guitar Player")
        self.assertEqual(sound_guy.notes, [])
        self.assertTrue(any("mix_profile=bass-anchor" in meta.text for meta in sound_guy.metas))
        self.assertLessEqual(len(guitar.notes), 400)

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sound-guy.mid"
            write_midi(output, tracks, ticks_per_beat=ticks, tempo_bpm=tempo)
            summary = read_midi_summary(output)

        self.assertIn("AI Sound Guy", [track.name for track in summary.tracks])


if __name__ == "__main__":
    unittest.main()
