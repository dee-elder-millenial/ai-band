from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.midi import MidiEvent, MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import scale_notes

LEAD_CHANNEL = 3


def generate(song: SongState, sparse: bool = False) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
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


def _add_bend(track: MidiTrack, start: int, duration: int, channel: int) -> None:
    track.events.extend(
        (
            _pitch_bend(start + int(duration * 0.18), channel, 8192 + 1800),
            _pitch_bend(start + int(duration * 0.38), channel, 8192 + 2600),
            _pitch_bend(start + int(duration * 0.78), channel, 8192),
        )
    )


def _pitch_bend(tick: int, channel: int, value: int) -> MidiEvent:
    value = max(0, min(16383, value))
    return MidiEvent(tick=tick, status=0xE0 | channel, data=(value & 0x7F, (value >> 7) & 0x7F))
