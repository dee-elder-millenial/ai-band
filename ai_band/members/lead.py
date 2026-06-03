from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.midi import MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import scale_notes

LEAD_CHANNEL = 3


def generate(song: SongState) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
    scale = scale_notes(song.key, song.scale, 5)
    hook = (0, 2, 4, 2, 5, 4, 2, 0)
    step = note_duration(song, 0.45)

    for section, bar, _chord in iter_section_bars(song):
        should_play = section.name in {"Intro", "Chorus", "Outro"}
        if not should_play:
            continue

        start_beat = 2 if section.name == "Intro" else 0
        for index, scale_degree in enumerate(hook[:4] if section.name == "Outro" else hook):
            beat = start_beat + index * 0.5
            if beat >= song.beats_per_bar:
                break
            note = scale[scale_degree % len(scale)]
            track.notes.append(
                MidiNote(song.beat_tick(bar, beat), step, note, velocity(58, section.energy), LEAD_CHANNEL)
            )

    return track

