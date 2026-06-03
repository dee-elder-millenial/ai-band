from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, phrase_lift, pocket_start, velocity_shift
from ai_band.midi import MidiEvent, MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import scale_notes

LEAD_CHANNEL = 3


def generate(song: SongState, sparse: bool = False) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
    if song.preset == "heartland-rock":
        return _generate_heartland_rock(song, sparse=sparse)
    if song.preset == "southern-blues":
        return _generate_southern_blues(song, sparse=sparse)
    if song.preset == "bluesy-alt-country":
        return _generate_bluesy_alt_country(song, sparse=sparse)

    scale = scale_notes(song.key, song.scale, 5)
    hook = (0, 2, 4, 2, 5, 4, 2, 0)
    if song.preset == "bluesy-alt-country":
        hook = (0, 2, 3, 2, 4, 3, 2, 0)
    durations = (
        note_duration(song, 0.42),
        note_duration(song, 0.35),
        note_duration(song, 0.50),
        note_duration(song, 0.30),
    )

    for section, bar, _chord in iter_section_bars(song):
        should_play = section.name in {"Intro", "Chorus", "Outro"}
        if song.preset == "bluesy-alt-country":
            should_play = section.name in {"Intro", "Chorus"}
        if not should_play:
            continue

        local_bar = bar - section.start_bar
        if section.name == "Intro" and local_bar > 1:
            continue
        if section.name == "Outro" and local_bar % 2 == 1:
            continue
        if sparse and section.name == "Chorus" and local_bar % 2 == 1:
            continue

        start_beat = 2 if section.name == "Intro" else 0
        phrase = hook[:4] if section.name == "Outro" else hook
        if section.name == "Chorus" and local_bar % 2 == 1:
            phrase = (0, 2, 4, 5, 4)
        if sparse:
            phrase = phrase[:4]

        for index, scale_degree in enumerate(phrase):
            beat = start_beat + index * 0.5
            if beat >= song.beats_per_bar:
                break
            note = scale[scale_degree % len(scale)]
            timing_offset = int(song.ticks_per_beat * ((index % 3) - 1) * 0.015)
            note_start = max(song.beat_tick(bar, beat) + timing_offset, song.bar_tick(bar))
            track.notes.append(
                MidiNote(
                    note_start,
                    durations[index % len(durations)],
                    note,
                    velocity(50, section.energy, accent=(index % 4) * 3),
                    LEAD_CHANNEL,
                )
            )

    return track


def _generate_bluesy_alt_country(song: SongState, sparse: bool = False) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
    scale = scale_notes(song.key, song.scale, 5)
    lick_shapes = (
        ((0.05, 2, 0.62, 58, True), (0.95, 3, 0.36, 50, False), (1.55, 2, 0.48, 54, False)),
        ((2.10, 4, 0.40, 60, True), (2.82, 3, 0.34, 48, False)),
        ((0.18, 5, 0.50, 56, False), (0.92, 4, 0.36, 48, True), (1.62, 2, 0.56, 52, False)),
    )

    for section, bar, _chord in iter_section_bars(song):
        if section.name not in {"Intro", "Chorus"}:
            continue
        local_bar = bar - section.start_bar
        if section.name == "Intro" and local_bar not in {1, 3}:
            continue
        if section.name == "Chorus" and local_bar % 2 == 1:
            continue
        if sparse and local_bar % 4 == 2:
            continue

        lick = lick_shapes[local_bar % len(lick_shapes)]
        for index, (beat, degree, beats, base_velocity, bend) in enumerate(lick):
            note = scale[degree % len(scale)]
            drift = int(song.ticks_per_beat * (0.02 * ((index % 2) * 2 - 1)))
            start = max(song.beat_tick(bar, beat) + drift, song.bar_tick(bar))
            duration = note_duration(song, beats)
            track.notes.append(
                MidiNote(
                    start,
                    duration,
                    note,
                    velocity(base_velocity, section.energy, accent=(index % 2) * 4),
                    LEAD_CHANNEL,
                )
            )
            if bend:
                _add_bend(track, start, duration, LEAD_CHANNEL)

    return track


