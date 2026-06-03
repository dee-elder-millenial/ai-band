from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_band.bandleader import create_default_song
from ai_band.controls import controls_from_cue
from ai_band.generate import build_tracks
from ai_band.live_cue import LiveCue
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

    def test_bluesy_alt_country_preset_uses_longer_form_and_flat_seven(self) -> None:
        song = create_default_song(key="D", scale="major", preset="bluesy-alt-country")

        self.assertEqual(song.total_bars, 24)
        self.assertEqual(song.preset, "bluesy-alt-country")
        self.assertEqual([section.name for section in song.sections], ["Intro", "Verse", "Chorus", "Outro"])
        self.assertIn("C", [chord.symbol for chord in song.sections[1].chords])

    def test_southern_blues_preset_uses_full_song_form(self) -> None:
        song = create_default_song(key="E", scale="minor", preset="southern-blues", tempo_bpm=86)

        self.assertEqual(song.total_bars, 76)
        self.assertEqual(song.preset, "southern-blues")
        self.assertEqual(
            [section.name for section in song.sections],
            ["Intro", "Verse 1", "Chorus 1", "Verse 2", "Chorus 2", "Bridge", "Solo", "Final Chorus", "Outro"],
        )
        self.assertIn("C", [chord.symbol for chord in song.sections[1].chords])

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

    def test_southern_blues_can_include_strummed_chordal_ai_rhythm_guitar(self) -> None:
        _ticks, _tempo, tracks = build_tracks(
            mode="ehaye",
            include_ai_rhythm_guitar=True,
            preset="southern-blues",
            key="E",
            scale="minor",
            tempo_bpm=86,
        )
        guitar = next(track for track in tracks if track.name == "AI Guitar Player")
        starts = [note.start for note in guitar.notes]

        self.assertGreaterEqual(len(guitar.notes), 1000)
        self.assertLessEqual(len(guitar.notes), 1400)
        self.assertLessEqual(max(note.velocity for note in guitar.notes), 64)
        self.assertTrue(any(start % 480 not in {0, 240} for start in starts))

    def test_keyboard_part_stays_sparse_for_backing_material(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks(mode="ehaye")
        keyboard = next(track for track in tracks if track.name == "AI Keyboard Player")
        lead = next(track for track in tracks if track.name == "AI Lead Player")

        self.assertLess(len(keyboard.notes), len(lead.notes))
        self.assertLessEqual(max(note.velocity for note in keyboard.notes), 56)

    def test_drum_part_uses_forward_velocities(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks(mode="ehaye")
        drums = next(track for track in tracks if track.name == "AI Drummer")

        self.assertGreaterEqual(max(note.velocity for note in drums.notes), 100)

    def test_bass_part_is_lighter_in_backing_mode(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks(mode="ehaye")
        bass = next(track for track in tracks if track.name == "AI Bass Player")

        self.assertLessEqual(len(bass.notes), 44)
        self.assertLessEqual(max(note.velocity for note in bass.notes), 82)

    def test_lead_part_has_phrase_space_and_timing_variation(self) -> None:
        song_ticks, _tempo_bpm, tracks = build_tracks(mode="ehaye")
        lead = next(track for track in tracks if track.name == "AI Lead Player")
        starts = [note.start for note in lead.notes]

        self.assertLess(len(lead.notes), 64)
        self.assertTrue(any(start % song_ticks != 0 for start in starts))

    def test_simplify_bass_cue_reduces_bass_notes(self) -> None:
        cue = LiveCue("live-cue", "simplify bass", "bandleader", 0.5, 12.0, "")
        controls = controls_from_cue(cue)
        _ticks, _tempo, normal_tracks = build_tracks(mode="ehaye")
        _ticks, _tempo, cued_tracks = build_tracks(mode="ehaye", controls=controls)

        normal_bass = next(track for track in normal_tracks if track.name == "AI Bass Player")
        cued_bass = next(track for track in cued_tracks if track.name == "AI Bass Player")
        bandleader = next(track for track in cued_tracks if track.name == "AI Bandleader")

        self.assertLess(len(cued_bass.notes), len(normal_bass.notes))
        self.assertTrue(any("Live cue applied" in meta.text for meta in bandleader.metas))

    def test_cue_interpreter_maps_common_commands(self) -> None:
        controls = controls_from_cue(LiveCue("live-cue", "drums bigger in chorus", "bandleader", 0.8, 0, ""))
        self.assertTrue(controls.drums_bigger)

        controls = controls_from_cue(LiveCue("live-cue", "keys leave more space", "keys", 0.8, 0, ""))
        self.assertTrue(controls.keys_leave_space)

        controls = controls_from_cue(LiveCue("live-cue", "lead answer the vocal", "lead", 0.8, 0, ""))
        self.assertTrue(controls.lead_sparse)

    def test_bluesy_alt_country_generates_backing_tracks(self) -> None:
        _ticks, _tempo, tracks = build_tracks(
            mode="ehaye",
            preset="bluesy-alt-country",
            key="D",
            scale="major",
            tempo_bpm=96,
        )

        self.assertNotIn("AI Guitar Player", [track.name for track in tracks])
        self.assertGreater(len(next(track for track in tracks if track.name == "AI Drummer").notes), 0)

    def test_bluesy_alt_country_lead_uses_sparse_bent_licks(self) -> None:
        _ticks, _tempo, tracks = build_tracks(
            mode="ehaye",
            preset="bluesy-alt-country",
            key="D",
            scale="major",
            tempo_bpm=96,
        )
        lead = next(track for track in tracks if track.name == "AI Lead Player")

        self.assertLessEqual(len(lead.notes), 24)
        self.assertGreaterEqual(len(lead.events), 6)

    def test_southern_blues_generates_long_backing_song(self) -> None:
        _ticks, _tempo, tracks = build_tracks(
            mode="ehaye",
            preset="southern-blues",
            key="E",
            scale="minor",
            tempo_bpm=86,
        )
        lead = next(track for track in tracks if track.name == "AI Lead Player")

        self.assertNotIn("AI Guitar Player", [track.name for track in tracks])
        self.assertGreater(len(next(track for track in tracks if track.name == "AI Drummer").notes), 500)
        self.assertGreaterEqual(len(lead.events), 18)
        self.assertLessEqual(len(next(track for track in tracks if track.name == "AI Percussion Extras").notes), 120)

    def test_southern_blues_sound_polish_stays_controlled(self) -> None:
        _ticks, _tempo, tracks = build_tracks(
            mode="ehaye",
            preset="southern-blues",
            key="E",
            scale="minor",
            tempo_bpm=86,
        )
        drums = next(track for track in tracks if track.name == "AI Drummer")
        bass = next(track for track in tracks if track.name == "AI Bass Player")
        keyboard = next(track for track in tracks if track.name == "AI Keyboard Player")
        lead = next(track for track in tracks if track.name == "AI Lead Player")

        self.assertLessEqual(max(note.velocity for note in bass.notes), 80)
        self.assertLessEqual(len(keyboard.notes), 180)
        self.assertTrue(any(note.note == 51 for note in drums.notes))
        self.assertLessEqual(len(lead.notes), 80)


if __name__ == "__main__":
    unittest.main()
