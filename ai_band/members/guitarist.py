from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import chord_tones

GUITAR_CHANNEL = 1


def generate(song: SongState) -> MidiTrack:
    track = MidiTrack("AI Guitar Player", channel=GUITAR_CHANNEL, program=29)
    eighth = note_duration(song, 0.45)
    half = note_duration(song, 1.75)
    strum_gap = max(1, int(song.ticks_per_beat * 0.035))

    for section, bar, chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        tones = chord_tones(chord.root, chord.quality, 3)
        voicing = (tones[0], tones[2], tones[0] + 12)
        beats = (0, 2) if section.energy < 0.75 else (0, 1.5, 2.5, 3.5)
        duration = half if section.energy < 0.75 else eighth
        base_velocity = 54

        if song.preset == "southern-blues":
            voicing = (tones[0], tones[1], tones[2], tones[0] + 12)
            beats = (0, 1.5, 2.5, 3.5) if section.energy < 0.75 else (0, 1.0, 2.0, 2.5, 3.5)
            duration = note_duration(song, 0.62 if section.energy < 0.75 else 0.34)
            base_velocity = 40
            if section.name.startswith("Verse ") and local_bar % 2 == 1:
                beats = (0, 2.5)

        for beat in beats:
            if song.preset == "southern-blues":
                direction = "down" if beat in {0, 2.0, 2.5} else "up"
                _add_strum(track, song, bar, beat, voicing, duration, base_velocity, section.energy, direction, strum_gap)
            else:
                for note in voicing:
                    track.notes.append(
                        MidiNote(song.beat_tick(bar, beat), duration, note, velocity(base_velocity, section.energy), GUITAR_CHANNEL)
                    )

        if song.preset == "southern-blues" and section.energy >= 0.75 and local_bar % 4 == 3:
            _add_strum(
                track,
                song,
                bar,
                3.75,
                (tones[1], tones[2], tones[0] + 12),
                note_duration(song, 0.18),
                38,
                section.energy,
                "up",
                strum_gap,
            )

    return track


def _add_strum(
    track: MidiTrack,
    song: SongState,
    bar: int,
    beat: float,
    voicing: tuple[int, ...],
    duration: int,
    base_velocity: int,
    energy: float,
    direction: str,
    gap: int,
) -> None:
    notes = voicing if direction == "down" else tuple(reversed(voicing))
    start = song.beat_tick(bar, beat)
    for index, note in enumerate(notes):
        track.notes.append(
            MidiNote(start + index * gap, duration, note, velocity(base_velocity, energy, index), GUITAR_CHANNEL)
        )
