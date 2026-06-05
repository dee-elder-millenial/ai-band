from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, phrase_lift, played_duration, played_start, played_velocity, pocket_start, section_groove_offset, section_lift, support_rest, transition_pickup, velocity_shift
from ai_band.midi import MidiEvent, MidiNote, MidiTrack
from ai_band.song_state import SongState

BASS_CHANNEL = 0


def generate(song: SongState, simplify: bool = False, run_request: bool = False) -> MidiTrack:
    track = MidiTrack("AI Bass Player", channel=BASS_CHANNEL, program=33)
    short = note_duration(song, 0.45)
    long = note_duration(song, 0.9)
    held = note_duration(song, 1.35)
    bars = list(iter_section_bars(song))

    for bar_index, (section, bar, chord) in enumerate(bars):
        root = 36 + chord.root
        fifth = root + 7
        flat_seventh = root + 10
        local_bar = bar - section.start_bar
        bar_lift = phrase_lift(local_bar, section.bars, 2) if song.preset == "heartland-rock" else section_lift(song, local_bar, section.bars, 2)
        groove_offset = section_groove_offset(song, local_bar, section.bars, 0.72)
        if simplify:
            pattern = (
                (0, root, held),
            )
        elif song.preset == "heartland-rock" and section.energy >= 0.85:
            octave = root + 12
            pattern = (
                (0, root, short),
                (0.5, root, short),
                (1.0, fifth, short),
                (1.5, root, short),
                (2.0, octave, short),
                (2.5, root, short),
                (3.0, fifth, short),
                (3.5, flat_seventh, short),
            )
        elif song.preset == "heartland-rock":
            pattern = (
                (0, root, long),
                (1.5, root, short),
                (2.0, fifth, short),
                (2.5, root, short),
                (3.5, fifth, short),
            )
        elif song.preset == "southern-blues" and section.energy >= 0.75:
            pattern = (
                (0, root, long),
                (2.0, fifth, short),
                (2.5, root, short),
                (3.5, flat_seventh, short),
            )
        elif song.preset == "southern-blues":
            pattern = (
                (0, root, held),
                (2.5, fifth, short),
            )
        elif song.preset == "texas-alt-country" and section.energy >= 0.70:
            pattern = (
                (0, root, long),
                (2.0, fifth, short),
                (3.0, root, short),
            )
        elif song.preset == "texas-alt-country":
            pattern = (
                (0, root, held),
                (2.5, fifth, short),
            )
        elif song.preset == "bluesy-alt-country" and section.energy >= 0.75:
            pattern = (
                (0, root, long),
                (2.0, fifth, short),
                (3.0, flat_seventh, short),
            )
        elif song.preset == "bluesy-alt-country":
            pattern = (
                (0, root, held),
                (2.5, fifth, short),
            )
        elif section.energy >= 0.75:
            pattern = (
                (0, root, long),
                (1.5, fifth, short),
                (2.5, root, short),
                (3.5, fifth, short),
            )
        elif local_bar % 2 == 0:
            pattern = (
                (0, root, held),
                (2.5, root, short),
            )
        else:
            pattern = (
                (0, root, held),
            )

        for beat, note, duration in pattern:
            if song.preset != "heartland-rock" and beat not in {0, 2.0} and support_rest(song, "bass", section.energy, local_bar, section.bars, beat):
                continue
            base_velocity = 59 if song.preset == "heartland-rock" else 54 if song.preset == "southern-blues" else 56 if song.preset == "texas-alt-country" else 60
            accent = 6 if song.preset == "heartland-rock" and beat in {0, 2.0} else 4 if song.preset == "southern-blues" and beat == 0 else 0
            start = song.beat_tick(bar, beat)
            note_duration_ticks = duration
            note_velocity = velocity(base_velocity, section.energy, accent)
            if song.preset == "heartland-rock":
                start = max(pocket_start(song, bar, beat, 0.55) + groove_offset, song.bar_tick(bar))
                note_duration_ticks = _heartland_articulated_duration(
                    song,
                    duration + _heartland_duration_shift(song, bar, beat),
                    local_bar,
                    beat,
                )
                note_velocity = min(clamp_midi(note_velocity + velocity_shift(bar, beat, 5) + bar_lift + _heartland_articulation_velocity(local_bar, beat)), 91)
                if _should_add_dead_note(section.energy, local_bar, beat):
                    _add_dead_note(track, song, start, note, section.energy, bar, beat)
            else:
                start = played_start(song, bar, beat, 0.55)
                note_duration_ticks = played_duration(song, duration, bar, beat, 0.45, note_duration(song, 0.20))
                note_velocity = played_velocity(note_velocity + bar_lift, song, bar, beat, 1)
                note_velocity = min(note_velocity, 80 if song.preset == "southern-blues" else 78 if song.preset == "texas-alt-country" else 82)
            track.notes.append(
                MidiNote(start, note_duration_ticks, note, note_velocity, BASS_CHANNEL)
            )

        if not simplify:
            next_chord = bars[bar_index + 1][2] if bar_index + 1 < len(bars) else None
            if song.preset == "heartland-rock" and next_chord is not None and next_chord.root != chord.root:
                approach = _approach_note(root, 36 + next_chord.root)
                start = max(pocket_start(song, bar, 3.75, 0.70) + groove_offset, song.bar_tick(bar))
                duration = note_duration(song, 0.20)
                note_velocity = clamp_midi(velocity(55, section.energy, velocity_shift(bar, 3.75, 4) + bar_lift))
                track.notes.append(MidiNote(start, duration, approach, note_velocity, BASS_CHANNEL))
                _add_heartland_slide(track, start, duration, bar)
            elif (
                next_chord is not None
                and next_chord.root != chord.root
                and transition_pickup(section.energy, local_bar, section.bars)
            ):
                approach = _approach_note(root, 36 + next_chord.root)
                start = played_start(song, bar, 3.75, 0.70)
                duration = played_duration(song, note_duration(song, 0.18), bar, 3.75, 0.50, note_duration(song, 0.10))
                note_velocity = played_velocity(velocity(48, section.energy, 2 + bar_lift), song, bar, 3.75, 2)
                track.notes.append(MidiNote(start, duration, approach, note_velocity, BASS_CHANNEL))
            if run_request and next_chord is not None and _should_add_requested_run(section.name, local_bar, section.bars):
                _add_requested_run(track, song, bar, root, 36 + next_chord.root, section.energy, bar_lift)

    return track


