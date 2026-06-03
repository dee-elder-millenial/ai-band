from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, pocket_start, velocity_shift
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState

BASS_CHANNEL = 0


def generate(song: SongState, simplify: bool = False) -> MidiTrack:
    track = MidiTrack("AI Bass Player", channel=BASS_CHANNEL, program=33)
    short = note_duration(song, 0.45)
    long = note_duration(song, 0.9)
    held = note_duration(song, 1.35)

    for section, bar, chord in iter_section_bars(song):
        root = 36 + chord.root
        fifth = root + 7
        flat_seventh = root + 10
        local_bar = bar - section.start_bar
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
                note_velocity = clamp_midi(note_velocity + velocity_shift(bar, beat, 5))
            track.notes.append(
                MidiNote(start, note_duration_ticks, note, note_velocity, BASS_CHANNEL)
            )

    return track


def _heartland_duration_shift(song: SongState, bar: int, beat: float) -> int:
    pattern = (-0.05, 0.02, -0.02, 0.04, -0.03, 0.03)
    index = (bar + int(beat * 2)) % len(pattern)
    return int(song.ticks_per_beat * pattern[index])
