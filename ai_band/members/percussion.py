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

        if song.preset == "heartland-rock":
            if section.energy >= 0.85:
                for beat in (1, 2, 3, 3.5):
                    track.notes.append(
                        MidiNote(song.beat_tick(bar, beat), duration, TAMBOURINE, velocity(44, section.energy), PERC_CHANNEL)
                    )
            elif section.name.startswith("Pre-Chorus"):
                track.notes.append(
                    MidiNote(song.beat_tick(bar, 3.5), duration, TAMBOURINE, velocity(38, section.energy), PERC_CHANNEL)
                )
            continue

        if song.preset == "southern-blues":
            if section.energy >= 0.75:
                for beat in (1, 3):
                    track.notes.append(
                        MidiNote(song.beat_tick(bar, beat), duration, CLAP, velocity(42, section.energy), PERC_CHANNEL)
                    )
                if (bar - section.start_bar) % 2 == 0:
                    track.notes.append(
                        MidiNote(song.beat_tick(bar, 3.5), duration, TAMBOURINE, velocity(46, section.energy), PERC_CHANNEL)
                    )
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
