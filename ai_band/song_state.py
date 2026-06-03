from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chord:
    symbol: str
    root: int
    quality: str


@dataclass(frozen=True)
class Section:
    name: str
    start_bar: int
    bars: int
    energy: float
    chords: tuple[Chord, ...]


@dataclass(frozen=True)
class SongState:
    title: str
    style: str
    tempo_bpm: int
    key: str
    scale: str
    beats_per_bar: int
    ticks_per_beat: int
    sections: tuple[Section, ...]

    @property
    def total_bars(self) -> int:
        return max(section.start_bar + section.bars for section in self.sections)

    def bar_tick(self, bar: int) -> int:
        return bar * self.beats_per_bar * self.ticks_per_beat

    def beat_tick(self, bar: int, beat: float) -> int:
        return self.bar_tick(bar) + int(beat * self.ticks_per_beat)

