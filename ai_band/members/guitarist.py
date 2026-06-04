from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, phrase_lift, played_duration, played_start, played_velocity, section_groove_offset, section_lift, support_rest
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import chord_tones

GUITAR_CHANNEL = 1


def generate(song: SongState, profile: str = "auto") -> MidiTrack:
    track = MidiTrack("AI Guitar Player", channel=GUITAR_CHANNEL, program=29)
    eighth = note_duration(song, 0.45)
    half = note_duration(song, 1.75)
    strum_gap = max(1, int(song.ticks_per_beat * 0.012))

    for section, bar, chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        tones = chord_tones(chord.root, chord.quality, 3)
        low_tones = chord_tones(chord.root, chord.quality, 2)
        bar_lift = phrase_lift(local_bar, section.bars, 3) if song.preset == "heartland-rock" else section_lift(song, local_bar, section.bars, 1)
        groove_offset = section_groove_offset(song, local_bar, section.bars, 0.65)
        voicing = (tones[0], tones[2], tones[0] + 12)
        beats = (0, 2) if section.energy < 0.75 else (0, 1.5, 2.5, 3.5)
        duration = half if section.energy < 0.75 else eighth
        base_velocity = 54

        if song.preset == "heartland-rock":
            voicing = (low_tones[0], low_tones[2], tones[0], tones[1], tones[2], tones[0] + 12)
            if profile in {"auto", "ample-strummer"}:
                strummer_voicing = _heartland_strummer_voicing(voicing, tones, local_bar, section.energy)
                _add_heartland_strummer_chord(track, song, bar, local_bar, strummer_voicing, section.energy, groove_offset, bar_lift)
                continue
            if profile == "simple-blocks":
                _add_heartland_strummer_chord(
                    track,
                    song,
                    bar,
                    local_bar,
                    _heartland_simple_block_voicing(tones, local_bar, section.energy),
                    section.energy,
                    groove_offset,
                    bar_lift,
                )
                continue
        elif song.preset == "southern-blues":
            voicing = (tones[0], tones[1], tones[2], tones[0] + 12)
            beats = (0, 1.5, 2.5, 3.5) if section.energy < 0.75 else (0, 1.0, 2.0, 2.5, 3.5)
            duration = note_duration(song, 0.62 if section.energy < 0.75 else 0.34)
            base_velocity = 40
            if section.name.startswith("Verse ") and local_bar % 2 == 1:
                beats = (0, 2.5)

        for beat in beats:
            if beat not in {0, 2.0} and support_rest(song, "guitar", section.energy, local_bar, section.bars, beat):
                continue
            if song.preset in {"heartland-rock", "southern-blues"}:
                direction = "down" if beat in {0, 2.0, 2.5} else "up"
                anchor_offset = (
                    _heartland_anchor_offset(song, bar, beat) + groove_offset
                    if song.preset == "heartland-rock"
                    else played_start(song, bar, beat, 0.55) - song.beat_tick(bar, beat)
                )
                velocity_shift = _heartland_velocity_shift(bar, beat) if song.preset == "heartland-rock" else 0
                string_gap = _heartland_strum_gap(song, bar, beat, strum_gap) if song.preset == "heartland-rock" else strum_gap
                strum_voicing = _heartland_color_voicing(voicing, tones, local_bar, beat) if song.preset == "heartland-rock" else voicing
                if song.preset == "heartland-rock":
                    strum_voicing = _heartland_string_group(strum_voicing, direction, local_bar, beat)
                if song.preset == "heartland-rock" and _should_add_heartland_rake(section.energy, local_bar, beat, direction):
                    _add_heartland_rake(track, song, bar, beat, strum_voicing, section.energy, anchor_offset)
                _add_strum(
                    track,
                    song,
                    bar,
                    beat,
                    strum_voicing,
                    duration,
                    base_velocity + velocity_shift + bar_lift,
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
                        MidiNote(
                            played_start(song, bar, beat, 0.55),
                            played_duration(song, duration, bar, beat, 0.50, note_duration(song, 0.25)),
                            note,
                            played_velocity(velocity(base_velocity, section.energy, bar_lift), song, bar, beat, 2),
                            GUITAR_CHANNEL,
                        )
                    )

        if song.preset in {"heartland-rock", "southern-blues"} and section.energy >= 0.75 and local_bar % 4 == 3:
            _add_strum(
                track,
                song,
                bar,
                3.75,
                _heartland_fill_voicing(tones, local_bar) if song.preset == "heartland-rock" else (tones[1], tones[2], tones[0] + 12),
                note_duration(song, 0.18),
                (46 + bar_lift) if song.preset == "heartland-rock" else 38 + bar_lift,
                section.energy,
                "up",
                _heartland_strum_gap(song, bar, 3.75, strum_gap) if song.preset == "heartland-rock" else strum_gap,
                (
                    _heartland_anchor_offset(song, bar, 3.75)
                    + groove_offset
                    if song.preset == "heartland-rock"
                    else played_start(song, bar, 3.75, 0.55) - song.beat_tick(bar, 3.75)
                ),
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


def _should_add_heartland_rake(energy: float, local_bar: int, beat: float, direction: str) -> bool:
    if energy < 0.78 or direction != "down":
        return False
    return beat in {0, 2.0, 2.5} and (local_bar + int(beat * 2)) % 4 in {0, 3}


def _add_heartland_rake(
    track: MidiTrack,
    song: SongState,
    bar: int,
    beat: float,
    voicing: tuple[int, ...],
    energy: float,
    anchor_offset: int,
) -> None:
    rake_start = max(song.beat_tick(bar, beat) + anchor_offset - int(song.ticks_per_beat * 0.055), song.bar_tick(bar))
    gap = max(1, int(song.ticks_per_beat * 0.010))
    duration = max(16, int(song.ticks_per_beat * 0.045))
    rake_notes = voicing[:3]
    for index, note in enumerate(rake_notes):
        note_velocity = min(clamp_midi(velocity(26, energy, index + _heartland_velocity_shift(bar, beat))), 58)
        track.notes.append(MidiNote(rake_start + index * gap, duration, note, note_velocity, GUITAR_CHANNEL))


def _add_heartland_strummer_chord(
    track: MidiTrack,
    song: SongState,
    bar: int,
    local_bar: int,
    voicing: tuple[int, ...],
    energy: float,
    groove_offset: int,
    bar_lift: int,
) -> None:
    start = max(song.bar_tick(bar) + groove_offset + _heartland_anchor_offset(song, bar, 0), song.bar_tick(bar))
    next_bar = song.bar_tick(bar + 1)
    duration = max(note_duration(song, 2.75), next_bar - start - note_duration(song, 0.08))
    base_velocity = 48 + int(energy * 18) + bar_lift + _heartland_velocity_shift(bar, 0)
    velocity_offsets = (0, -2, 1, -1, 2, -2)
    for index, note in enumerate(voicing):
        track.notes.append(
            MidiNote(
                start,
                duration,
                note,
                clamp_midi(base_velocity + velocity_offsets[index % len(velocity_offsets)]),
                GUITAR_CHANNEL,
            )
        )


def _heartland_strummer_voicing(
    voicing: tuple[int, ...],
    tones: tuple[int, int, int],
    local_bar: int,
    energy: float,
) -> tuple[int, ...]:
    colored = _heartland_color_voicing(voicing, tones, local_bar, 2.0)
    if energy < 0.78:
        return colored[1:5]
    if local_bar % 4 == 2:
        return colored[:5]
    return colored


def _heartland_simple_block_voicing(
    tones: tuple[int, int, int],
    local_bar: int,
    energy: float,
) -> tuple[int, ...]:
    root, third, fifth = tones
    if energy < 0.78:
        return (root, third, fifth)
    if local_bar % 4 == 2:
        return (root, third, fifth, root + 12)
    return (root - 12, root, third, fifth, root + 12)


def _heartland_color_voicing(
    voicing: tuple[int, ...],
    tones: tuple[int, int, int],
    local_bar: int,
    beat: float,
) -> tuple[int, ...]:
    root, third, fifth = tones
    second = root + 2
    fourth = root + 5
    sixth = root + 9
    shape = (local_bar + int(beat * 2)) % 8
    if shape == 1 and beat >= 1.0:
        return (voicing[0], voicing[1], root, fourth, fifth, root + 12)
    if shape == 4 and beat >= 2.0:
        return (voicing[0], voicing[1], root, third, sixth, root + 12)
    if shape == 6 and beat >= 2.5:
        return (voicing[0], voicing[1], second, third, fifth, root + 12)
    return voicing


def _heartland_string_group(voicing: tuple[int, ...], direction: str, local_bar: int, beat: float) -> tuple[int, ...]:
    if len(voicing) < 6:
        return voicing
    shape = (local_bar + int(beat * 4)) % 6
    if direction == "up":
        if shape in {0, 3}:
            return voicing[2:]
        return voicing[1:]
    if beat in {0, 2.0}:
        return voicing
    if shape in {2, 5}:
        return voicing[:5]
    return voicing


def _heartland_fill_voicing(tones: tuple[int, int, int], local_bar: int) -> tuple[int, ...]:
    root, third, fifth = tones
    if local_bar % 8 in {3, 7}:
        return (root + 2, third, fifth, root + 12)
    return (third, fifth, root + 12)