def _generate_southern_blues(song: SongState, sparse: bool = False) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
    scale = scale_notes(song.key, "minor", 5)
    low_scale = scale_notes(song.key, "minor", 4)
    answer_shapes = (
        ((2.05, 2, 0.46, 52, False), (2.78, 4, 0.62, 56, True)),
        ((2.20, 5, 0.52, 58, True), (3.02, 4, 0.36, 50, False), (3.48, 2, 0.34, 50, False)),
        ((2.35, 3, 0.42, 54, False), (3.05, 4, 0.70, 58, True)),
        ((2.12, 2, 0.40, 52, False), (2.72, 0, 0.80, 56, True)),
    )
    solo_shapes = (
        ((0.20, 0, 0.44, 55, True), (0.92, 2, 0.34, 49, False), (1.45, 3, 0.36, 52, False), (2.25, 4, 0.62, 59, True)),
        ((0.55, 5, 0.48, 60, True), (1.28, 4, 0.34, 50, False), (2.10, 2, 0.42, 53, False), (3.02, 0, 0.56, 57, True)),
        ((1.05, 3, 0.40, 55, False), (1.72, 4, 0.58, 58, True), (2.72, 5, 0.36, 57, False)),
        ((0.28, 2, 0.38, 52, False), (1.08, 0, 0.50, 54, True), (2.35, 4, 0.46, 58, True), (3.18, 2, 0.36, 51, False)),
    )

    for section, bar, _chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        section_is_solo = section.name == "Solo"
        section_is_big = section.name.startswith("Chorus") or section.name == "Final Chorus"
        section_is_call = section.name in {"Intro", "Bridge", "Outro"}
        if not section_is_big and not section_is_call and not section_is_solo:
            continue
        if section.name == "Intro" and local_bar not in {1, 3}:
            continue
        if section.name == "Bridge" and local_bar not in {3, 7}:
            continue
        if section.name == "Outro" and local_bar not in {1, 3}:
            continue
        if section_is_solo and local_bar % 3 == 1:
            continue
        if section_is_big and local_bar % 2 == 0:
            continue
        if sparse and local_bar % 4 == 2:
            continue

        lick = solo_shapes[local_bar % len(solo_shapes)] if section_is_solo else answer_shapes[local_bar % len(answer_shapes)]
        note_pool = low_scale if section.name in {"Bridge", "Outro"} else scale
        for index, (beat, degree, beats, base_velocity, bend) in enumerate(lick):
            note = note_pool[degree % len(note_pool)]
            drift = int(song.ticks_per_beat * (0.028 * ((index % 2) * 2 - 1)))
            start = max(song.beat_tick(bar, beat) + drift, song.bar_tick(bar))
            duration = note_duration(song, beats)
            track.notes.append(
                MidiNote(
                    start,
                    duration,
                    note,
                    velocity(base_velocity, section.energy, accent=(index % 2) * 5),
                    LEAD_CHANNEL,
                )
            )
            if bend:
                _add_bend(track, start, duration, LEAD_CHANNEL)

    return track


