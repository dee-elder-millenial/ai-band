from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, pocket_start, velocity_shift
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState

DRUM_CHANNEL = 9
KICK = 36
SNARE = 38
CLOSED_HAT = 42
OPEN_HAT = 46
RIDE = 51
CRASH = 49
TOM_LOW = 45
TOM_MID = 47


def generate(song: SongState, bigger: bool = False) -> MidiTrack:
    track = MidiTrack("AI Drummer", channel=DRUM_CHANNEL)
    step = note_duration(song, 0.5)
    hat_duration = note_duration(song, 0.18)

    for section, bar, _chord in iter_section_bars(song):
        energetic = section.energy >= 0.75
        drum_lift = 10 if bigger and section.energy >= 0.75 else 0
        if song.preset == "heartland-rock":
            kick_beats = (0, 2.5) if not energetic else (0, 1.5, 2, 3, 3.5)
            kick_base = 96
            snare_base = 98
            hat_base = 60
        elif song.preset == "southern-blues":
            kick_beats = (0, 2.5) if not energetic else (0, 2, 3, 3.5)
            kick_base = 92
            snare_base = 94
            hat_base = 54
        elif song.preset == "bluesy-alt-country":
            kick_beats = (0, 2.5) if not energetic else (0, 2, 3.5)
            kick_base = 88
            snare_base = 86
            hat_base = 58
        else:
            kick_beats = (0, 2.5) if not energetic else (0, 1.5, 2.5, 3.5)
            kick_base = 88
            snare_base = 86
            hat_base = 58
        snare_beats = (1, 3)

        for eighth in range(8):
            beat = eighth * 0.5
            if song.preset in {"bluesy-alt-country", "southern-blues"} and eighth in {1, 5} and section.energy < 0.75:
                continue
            note = RIDE if song.preset == "heartland-rock" and energetic and eighth % 2 == 0 else OPEN_HAT if energetic and eighth == 7 else CLOSED_HAT
            start = _heartland_drum_start(song, bar, beat, "hat") if song.preset == "heartland-rock" else song.beat_tick(bar, beat)
            note_velocity = velocity(hat_base, section.energy, drum_lift)
            if song.preset == "heartland-rock":
                note_velocity = min(clamp_midi(note_velocity + velocity_shift(bar, beat, 4) + (5 if eighth in {2, 6} else 0)), 122)
            track.notes.append(
                MidiNote(start, hat_duration, note, note_velocity, DRUM_CHANNEL)
            )

        if song.preset in {"heartland-rock", "southern-blues"} and energetic:
            for beat in (0, 1, 2, 3):
                start = _heartland_drum_start(song, bar, beat, "ride") if song.preset == "heartland-rock" else song.beat_tick(bar, beat)
                note_velocity = velocity(54 if song.preset == "heartland-rock" else 48, section.energy)
                if song.preset == "heartland-rock":
                    note_velocity = min(clamp_midi(note_velocity + velocity_shift(bar, beat, 2)), 122)
                track.notes.append(
                    MidiNote(start, hat_duration, RIDE, note_velocity, DRUM_CHANNEL)
                )

        for beat in kick_beats:
            start = _heartland_drum_start(song, bar, beat, "kick") if song.preset == "heartland-rock" else song.beat_tick(bar, beat)
            note_velocity = velocity(kick_base, section.energy, 8 + drum_lift)
            if song.preset == "heartland-rock":
                note_velocity = min(clamp_midi(note_velocity + velocity_shift(bar, beat, 3)), 122)
            track.notes.append(
                MidiNote(start, step, KICK, note_velocity, DRUM_CHANNEL)
            )

        for beat in snare_beats:
            start = _heartland_drum_start(song, bar, beat, "snare") if song.preset == "heartland-rock" else song.beat_tick(bar, beat)
            note_velocity = velocity(snare_base, section.energy, 8 + drum_lift)
            if song.preset == "heartland-rock":
                note_velocity = min(clamp_midi(note_velocity + velocity_shift(bar, beat, 4) + 2), 122)
            track.notes.append(
                MidiNote(start, step, SNARE, note_velocity, DRUM_CHANNEL)
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


def _heartland_drum_start(song: SongState, bar: int, beat: float, part: str) -> int:
    if part == "kick":
        return pocket_start(song, bar, beat, 0.65)
    if part == "snare":
        return pocket_start(song, bar, beat, -0.45) + int(song.ticks_per_beat * 0.018)
    if part == "ride":
        return pocket_start(song, bar, beat, 0.55)
    return pocket_start(song, bar, beat, 0.85)
