from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_band.controls import controls_from_cue
from ai_band.generate import build_tracks, tempo_events_for_preset
from ai_band.live_cue import LiveCue
from ai_band.midi import _event_order, write_midi
from ai_band.midi_read import read_midi_summary


class MidiOutputTests(unittest.TestCase):
    def test_midi_writer_orders_same_tick_setup_events_before_note_ons(self) -> None:
        note_off = bytes([0x80, 60, 0])
        expression = bytes([0xB0, 11, 90])
        pitch_bend = bytes([0xE0, 0, 64])
        note_on = bytes([0x90, 60, 96])

        self.assertLess(_event_order(note_off), _event_order(expression))
        self.assertLess(_event_order(expression), _event_order(note_on))
        self.assertLess(_event_order(pitch_bend), _event_order(note_on))

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

    def test_generated_midi_includes_live_cue_marker_text(self) -> None:
        controls = controls_from_cue(LiveCue("live-cue", "simplify bass", "bandleader", 0.5, 12, ""))
        ticks_per_beat, tempo_bpm, tracks = build_tracks(mode="ehaye", controls=controls)

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "cue.mid"
            write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)
            summary = read_midi_summary(output)

        self.assertIn("Live cue applied", " ".join(summary.tracks[1].text))

    def test_bluesy_alt_country_midi_contains_lead_pitch_bends(self) -> None:
        ticks_per_beat, tempo_bpm, tracks = build_tracks(
            mode="ehaye",
            preset="bluesy-alt-country",
            key="D",
            scale="major",
            tempo_bpm=96,
        )

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "county.mid"
            write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)
            summary = read_midi_summary(output)

        lead_track = next(track for track in summary.tracks if track.name == "AI Lead Player")
        self.assertGreater(lead_track.pitch_bend_count, 0)

    def test_southern_blues_midi_contains_long_form_markers(self) -> None:
        ticks_per_beat, tempo_bpm, tracks = build_tracks(
            mode="ehaye",
            preset="southern-blues",
            key="E",
            scale="minor",
            tempo_bpm=86,
        )

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "southern.mid"
            write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)
            summary = read_midi_summary(output)

        bandleader = summary.tracks[1]
        self.assertIn("Final Chorus", bandleader.markers)
        self.assertIn("Southern blues preset", " ".join(bandleader.text))

    def test_heartland_midi_can_include_human_tempo_map(self) -> None:
        ticks_per_beat, tempo_bpm, tracks = build_tracks(
            preset="heartland-rock",
            key="E",
            scale="major",
            tempo_bpm=118,
        )
        tempo_events = tempo_events_for_preset("heartland-rock", tempo_bpm, ticks_per_beat, total_bars=88)

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "heartland.mid"
            write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm, tempo_events=tempo_events)
            data = output.read_bytes()

        self.assertGreaterEqual(len(tempo_events), 8)
        self.assertGreater(data.count(b"\xff\x51\x03"), 1)
        self.assertIn(117, [bpm for _tick, bpm in tempo_events])
        self.assertIn(119, [bpm for _tick, bpm in tempo_events])


if __name__ == "__main__":
    unittest.main()
