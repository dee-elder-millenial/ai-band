from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState

DRUM_CHANNEL = 9
KICK = 36
SNARE = 38
CLOSED_HAT = 42
OPEN_HAT = 46
CRASH = 49
TOM_LOW = 45
TOM_MID = 47


def generate(song: SongState) -> MidiTrack:
    track = MidiTrack("AI Drummer", channel=DRUM_CHANNEL)
    step = note_duration(song, 0.5)
    hat_duration = note_duration(song, 0.18)

    for section, bar, _chord in iter_section_bars(song):
        energetic = section.energy >= 0.75
        kick_beats = (0, 2.5) if not energetic else (0, 1.5, 2.5, 3.5)
        snare_beats = (1, 3)

        for eighth in range(8):
            beat = eighth * 0.5
            note = OPEN_HAT if energetic and eighth == 7 else CLOSED_HAT
            track.notes.append(
                MidiNote(song.beat_tick(bar, beat), hat_duration, note, velocity(58, section.energy), DRUM_CHANNEL)
            )

        for beat in kick_beats:
            track.notes.append(
                MidiNote(song.beat_tick(bar, beat), step, KICK, velocity(88, section.energy, 8), DRUM_CHANNEL)
            )

        for beat in snare_beats:
            track.notes.append(
                MidiNote(song.beat_tick(bar, beat), step, SNARE, velocity(86, section.energy, 6), DRUM_CHANNEL)
            )

        if bar == section.start_bar:
            track.notes.append(
                MidiNote(song.beat_tick(bar, 0), note_duration(song, 1), CRASH, velocity(94, section.energy), DRUM_CHANNEL)
            )

        if bar == section.start_bar + section.bars - 1:
            fill_start = song.beat_tick(bar, 3)
            for index, note in enumerate((TOM_MID, TOM_LOW, SNARE, CRASH)):
                track.notes.append(
                    MidiNote(fill_start + index * int(step / 2), int(step / 2), note, velocity(82, section.energy), DRUM_CHANNEL)
                )

    return track
