from __future__ import annotations

import unittest

from ai_band.generate import build_tracks, compose_tracks
from ai_band.midi import MidiNote, MidiTrack
from ai_band.performance import PerformanceSettings, default_performance_settings, render_performance


class PerformanceRenderTests(unittest.TestCase):
    def test_build_tracks_renders_mixer_and_instrument_preset_metadata(self) -> None:
        _ticks, _tempo, composed = compose_tracks()
        _ticks, _tempo, rendered = build_tracks()

        composed_bass = next(track for track in composed if track.name == "AI Bass Player")
        rendered_bass = next(track for track in rendered if track.name == "AI Bass Player")

        self.assertFalse(any("render-role=" in meta.text for meta in composed_bass.metas))
        self.assertTrue(any("render-role=bass" in meta.text for meta in rendered_bass.metas))
        self.assertTrue(any("Ample Bass" in meta.text for meta in rendered_bass.metas))
        self.assertTrue(any(event.status == 0xB0 and event.data[0] == 7 for event in rendered_bass.events))
        self.assertTrue(any(event.status == 0xB0 and event.data[0] == 91 for event in rendered_bass.events))
        self.assertTrue(any(event.status == 0xB0 and event.data[0] == 94 for event in rendered_bass.events))

    def test_swing_and_groove_controls_move_rendered_notes_when_requested(self) -> None:
        track = MidiTrack("Test Melody", channel=3, program=81)
        track.notes.extend(
            (
                MidiNote(0, 120, 60, 80, 3),
                MidiNote(240, 120, 62, 80, 3),
            )
        )

        rendered = render_performance(
            [track],
            ticks_per_beat=480,
            settings=PerformanceSettings(groove_amount=1.0, swing_amount=1.0, velocity_humanize_amount=1.0),
        )[0]

        self.assertNotEqual([note.start for note in rendered.notes], [0, 240])
        self.assertGreater(rendered.notes[1].start, 240)
        self.assertGreaterEqual(len({note.velocity for note in rendered.notes}), 2)

    def test_ample_strummer_profile_preserves_chord_block_timing(self) -> None:
        _ticks, _tempo, tracks = build_tracks(preset="heartland-rock", key="E", scale="major", tempo_bpm=118)
        guitar = next(track for track in tracks if track.name == "AI Guitar Player")
        chord_blocks: dict[int, list[MidiNote]] = {}
        for note in guitar.notes:
            chord_blocks.setdefault(note.start, []).append(note)

        self.assertGreaterEqual(len(chord_blocks), 80)
        self.assertEqual(max(max(note.start for note in notes) - min(note.start for note in notes) for notes in chord_blocks.values()), 0)
        self.assertTrue(any("Ample Guitar M Lite Strummer" in meta.text for meta in guitar.metas))

    def test_default_settings_expose_roles_for_drums_bass_chords_and_melody(self) -> None:
        settings = default_performance_settings()
        roles = {preset.role for preset in settings.track_presets.values()}

        self.assertTrue({"drums", "bass", "chords", "melody"}.issubset(roles))


if __name__ == "__main__":
    unittest.main()
