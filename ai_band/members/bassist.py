from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
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
            base_velocity = 54 if song.preset == "southern-blues" else 60
            accent = 4 if song.preset == "southern-blues" and beat == 0 else 0
            track.notes.append(
                MidiNote(song.beat_tick(bar, beat), duration, note, velocity(base_velocity, section.energy, accent), BASS_CHANNEL)
            )

    return track
