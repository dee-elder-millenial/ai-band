from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState

PERC_CHANNEL = 9
SHAKER = 82
TAMBOURINE = 54
CLAP = 39


def generate(song: SongState) -> MidiTrack:
    track = MidiTrack("AI Percussion Extras", channel=PERC_CHANNEL)
    duration = note_duration(song, 0.12)

    for section, bar, _chord in iter_section_bars(song):
        if section.energy < 0.5:
            continue

        for sixteenth in range(16):
            beat = sixteenth * 0.25
            track.notes.append(
                MidiNote(song.beat_tick(bar, beat), duration, SHAKER, velocity(28, section.energy), PERC_CHANNEL)
            )

        if section.energy >= 0.75:
            for beat in (1, 3):
                track.notes.append(
                    MidiNote(song.beat_tick(bar, beat), duration, CLAP, velocity(48, section.energy), PERC_CHANNEL)
                )
            track.notes.append(
                MidiNote(song.beat_tick(bar, 3.5), duration, TAMBOURINE, velocity(54, section.energy), PERC_CHANNEL)
            )

    return track