def _should_add_requested_run(section_name: str, local_bar: int, section_bars: int) -> bool:
    in_chorus = section_name.startswith("Chorus") or section_name == "Final Chorus"
    return in_chorus and local_bar % 4 == 3 and local_bar < section_bars - 1


def _add_requested_run(
    track: MidiTrack,
    song: SongState,
    bar: int,
    current_root: int,
    next_root: int,
    energy: float,
    bar_lift: int,
) -> None:
    direction = 1 if next_root >= current_root else -1
    start_note = current_root
    run = (
        start_note,
        start_note + direction * 2,
        start_note + direction * 4,
        _approach_note(current_root, next_root),
    )
    duration = note_duration(song, 0.18)
    for index, note in enumerate(run):
        while note < 35:
            note += 12
        while note > 54:
            note -= 12
        beat = 3.0 + index * 0.25
        start = played_start(song, bar, beat, 0.55)
        note_velocity = min(92, played_velocity(velocity(58, energy, index + bar_lift), song, bar, beat, 2))
        track.notes.append(MidiNote(start, duration, note, note_velocity, BASS_CHANNEL))


def _heartland_duration_shift(song: SongState, bar: int, beat: float) -> int:
    pattern = (-0.05, 0.02, -0.02, 0.04, -0.03, 0.03)
    index = (bar + int(beat * 2)) % len(pattern)
    return int(song.ticks_per_beat * pattern[index])


def _heartland_articulated_duration(song: SongState, duration: int, local_bar: int, beat: float) -> int:
    minimum = note_duration(song, 0.24 if beat in {0.5, 1.5, 2.5, 3.5} else 0.30)
    if beat in {0.5, 1.5, 2.5, 3.5}:
        mute_shape = (-0.16, -0.10, -0.13, -0.08)
        duration += int(song.ticks_per_beat * mute_shape[(local_bar + int(beat * 2)) % len(mute_shape)])
    return max(minimum, duration)


def _heartland_articulation_velocity(local_bar: int, beat: float) -> int:
    if beat in {0.5, 1.5, 2.5, 3.5}:
        return (-5, -3, -4, -2)[(local_bar + int(beat * 2)) % 4]
    return 0


def _approach_note(current_root: int, next_root: int) -> int:
    approach = next_root - 1 if next_root >= current_root else next_root + 1
    while approach < 35:
        approach += 12
    while approach > 52:
        approach -= 12
    return approach


def _should_add_dead_note(energy: float, local_bar: int, beat: float) -> bool:
    if energy < 0.72:
        return False
    return beat in {0.5, 1.5, 2.5, 3.5} and (local_bar + int(beat * 2)) % 3 != 1


def _add_dead_note(track: MidiTrack, song: SongState, start: int, note: int, energy: float, bar: int, beat: float) -> None:
    dead_start = max(start - int(song.ticks_per_beat * 0.070), song.bar_tick(bar))
    if dead_start >= start:
        return
    duration = max(18, int(song.ticks_per_beat * 0.060))
    dead_note = note - 12 if note >= 48 else note
    note_velocity = min(clamp_midi(velocity(28, energy, velocity_shift(bar, beat, 2))), 58)
    track.notes.append(MidiNote(dead_start, duration, dead_note, note_velocity, BASS_CHANNEL))


def _add_heartland_slide(track: MidiTrack, start: int, duration: int, bar: int) -> None:
    amount = (700, 950, 550, 820)[bar % 4]
    direction = -1 if bar % 3 != 1 else 1
    track.events.extend(
        (
            _pitch_bend(start, 8192 + direction * amount),
            _pitch_bend(start + int(duration * 0.48), 8192 + direction * int(amount * 0.35)),
            _pitch_bend(start + int(duration * 0.84), 8192),
        )
    )


def _pitch_bend(tick: int, value: int) -> MidiEvent:
    value = max(0, min(16383, value))
    return MidiEvent(tick=tick, status=0xE0 | BASS_CHANNEL, data=(value & 0x7F, (value >> 7) & 0x7F))
