from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_band.bandleader import create_default_song
from ai_band.controls import controls_from_cue
from ai_band.generate import build_tracks
from ai_band.humanize import section_groove_offset
from ai_band.live_cue import LiveCue
from ai_band.midi import write_midi
from ai_band.theory import chord_tones


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

    def test_heartland_rock_preset_uses_driving_full_song_form(self) -> None:
        song = create_default_song(key="E", scale="major", preset="heartland-rock", tempo_bpm=118)

        self.assertEqual(song.total_bars, 88)
        self.assertEqual(song.preset, "heartland-rock")
        self.assertEqual(
            [section.name for section in song.sections],
            [
                "Intro",
                "Verse 1",
                "Pre-Chorus 1",
                "Chorus 1",
                "Verse 2",
                "Pre-Chorus 2",
                "Chorus 2",
                "Bridge",
                "Guitar Solo",
                "Final Chorus",
                "Outro",
            ],
        )

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

    def test_default_generation_applies_shared_human_feel(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks()
        members = {
            track.name: track
            for track in tracks
            if track.name
            in {
                "AI Drummer",
                "AI Bass Player",
                "AI Guitar Player",
                "AI Keyboard Player",
                "AI Lead Player",
                "AI Percussion Extras",
            }
        }

        self.assertEqual(len(members), 6)
        for name, track in members.items():
            with self.subTest(member=name):
                self.assertTrue(any(note.start % 120 != 0 for note in track.notes))
                self.assertGreaterEqual(len({note.velocity for note in track.notes}), 8)

    def test_lead_generation_varies_phrase_shapes_across_presets(self) -> None:
        scenarios = (
            ({}, 7, 12),
            ({"mode": "ehaye", "preset": "southern-blues", "key": "E", "scale": "minor", "tempo_bpm": 86}, 8, 12),
            ({"preset": "heartland-rock", "key": "E", "scale": "major", "tempo_bpm": 118}, 5, 24),
        )

        for kwargs, minimum_pitches, minimum_durations in scenarios:
            with self.subTest(preset=kwargs.get("preset", "default")):
                _ticks_per_beat, _tempo_bpm, tracks = build_tracks(**kwargs)
                lead = next(track for track in tracks if track.name == "AI Lead Player")

                self.assertGreaterEqual(len({note.note for note in lead.notes}), minimum_pitches)
                self.assertGreaterEqual(len({note.duration for note in lead.notes}), minimum_durations)
                self.assertTrue(any(note.start % 120 != 0 for note in lead.notes))

    def test_pitch_bend_tracks_start_and_end_centered(self) -> None:
        _ticks, _tempo, tracks = build_tracks(preset="heartland-rock", key="E", scale="major", tempo_bpm=118)

        for track in tracks:
            if track.channel is None:
                continue
            pitch_bends = [event for event in track.events if event.status == (0xE0 | track.channel)]
            if not pitch_bends:
                continue
            with self.subTest(track=track.name):
                bend_values = [(event.tick, event.data[0] | (event.data[1] << 7)) for event in pitch_bends]
                self.assertIn((0, 8192), bend_values)
                last_tick = max(tick for tick, _value in bend_values)
                self.assertIn((last_tick, 8192), bend_values)

    def test_heartland_bandleader_includes_reaper_audition_hint(self) -> None:
        _ticks, _tempo, tracks = build_tracks(preset="heartland-rock", key="E", scale="major", tempo_bpm=118)
        bandleader = next(track for track in tracks if track.name == "AI Bandleader")
        text = " ".join(meta.text for meta in bandleader.metas if meta.kind == "text")

        self.assertIn("ai_band_apply_audition_mix.lua", text)
        self.assertIn("lead-back", text)
        self.assertIn("warmer-room", text)
        self.assertIn("drums-forward", text)

    def test_default_generation_leaves_arrangement_space(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks()
        bar_ticks = 480 * 4

        for member_name in ("AI Drummer", "AI Guitar Player", "AI Percussion Extras"):
            with self.subTest(member=member_name):
                track = next(track for track in tracks if track.name == member_name)
                counts_by_bar: dict[int, int] = {}
                for note in track.notes:
                    counts_by_bar[note.start // bar_ticks] = counts_by_bar.get(note.start // bar_ticks, 0) + 1

                self.assertGreaterEqual(len(set(counts_by_bar.values())), 2)

    def test_rhythm_section_adds_transition_pickups(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks(
            mode="ehaye",
            preset="southern-blues",
            key="E",
            scale="minor",
            tempo_bpm=86,
        )
        bass = next(track for track in tracks if track.name == "AI Bass Player")
        drums = next(track for track in tracks if track.name == "AI Drummer")
        bass_pickups = [note for note in bass.notes if 340 <= note.start % 480 <= 390]
        drum_pickups = [note for note in drums.notes if note.start % (480 * 4) >= int(3.45 * 480)]

        self.assertGreaterEqual(len(bass_pickups), 8)
        self.assertGreaterEqual(len(drum_pickups), 60)

    def test_generated_lead_and_keys_include_expression_curves(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks()
        lead = next(track for track in tracks if track.name == "AI Lead Player")
        keyboard = next(track for track in tracks if track.name == "AI Keyboard Player")
        lead_expression_events = [event for event in lead.events if event.status == 0xB0 | 3 and event.data[0] == 11]
        keyboard_expression_events = [event for event in keyboard.events if event.status == 0xB0 | 2 and event.data[0] == 11]

        self.assertGreaterEqual(len(lead_expression_events), 100)
        self.assertGreaterEqual(len(keyboard_expression_events), 60)
        self.assertGreaterEqual(len({event.data[1] for event in lead_expression_events}), 8)

    def test_default_generation_has_section_dynamic_contour(self) -> None:
        _ticks_per_beat, _tempo_bpm, tracks = build_tracks()
        bar_ticks = 480 * 4
        chorus_open = range(8 * bar_ticks, 9 * bar_ticks)
        chorus_lift = range(10 * bar_ticks, 12 * bar_ticks)

        def average_velocity(track_name: str, window: range) -> float:
            track = next(track for track in tracks if track.name == track_name)
            velocities = [note.velocity for note in track.notes if note.start in window]
            return sum(velocities) / len(velocities)

        for member_name in ("AI Drummer", "AI Keyboard Player", "AI Lead Player", "AI Percussion Extras"):
            with self.subTest(member=member_name):
                self.assertGreater(average_velocity(member_name, chorus_lift), average_velocity(member_name, chorus_open))

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
        offgrid_starts = [start for start in starts if start % 480 not in {0, 240}]

        self.assertGreaterEqual(len(guitar.notes), 1000)
        self.assertLessEqual(len(guitar.notes), 1400)
        self.assertLessEqual(max(note.velocity for note in guitar.notes), 64)
        self.assertTrue(offgrid_starts)
        self.assertLessEqual(
            max(
                min(min(abs(start % 480 - anchor), 480 - abs(start % 480 - anchor)) for anchor in (0, 240, 360))
                for start in offgrid_starts
            ),
            18,
        )

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

        controls = controls_from_cue(
            LiveCue("live-cue", "keys and lead are stepping on my vocal, leave more room", "bandleader", 0.8, 0, "")
        )
        self.assertTrue(controls.keys_leave_space)
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

    def test_heartland_rock_generates_big_guitar_bass_and_sax_support(self) -> None:
        song = create_default_song(
            preset="heartland-rock",
            key="E",
            scale="major",
            tempo_bpm=118,
        )
        _ticks, _tempo, tracks = build_tracks(
            preset="heartland-rock",
            key="E",
            scale="major",
            tempo_bpm=118,
        )
        drums = next(track for track in tracks if track.name == "AI Drummer")
        bass = next(track for track in tracks if track.name == "AI Bass Player")
        guitar = next(track for track in tracks if track.name == "AI Guitar Player")
        keyboard = next(track for track in tracks if track.name == "AI Keyboard Player")
        lead = next(track for track in tracks if track.name == "AI Lead Player")
        percussion = next(track for track in tracks if track.name == "AI Percussion Extras")
        bar_ticks = 480 * 4
        guitar_pitches = {note.note for note in guitar.notes}
        guitar_low_notes = [note for note in guitar.notes if note.note <= 47]
        guitar_chord_blocks = {}
        for note in guitar.notes:
            guitar_chord_blocks.setdefault(note.start, []).append(note)
        guitar_block_sizes = [len(notes) for notes in guitar_chord_blocks.values()]
        guitar_block_spans = [max(note.start for note in notes) - min(note.start for note in notes) for notes in guitar_chord_blocks.values()]
        guitar_partial_blocks = [count for count in guitar_block_sizes if count in {4, 5}]
        guitar_full_blocks = [count for count in guitar_block_sizes if count == 6]
        keyboard_pitches = {note.note for note in keyboard.notes}
        keyboard_expression_events = [event for event in keyboard.events if event.status == 0xB0 | 2 and event.data[0] == 11]
        keyboard_bend_values = [
            event.data[0] | (event.data[1] << 7)
            for event in keyboard.events
            if event.status == 0xE0 | 2
        ]
        keyboard_bend_targets = {value for value in keyboard_bend_values if value != 8192}
        bass_bend_values = [event.data[0] | (event.data[1] << 7) for event in bass.events]
        bass_bend_targets = {value for value in bass_bend_values if value != 8192}
        bass_main_notes = [note for note in bass.notes if note.duration > 32 and note.velocity >= 60]
        bass_short_articulations = [note for note in bass_main_notes if note.duration <= 180]
        bass_dead_notes = [note for note in bass.notes if note.duration <= 32 and note.velocity < 60]
        lead_grace_notes = [note for note in lead.notes if note.duration <= 44 and note.velocity < 70]
        lead_bend_values = [
            event.data[0] | (event.data[1] << 7)
            for event in lead.events
            if event.status == 0xE0 | 3
        ]
        lead_bend_targets = {value for value in lead_bend_values if value != 8192}
        lead_vibrato_targets = {value for value in lead_bend_targets if abs(value - 8192) <= 180}
        lead_main_notes = [note for note in lead.notes if note.duration > 44]
        lead_pitch_classes = {note.note % 12 for note in lead.notes if note.duration > 44}
        lead_phrase_intervals = [
            abs(lead_main_notes[index + 1].note - lead_main_notes[index].note)
            for index in range(len(lead_main_notes) - 1)
            if lead_main_notes[index + 1].start - lead_main_notes[index].start < bar_ticks
        ]
        bass_pickups = [note for note in bass.notes if 340 <= note.start % 480 <= 380]
        drum_ghost_snares = [note for note in drums.notes if note.note == 38 and note.duration > 32 and note.velocity < 70]
        drum_snare_flams = [
            note for note in drums.notes if note.note == 38 and note.duration <= 32 and 45 <= note.velocity <= 66
        ]
        drum_ghost_durations = {note.duration for note in drum_ghost_snares}
        drum_flam_durations = {note.duration for note in drum_snare_flams}
        drum_tom_notes = {note.note for note in drums.notes}
        drum_starts = [note.start for note in drums.notes]
        bass_starts = [note.start for note in bass.notes if note.duration > 32 or note.velocity >= 60]
        guitar_starts = [note.start for note in guitar.notes]
        keyboard_starts = [note.start for note in keyboard.notes]
        percussion_starts = [note.start for note in percussion.notes if note.duration > 45]
        percussion_counts_by_bar = {}
        for note in percussion.notes:
            percussion_counts_by_bar[note.start // bar_ticks] = percussion_counts_by_bar.get(note.start // bar_ticks, 0) + 1
        percussion_pickups = [note for note in percussion.notes if note.start % bar_ticks > int(3.65 * 480)]
        drum_anchor_offsets = [
            min(min(abs(start % 480 - anchor), 480 - abs(start % 480 - anchor)) for anchor in (0, 120, 240, 360))
            for start in drum_starts
            if start % 480 not in {0, 120, 240, 360}
        ]
        bass_anchor_offsets = [
            min(min(abs(start % 480 - anchor), 480 - abs(start % 480 - anchor)) for anchor in (0, 240, 360))
            for start in bass_starts
            if start % 480 not in {0, 240, 360}
        ]
        guitar_anchor_offsets = [
            min(min(abs(start % 480 - anchor), 480 - abs(start % 480 - anchor)) for anchor in (0, 240, 360))
            for start in guitar_starts
            if start % 480 not in {0, 240, 360}
        ]
        keyboard_anchor_offsets = [
            min(min(abs(start % 480 - anchor), 480 - abs(start % 480 - anchor)) for anchor in (0, 240, 360))
            for start in keyboard_starts
            if start % 480 not in {0, 240, 360}
        ]
        percussion_anchor_offsets = [
            min(min(abs(start % 480 - anchor), 480 - abs(start % 480 - anchor)) for anchor in (0, 240, 360))
            for start in percussion_starts
            if start % 480 not in {0, 240, 360}
        ]
        final_chorus_start = range(72 * bar_ticks, 76 * bar_ticks)
        final_chorus_lift = range(80 * bar_ticks, 84 * bar_ticks)
        heartland_groove = [section_groove_offset(song, local_bar, 8) for local_bar in range(4)]
        lead_chord_tone_hits = []
        for note in lead.notes:
            if note.duration <= 44:
                continue
            note_bar = note.start // bar_ticks
            note_section = next(
                section
                for section in song.sections
                if section.start_bar <= note_bar < section.start_bar + section.bars
            )
            note_chord = note_section.chords[(note_bar - note_section.start_bar) % len(note_section.chords)]
            chord_classes = {tone % 12 for tone in chord_tones(note_chord.root, note_chord.quality, 3)}
            lead_chord_tone_hits.append(note.note % 12 in chord_classes)

        def average_velocity(track, window: range) -> float:
            velocities = [note.velocity for note in track.notes if note.start in window]
            return sum(velocities) / len(velocities)

        self.assertGreater(len(drums.notes), 1000)
        self.assertLessEqual(max(note.velocity for note in drums.notes), 122)
        self.assertGreaterEqual(len(drum_ghost_snares), 120)
        self.assertLessEqual(max(note.velocity for note in drum_ghost_snares), 58)
        self.assertGreaterEqual(len(drum_ghost_durations), 4)
        self.assertGreaterEqual(len(drum_snare_flams), 70)
        self.assertLessEqual(max(note.velocity for note in drum_snare_flams), 66)
        self.assertGreaterEqual(len(drum_flam_durations), 3)
        self.assertIn(43, drum_tom_notes)
        self.assertIn(50, drum_tom_notes)
        self.assertGreater(len(bass.notes), 400)
        self.assertGreaterEqual(len(bass_pickups), 50)
        self.assertLessEqual(max(note.velocity for note in bass_main_notes), 91)
        self.assertGreaterEqual(len(bass_short_articulations), 200)
        self.assertGreaterEqual(len(bass_dead_notes), 80)
        self.assertLessEqual(max(note.velocity for note in bass_dead_notes), 58)
        self.assertGreaterEqual(len(bass.events), 150)
        self.assertGreaterEqual(len(bass_bend_targets), 4)
        self.assertGreater(average_velocity(bass, final_chorus_lift), average_velocity(bass, final_chorus_start))
        self.assertGreaterEqual(len(guitar.notes), 400)
        self.assertLessEqual(len(guitar.notes), 600)
        self.assertLessEqual(min(note.note for note in guitar.notes), 45)
        self.assertGreaterEqual(len(guitar_low_notes), 80)
        self.assertGreaterEqual(len(guitar_chord_blocks), 80)
        self.assertEqual(max(guitar_block_spans), 0)
        self.assertGreaterEqual(len(guitar_partial_blocks), 40)
        self.assertGreaterEqual(len(guitar_full_blocks), 30)
        self.assertGreaterEqual(len(guitar_pitches), 20)
        self.assertGreater(average_velocity(guitar, final_chorus_lift), average_velocity(guitar, final_chorus_start))
        self.assertTrue(drum_anchor_offsets)
        self.assertLessEqual(max(drum_anchor_offsets), 18)
        self.assertTrue(bass_anchor_offsets)
        self.assertLessEqual(max(bass_anchor_offsets), 14)
        self.assertFalse(guitar_anchor_offsets)
        self.assertTrue(all(start % bar_ticks == 0 for start in guitar_chord_blocks))
        self.assertLessEqual(len({note.duration for note in guitar.notes}), 3)
        self.assertEqual(keyboard.program, 66)
        self.assertGreaterEqual(len(keyboard_pitches), 12)
        self.assertGreaterEqual(len(keyboard_expression_events), 300)
        self.assertGreaterEqual(len(keyboard_bend_targets), 4)
        self.assertTrue(keyboard_anchor_offsets)
        self.assertLessEqual(max(keyboard_anchor_offsets), 12)
        self.assertTrue(percussion_anchor_offsets)
        self.assertLessEqual(max(percussion_anchor_offsets), 12)
        self.assertGreaterEqual(len(set(percussion_counts_by_bar.values())), 3)
        self.assertGreaterEqual(len(percussion_pickups), 8)
        self.assertGreater(heartland_groove[0], heartland_groove[1])
        self.assertGreater(heartland_groove[1], heartland_groove[2])
        self.assertGreater(heartland_groove[2], heartland_groove[3])
        self.assertGreaterEqual(len(lead.events), 24)
        self.assertGreaterEqual(len(lead_bend_targets), 6)
        self.assertLessEqual(max(abs(value - 8192) for value in lead_bend_targets), 120)
        self.assertLessEqual(max(note.note for note in lead.notes), 78)
        self.assertLessEqual(len(lead_pitch_classes), 7)
        self.assertTrue(lead_phrase_intervals)
        self.assertLessEqual(max(lead_phrase_intervals), 7)
        self.assertGreaterEqual(max(note.velocity for note in lead_main_notes) - min(note.velocity for note in lead_main_notes), 24)
        self.assertGreaterEqual(sum(lead_chord_tone_hits) / len(lead_chord_tone_hits), 0.80)
        self.assertGreaterEqual(len(lead_vibrato_targets), 4)
        self.assertGreaterEqual(len(lead_grace_notes), 14)


if __name__ == "__main__":
    unittest.main()
