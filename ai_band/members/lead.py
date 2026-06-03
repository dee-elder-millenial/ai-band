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
    durations = (
        note_duration(song, 0.42),
        note_duration(song, 0.35),
        note_duration(song, 0.50),
        note_duration(song, 0.30),
    )

    for section, bar, _chord in iter_section_bars(song):
        should_play = section.name in {"Intro", "Chorus", "Outro"}
        if not should_play:
            continue

        local_bar = bar - section.start_bar
        if section.name == "Intro" and local_bar > 1:
            continue
        if section.name == "Outro" and local_bar % 2 == 1:
            continue

        start_beat = 2 if section.name == "Intro" else 0
        phrase = hook[:4] if section.name == "Outro" else hook
        if section.name == "Chorus" and local_bar % 2 == 1:
            phrase = (0, 2, 4, 5, 4)

        for index, scale_degree in enumerate(phrase):
            beat = start_beat + index * 0.5
            if beat >= song.beats_per_bar:
                break
            note = scale[scale_degree % len(scale)]
            timing_offset = int(song.ticks_per_beat * ((index % 3) - 1) * 0.015)
            note_start = max(song.beat_tick(bar, beat) + timing_offset, song.bar_tick(bar))
            track.notes.append(
                MidiNote(
                    note_start,
                    durations[index % len(durations)],
                    note,
                    velocity(50, section.energy, accent=(index % 4) * 3),
                    LEAD_CHANNEL,
                )
            )

    return track
