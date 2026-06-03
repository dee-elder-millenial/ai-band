from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, phrase_lift, pocket_start, velocity_shift
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
        local_bar = bar - section.start_bar
        bar_lift = phrase_lift(local_bar, section.bars, 3) if song.preset == "heartland-rock" else 0

        if song.preset == "heartland-rock":
            if section.energy >= 0.85:
                for beat in _heartland_tambourine_beats(local_bar):
                    start = pocket_start(song, bar, beat, 1.15)
                    note_velocity = clamp_midi(velocity(44, section.energy) + velocity_shift(bar, beat, 5) + bar_lift)
                    track.notes.append(
                        MidiNote(start, duration, TAMBOURINE, note_velocity, PERC_CHANNEL)
                    )
                if local_bar % 4 in {2, 3}:
                    _add_heartland_pickup_shake(track, song, bar, local_bar, section.energy, bar_lift)
            elif section.name.startswith("Pre-Chorus"):
                start = pocket_start(song, bar, 3.5, 1.10)
                note_velocity = clamp_midi(velocity(38, section.energy) + velocity_shift(bar, 3.5, 4) + bar_lift)
                track.notes.append(
                    MidiNote(start, duration, TAMBOURINE, note_velocity, PERC_CHANNEL)
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


def _heartland_tambourine_beats(local_bar: int) -> tuple[float, ...]:
    patterns = (
        (1.0, 2.0, 3.0, 3.5),
        (1.0, 3.0, 3.5),
        (1.0, 2.0, 3.5),
        (2.0, 3.0, 3.5),
        (1.0, 2.0, 3.0),
    )
    return patterns[local_bar % len(patterns)]


def _add_heartland_pickup_shake(
    track: MidiTrack,
    song: SongState,
    bar: int,
    local_bar: int,
    energy: float,
    bar_lift: int,
) -> None:
    duration = note_duration(song, 0.08)
    for beat in (3.70, 3.86) if local_bar % 4 == 3 else (2.86,):
        start = pocket_start(song, bar, beat, 1.25)
        note_velocity = clamp_midi(velocity(34, energy, velocity_shift(bar, beat, 3) + bar_lift))
        track.notes.append(MidiNote(start, duration, TAMBOURINE, note_velocity, PERC_CHANNEL))
