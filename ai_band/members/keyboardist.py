from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import chord_tones

KEYS_CHANNEL = 2


def generate(song: SongState) -> MidiTrack:
    track = MidiTrack("AI Keyboard Player", channel=KEYS_CHANNEL, program=4)
    pad_duration = note_duration(song, 3.75)

    for section, bar, chord in iter_section_bars(song):
        tones = chord_tones(chord.root, chord.quality, 4)
        voicing = (tones[0], tones[1], tones[2], tones[0] + 12)
        if section.energy >= 0.75:
            voicing = (tones[1], tones[2], tones[0] + 12)

        for note in voicing:
            track.notes.append(
                MidiNote(song.beat_tick(bar, 0), pad_duration, note, velocity(42, section.energy), KEYS_CHANNEL)
            )

    return track

