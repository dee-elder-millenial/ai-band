from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import chord_tones

GUITAR_CHANNEL = 1


def generate(song: SongState) -> MidiTrack:
    track = MidiTrack("AI Guitar Player", channel=GUITAR_CHANNEL, program=29)
    eighth = note_duration(song, 0.45)
    half = note_duration(song, 1.75)
    strum_gap = max(1, int(song.ticks_per_beat * 0.012))

    for section, bar, chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        tones = chord_tones(chord.root, chord.quality, 3)
        low_tones = chord_tones(chord.root, chord.quality, 2)
        voicing = (tones[0], tones[2], tones[0] + 12)
        beats = (0, 2) if section.energy < 0.75 else (0, 1.5, 2.5, 3.5)
        duration = half if section.energy < 0.75 else eighth
        base_velocity = 54

        if song.preset == "heartland-rock":
            voicing = (low_tones[0], low_tones[2], tones[0], tones[1], tones[2], tones[0] + 12)
            beats = (0, 1.5, 2.5, 3.5) if section.energy < 0.85 else (0, 0.5, 1.5, 2.0, 2.5, 3.5)
            duration = note_duration(song, 0.44 if section.energy < 0.85 else 0.30)
            base_velocity = 50
        elif song.preset == "southern-blues":
            voicing = (tones[0], tones[1], tones[2], tones[0] + 12)
            beats = (0, 1.5, 2.5, 3.5) if section.energy < 0.75 else (0, 1.0, 2.0, 2.5, 3.5)
            duration = note_duration(song, 0.62 if section.energy < 0.75 else 0.34)
            base_velocity = 40
            if section.name.startswith("Verse ") and local_bar % 2 == 1:
                beats = (0, 2.5)

        for beat in beats:
            if song.preset in {"heartland-rock", "southern-blues"}:
                direction = "down" if beat in {0, 2.0, 2.5} else "up"
                anchor_offset = _heartland_anchor_offset(song, bar, beat) if song.preset == "heartland-rock" else 0
                velocity_shift = _heartland_velocity_shift(bar, beat) if song.preset == "heartland-rock" else 0
                string_gap = _heartland_strum_gap(song, bar, beat, strum_gap) if song.preset == "heartland-rock" else strum_gap
                _add_strum(
                    track,
                    song,
                    bar,
                    beat,
                    voicing,
                    duration,
                    base_velocity + velocity_shift,
                    section.energy,
                    direction,
                    string_gap,
                    anchor_offset,
                    _heartland_string_durations(song, bar, beat) if song.preset == "heartland-rock" else None,
                    _heartland_string_velocities(bar, beat) if song.preset == "heartland-rock" else None,
                )
            else:
                for note in voicing:
                    track.notes.append(
                        MidiNote(song.beat_tick(bar, beat), duration, note, velocity(base_velocity, section.energy), GUITAR_CHANNEL)
                    )

        if song.preset in {"heartland-rock", "southern-blues"} and section.energy >= 0.75 and local_bar % 4 == 3:
            _add_strum(
                track,
                song,
                bar,
                3.75,
                (tones[1], tones[2], tones[0] + 12),
                note_duration(song, 0.18),
                46 if song.preset == "heartland-rock" else 38,
                section.energy,
                "up",
                _heartland_strum_gap(song, bar, 3.75, strum_gap) if song.preset == "heartland-rock" else strum_gap,
                _heartland_anchor_offset(song, bar, 3.75) if song.preset == "heartland-rock" else 0,
                _heartland_string_durations(song, bar, 3.75) if song.preset == "heartland-rock" else None,
                _heartland_string_velocities(bar, 3.75) if song.preset == "heartland-rock" else None,
            )

    return track


def _add_strum(
    track: MidiTrack,
    song: SongState,
    bar: int,
    beat: float,
    voicing: tuple[int, ...],
    duration: int,
    base_velocity: int,
    energy: float,
    direction: str,
    gap: int,
    anchor_offset: int = 0,
    duration_offsets: tuple[int, ...] | None = None,
    velocity_offsets: tuple[int, ...] | None = None,
) -> None:
    notes = voicing if direction == "down" else tuple(reversed(voicing))
    start = max(song.beat_tick(bar, beat) + anchor_offset, song.bar_tick(bar))
    for index, note in enumerate(notes):
        note_duration_ticks = duration
        if duration_offsets:
            note_duration_ticks = max(gap * 3, duration + duration_offsets[index % len(duration_offsets)])
        note_velocity = velocity(base_velocity, energy, index)
        if velocity_offsets:
            note_velocity = clamp_midi(note_velocity + velocity_offsets[index % len(velocity_offsets)])
        track.notes.append(
            MidiNote(start + index * gap, note_duration_ticks, note, note_velocity, GUITAR_CHANNEL)
        )


def _heartland_anchor_offset(song: SongState, bar: int, beat: float) -> int:
    pattern = (-0.010, 0.000, 0.006, -0.004)
    index = (bar * 4 + int(beat * 2)) % len(pattern)
    return int(song.ticks_per_beat * pattern[index])


def _heartland_velocity_shift(bar: int, beat: float) -> int:
    pattern = (0, -4, 3, -2, 2, -3)
    index = (bar + int(beat * 2)) % len(pattern)
    return pattern[index]


def _heartland_strum_gap(song: SongState, bar: int, beat: float, base_gap: int) -> int:
    pattern = (0.010, 0.015, 0.012, 0.018, 0.011, 0.016)
    index = (bar * 3 + int(beat * 4)) % len(pattern)
    return max(base_gap, int(song.ticks_per_beat * pattern[index]))


def _heartland_string_durations(song: SongState, bar: int, beat: float) -> tuple[int, ...]:
    patterns = (
        (0.03, -0.02, 0.01, -0.03, 0.02, -0.01),
        (-0.02, 0.02, -0.01, 0.03, -0.03, 0.01),
        (0.01, -0.03, 0.03, -0.01, 0.02, -0.02),
    )
    pattern = patterns[(bar + int(beat * 2)) % len(patterns)]
    return tuple(int(song.ticks_per_beat * amount) for amount in pattern)


def _heartland_string_velocities(bar: int, beat: float) -> tuple[int, ...]:
    patterns = (
        (2, -1, 0, -2, 1, -3),
        (-1, 1, -2, 2, -1, 0),
        (0, -2, 2, -1, 1, -2),
    )
    return patterns[(bar + int(beat * 2)) % len(patterns)]
