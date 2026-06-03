from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import chord_tones

KEYS_CHANNEL = 2


def generate(song: SongState, leave_space: bool = False) -> MidiTrack:
    track = MidiTrack("AI Keyboard Player", channel=KEYS_CHANNEL, program=4)

    for section, bar, chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        is_verse = section.name == "Verse" or section.name.startswith("Verse ")
        if leave_space and local_bar % 2 == 1:
            continue
        if section.name in {"Intro", "Outro"} or is_verse:
            if local_bar % 2 == 1:
                continue

        if song.preset == "southern-blues" and section.name == "Bridge" and local_bar % 2 == 1:
            continue

        tones = chord_tones(chord.root, chord.quality, 4)
        voicing = (tones[1], tones[2])
        beats = (2.0,)
        duration = note_duration(song, 1.6)
        if song.preset == "southern-blues":
            voicing = (tones[0], tones[2])
            beats = (2.75,)
            duration = note_duration(song, 0.9)
        elif song.preset == "bluesy-alt-country":
            voicing = (tones[0], tones[1])
            beats = (2.5,)
            duration = note_duration(song, 1.0)

        if section.energy >= 0.75:
            voicing = (tones[1], tones[2] + 12)
            beats = (1.5, 3.0)
            duration = note_duration(song, 0.45)
            if song.preset == "southern-blues":
                voicing = (tones[1], tones[2])
                beats = (3.0,)
                duration = note_duration(song, 0.55)
                if section.name in {"Solo", "Final Chorus"}:
                    beats = (1.0, 3.0)
            elif song.preset == "bluesy-alt-country":
                voicing = (tones[0], tones[2])
                beats = (1.0, 3.0)
                duration = note_duration(song, 0.55)
        if leave_space:
            beats = (beats[0],)
            duration = min(duration, note_duration(song, 0.8))

        for beat in beats:
            for note in voicing:
                track.notes.append(
                    MidiNote(song.beat_tick(bar, beat), duration, note, velocity(32, section.energy), KEYS_CHANNEL)
                )

    return track
