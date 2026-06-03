from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, phrase_lift, pocket_start, velocity_shift
from ai_band.midi import MidiEvent, MidiNote, MidiTrack
from ai_band.song_state import SongState

BASS_CHANNEL = 0


def generate(song: SongState, simplify: bool = False) -> MidiTrack:
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
        bar_lift = phrase_lift(local_bar, section.bars, 2) if song.preset == "heartland-rock" else 0
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
            base_velocity = 59 if song.preset == "heartland-rock" else 54 if song.preset == "southern-blues" else 60
            accent = 6 if song.preset == "heartland-rock" and beat in {0, 2.0} else 4 if song.preset == "southern-blues" and beat == 0 else 0
            start = song.beat_tick(bar, beat)
            note_duration_ticks = duration
            note_velocity = velocity(base_velocity, section.energy, accent)
            if song.preset == "heartland-rock":
                start = pocket_start(song, bar, beat, 0.55)
                note_duration_ticks = max(note_duration(song, 0.30), duration + _heartland_duration_shift(song, bar, beat))
                note_velocity = clamp_midi(note_velocity + velocity_shift(bar, beat, 5) + bar_lift)
                if _should_add_dead_note(section.energy, local_bar, beat):
                    _add_dead_note(track, song, start, note, section.energy, bar, beat)
            track.notes.append(
                MidiNote(start, note_duration_ticks, note, note_velocity, BASS_CHANNEL)
            )

        if song.preset == "heartland-rock" and not simplify:
            next_chord = bars[bar_index + 1][2] if bar_index + 1 < len(bars) else None
            if next_chord is not None and next_chord.root != chord.root:
                approach = _heartland_approach_note(root, 36 + next_chord.root)
                start = pocket_start(song, bar, 3.75, 0.70)
                duration = note_duration(song, 0.20)
                note_velocity = clamp_midi(velocity(55, section.energy, velocity_shift(bar, 3.75, 4) + bar_lift))
                track.notes.append(MidiNote(start, duration, approach, note_velocity, BASS_CHANNEL))
                _add_heartland_slide(track, start, duration, bar)

    return track


def _heartland_duration_shift(song: SongState, bar: int, beat: float) -> int:
    pattern = (-0.05, 0.02, -0.02, 0.04, -0.03, 0.03)
    index = (bar + int(beat * 2)) % len(pattern)
    return int(song.ticks_per_beat * pattern[index])


def _heartland_approach_note(current_root: int, next_root: int) -> int:
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
