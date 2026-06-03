from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, phrase_lift, played_start, played_velocity, pocket_start, support_rest, velocity_shift
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState

DRUM_CHANNEL = 9
KICK = 36
SNARE = 38
CLOSED_HAT = 42
OPEN_HAT = 46
RIDE = 51
CRASH = 49
TOM_HIGH = 50
TOM_LOW = 45
TOM_MID = 47
TOM_FLOOR = 43


def generate(song: SongState, bigger: bool = False) -> MidiTrack:
    track = MidiTrack("AI Drummer", channel=DRUM_CHANNEL)
    step = note_duration(song, 0.5)
    hat_duration = note_duration(song, 0.18)

    for section, bar, _chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        bar_lift = phrase_lift(local_bar, section.bars, 4) if song.preset == "heartland-rock" else 0
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
            if eighth not in {0, 2, 4, 6} and support_rest(song, "hat", section.energy, local_bar, section.bars, beat):
                continue
            note = RIDE if song.preset == "heartland-rock" and energetic and eighth % 2 == 0 else OPEN_HAT if energetic and eighth == 7 else CLOSED_HAT
            start = _heartland_drum_start(song, bar, beat, "hat") if song.preset == "heartland-rock" else played_start(song, bar, beat, 0.70)
            note_velocity = velocity(hat_base, section.energy, drum_lift)
            if song.preset == "heartland-rock":
                note_velocity = min(clamp_midi(note_velocity + velocity_shift(bar, beat, 4) + bar_lift + (5 if eighth in {2, 6} else 0)), 122)
            else:
                note_velocity = played_velocity(note_velocity, song, bar, beat, 2)
            track.notes.append(
                MidiNote(start, hat_duration, note, note_velocity, DRUM_CHANNEL)
            )

        if song.preset in {"heartland-rock", "southern-blues"} and energetic:
            for beat in (0, 1, 2, 3):
                start = _heartland_drum_start(song, bar, beat, "ride") if song.preset == "heartland-rock" else played_start(song, bar, beat, 0.65)
                note_velocity = velocity(54 if song.preset == "heartland-rock" else 48, section.energy)
                if song.preset == "heartland-rock":
                    note_velocity = min(clamp_midi(note_velocity + velocity_shift(bar, beat, 2) + bar_lift), 122)
                else:
                    note_velocity = played_velocity(note_velocity, song, bar, beat, 1)
                track.notes.append(
                    MidiNote(start, hat_duration, RIDE, note_velocity, DRUM_CHANNEL)
                )

        for beat in kick_beats:
            start = _heartland_drum_start(song, bar, beat, "kick") if song.preset == "heartland-rock" else played_start(song, bar, beat, 0.55)
            note_velocity = velocity(kick_base, section.energy, 8 + drum_lift)
            if song.preset == "heartland-rock":
                note_velocity = min(clamp_midi(note_velocity + velocity_shift(bar, beat, 3) + bar_lift), 122)
            else:
                note_velocity = played_velocity(note_velocity, song, bar, beat, 1)
            track.notes.append(
                MidiNote(start, step, KICK, note_velocity, DRUM_CHANNEL)
            )

        for beat in snare_beats:
            start = _heartland_drum_start(song, bar, beat, "snare") if song.preset == "heartland-rock" else played_start(song, bar, beat, -0.35)
            note_velocity = velocity(snare_base, section.energy, 8 + drum_lift)
            if song.preset == "heartland-rock":
                note_velocity = min(clamp_midi(note_velocity + velocity_shift(bar, beat, 4) + bar_lift + 2), 122)
                if _should_add_heartland_flam(section.energy, local_bar, beat):
                    _add_heartland_flam(track, song, start, section.energy, bar, beat, bar_lift)
            else:
                note_velocity = played_velocity(note_velocity, song, bar, beat, 1)
            track.notes.append(
                MidiNote(start, step, SNARE, note_velocity, DRUM_CHANNEL)
            )

        if song.preset == "heartland-rock":
            _add_heartland_ghosts(track, song, bar, local_bar, section.energy, bar_lift)

        if bar == section.start_bar:
            crash_start = _heartland_drum_start(song, bar, 0, "crash") if song.preset == "heartland-rock" else played_start(song, bar, 0, 0.55)
            crash_velocity = velocity(94, section.energy)
            if song.preset == "heartland-rock":
                crash_velocity = min(clamp_midi(crash_velocity + velocity_shift(bar, 0, 3) + bar_lift), 120)
            else:
                crash_velocity = played_velocity(crash_velocity, song, bar, 0, 1)
            track.notes.append(
                MidiNote(crash_start, note_duration(song, 1), CRASH, crash_velocity, DRUM_CHANNEL)
            )

        if bar == section.start_bar + section.bars - 1:
            if song.preset == "heartland-rock":
                _add_heartland_fill(track, song, bar, section.energy, step)
            else:
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
    if part == "crash":
        return pocket_start(song, bar, beat, 0.40)
    if part == "ride":
        return pocket_start(song, bar, beat, 0.55)
    return pocket_start(song, bar, beat, 0.85)


