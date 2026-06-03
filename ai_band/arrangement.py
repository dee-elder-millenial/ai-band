from __future__ import annotations

from collections.abc import Iterator

from ai_band.song_state import Chord, Section, SongState


def iter_section_bars(song: SongState) -> Iterator[tuple[Section, int, Chord]]:
    for section in song.sections:
        for local_bar in range(section.bars):
            chord = section.chords[local_bar % len(section.chords)]
            yield section, section.start_bar + local_bar, chord


def note_duration(song: SongState, beats: float) -> int:
    return int(song.ticks_per_beat * beats)


def velocity(base: int, energy: float, accent: int = 0) -> int:
    return max(1, min(127, int(base + energy * 24 + accent)))