def _generate_heartland_rock(song: SongState, sparse: bool = False) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
    scale = scale_notes(song.key, "major", 5)
    low_scale = scale_notes(song.key, "major", 4)
    hook_shapes = (
        ((2.00, 4, 0.36, 58, True), (2.55, 5, 0.34, 54, False), (3.10, 4, 0.44, 58, False)),
        ((1.55, 2, 0.38, 56, False), (2.20, 4, 0.42, 60, True), (3.00, 0, 0.52, 57, False)),
        ((2.05, 5, 0.40, 62, True), (2.70, 4, 0.34, 54, False), (3.30, 2, 0.40, 56, False)),
    )
    solo_shapes = (
        ((0.18, 0, 0.34, 58, True), (0.72, 2, 0.30, 54, False), (1.18, 4, 0.34, 60, True), (2.05, 5, 0.46, 63, True), (3.00, 4, 0.34, 57, False)),
        ((0.35, 5, 0.36, 62, True), (0.92, 4, 0.28, 55, False), (1.45, 2, 0.32, 56, False), (2.20, 0, 0.48, 59, True)),
        ((0.15, 2, 0.34, 57, False), (0.72, 4, 0.32, 60, True), (1.35, 5, 0.34, 62, False), (2.40, 7, 0.50, 64, True)),
    )

    for section, bar, _chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        section_is_solo = section.name == "Guitar Solo"
        section_is_hook = section.name in {"Intro", "Outro"} or section.name.startswith("Chorus") or section.name == "Final Chorus"
        if not section_is_solo and not section_is_hook:
            continue
        if section.name == "Intro" and local_bar not in {1, 3}:
            continue
        if section.name == "Outro" and local_bar not in {0, 2, 3}:
            continue
        if section_is_hook and local_bar % 2 == 0 and section.name not in {"Intro", "Outro"}:
            continue
        if sparse and local_bar % 4 == 1:
            continue

        bar_lift = phrase_lift(local_bar, section.bars, 3)
        lick = solo_shapes[local_bar % len(solo_shapes)] if section_is_solo else hook_shapes[local_bar % len(hook_shapes)]
        note_pool = low_scale if section.name == "Outro" else scale
        for index, (beat, degree, beats, base_velocity, bend) in enumerate(lick):
            note = note_pool[degree % len(note_pool)]
            start = _heartland_lead_start(song, bar, beat, index)
            duration = note_duration(song, beats + _heartland_phrase_length(index))
            note_velocity = clamp_midi(velocity(base_velocity, section.energy, accent=(index % 2) * 4) + velocity_shift(bar, beat, 3) + bar_lift)
            track.notes.append(
                MidiNote(
                    start,
                    duration,
                    note,
                    note_velocity,
                    LEAD_CHANNEL,
                )
            )
            if bend:
                _add_bend(track, start, duration, LEAD_CHANNEL, _heartland_bend_profile(bar, index))

    return track


def _heartland_lead_start(song: SongState, bar: int, beat: float, index: int) -> int:
    phrase_drag = 0.012 if index in {0, 3} else -0.006 if index == 1 else 0.004
    return max(pocket_start(song, bar, beat, 0.45) + int(song.ticks_per_beat * phrase_drag), song.bar_tick(bar))


def _heartland_phrase_length(index: int) -> float:
    return (0.04, -0.03, 0.02, 0.05, -0.02)[index % 5]


def _heartland_bend_profile(bar: int, index: int) -> tuple[tuple[float, int], ...]:
    shapes = (
        ((0.14, 1400), (0.34, 2300), (0.58, 2050), (0.82, 0)),
        ((0.20, 1800), (0.44, 2800), (0.68, 2450), (0.86, 0)),
        ((0.16, 1200), (0.36, 2100), (0.62, 1800), (0.78, 0)),
        ((0.22, 2000), (0.48, 3000), (0.70, 2550), (0.88, 0)),
    )
    return shapes[(bar + index) % len(shapes)]


def _add_bend(
    track: MidiTrack,
    start: int,
    duration: int,
    channel: int,
    profile: tuple[tuple[float, int], ...] | None = None,
) -> None:
    if profile is None:
        profile = ((0.18, 1800), (0.38, 2600), (0.78, 0))
    track.events.extend(
        _pitch_bend(start + int(duration * timing), channel, 8192 + amount)
        for timing, amount in profile
    )


def _pitch_bend(tick: int, channel: int, value: int) -> MidiEvent:
    value = max(0, min(16383, value))
    return MidiEvent(tick=tick, status=0xE0 | channel, data=(value & 0x7F, (value >> 7) & 0x7F))
