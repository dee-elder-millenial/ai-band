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

    for section, bar, chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        tones = chord_tones(chord.root, chord.quality, 3)
        voicing = (tones[0], tones[2], tones[0] + 12)
        beats = (0, 2) if section.energy < 0.75 else (0, 1.5, 2.5, 3.5)
        duration = half if section.energy < 0.75 else eighth
        base_velocity = 54

        if song.preset == "southern-blues":
            voicing = (tones[0], tones[1], tones[2])
            beats = (0, 2.5) if section.energy < 0.75 else (0, 2, 3.5)
            duration = note_duration(song, 0.7 if section.energy < 0.75 else 0.38)
            base_velocity = 42
            if section.name.startswith("Verse ") and local_bar % 2 == 1:
                continue

        for beat in beats:
            for note in voicing:
                track.notes.append(
                    MidiNote(song.beat_tick(bar, beat), duration, note, velocity(base_velocity, section.energy), GUITAR_CHANNEL)
                )

    return track