def _should_add_heartland_flam(energy: float, local_bar: int, beat: float) -> bool:
    if energy < 0.78:
        return False
    return beat == 3 or local_bar % 4 in {1, 3}


def _add_heartland_flam(
    track: MidiTrack,
    song: SongState,
    snare_start: int,
    energy: float,
    bar: int,
    beat: float,
    bar_lift: int,
) -> None:
    flam_gap = int(song.ticks_per_beat * (0.030 + 0.006 * ((bar + int(beat)) % 3)))
    flam_start = max(snare_start - flam_gap, song.bar_tick(bar))
    if flam_start >= snare_start:
        return
    duration = max(18, int(song.ticks_per_beat * 0.055))
    note_velocity = min(clamp_midi(velocity(35, energy, velocity_shift(bar, beat, 2) + bar_lift)), 66)
    track.notes.append(MidiNote(flam_start, duration, SNARE, note_velocity, DRUM_CHANNEL))


def _add_heartland_fill(track: MidiTrack, song: SongState, bar: int, energy: float, step: int) -> None:
    shapes = (
        ((2.5, SNARE, 0.20, -8), (2.75, TOM_HIGH, 0.18, -6), (3.0, TOM_MID, 0.20, -4), (3.25, TOM_LOW, 0.22, -2), (3.5, CRASH, 0.45, 4)),
        ((3.0, TOM_HIGH, 0.16, -5), (3.20, TOM_MID, 0.16, -3), (3.40, TOM_LOW, 0.18, -1), (3.62, SNARE, 0.16, -4), (3.78, CRASH, 0.35, 3)),
        ((2.75, SNARE, 0.18, -7), (3.0, SNARE, 0.14, -10), (3.25, TOM_MID, 0.18, -4), (3.5, TOM_FLOOR, 0.24, 0), (3.75, CRASH, 0.38, 2)),
        ((2.5, TOM_MID, 0.18, -7), (2.75, TOM_LOW, 0.18, -5), (3.0, SNARE, 0.16, -6), (3.25, TOM_HIGH, 0.16, -3), (3.5, TOM_FLOOR, 0.22, 1), (3.75, CRASH, 0.36, 4)),
    )
    shape = shapes[bar % len(shapes)]
    for beat, note, beats, accent in shape:
        duration = max(int(step * 0.25), note_duration(song, beats))
        start = _heartland_drum_start(song, bar, beat, "fill")
        note_velocity = min(clamp_midi(velocity(82, energy, accent) + velocity_shift(bar, beat, 3)), 122)
        track.notes.append(MidiNote(start, duration, note, note_velocity, DRUM_CHANNEL))


def _add_heartland_ghosts(
    track: MidiTrack,
    song: SongState,
    bar: int,
    local_bar: int,
    energy: float,
    bar_lift: int,
) -> None:
    shapes = (
        ((0.75, -4), (2.75, -2)),
        ((1.75, -6), (2.75, -3), (3.25, -5)),
        ((0.75, -5), (2.25, -7)),
        ((1.75, -4), (2.75, -6)),
    )
    if energy < 0.70 and local_bar % 2 == 1:
        return
    duration = note_duration(song, 0.11)
    for beat, accent in shapes[local_bar % len(shapes)]:
        start = _heartland_drum_start(song, bar, beat, "ghost")
        note_velocity = min(clamp_midi(velocity(24, energy, accent) + velocity_shift(bar, beat, 2) + bar_lift), 58)
        track.notes.append(MidiNote(start, duration, SNARE, note_velocity, DRUM_CHANNEL))
