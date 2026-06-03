from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState

BASS_CHANNEL = 0


def generate(song: SongState) -> MidiTrack:
    track = MidiTrack("AI Bass Player", channel=BASS_CHANNEL, program=33)
    short = note_duration(song, 0.45)
    long = note_duration(song, 0.9)

    for section, bar, chord in iter_section_bars(song):
        root = 36 + chord.root
        fifth = root + 7
        octave = root + 12
        pattern = (
            (0, root, long),
            (1.5, fifth, short),
            (2.5, root, short),
            (3.5, octave if section.energy >= 0.75 else fifth, short),
        )

        for beat, note, duration in pattern:
            track.notes.append(
                MidiNote(song.beat_tick(bar, beat), duration, note, velocity(70, section.energy), BASS_CHANNEL)
            )

    return track

