from __future__ import annotations

from ai_band.song_state import Chord, Section, SongState
from ai_band.theory import NOTE_NAMES


def chord(symbol: str) -> Chord:
    quality = "major"
    root_name = symbol
    if symbol.endswith("m"):
        quality = "minor"
        root_name = symbol[:-1]
    if symbol.endswith("dim"):
        quality = "dim"
        root_name = symbol[:-3]
    return Chord(symbol=symbol, root=NOTE_NAMES[root_name], quality=quality)


def create_default_song(
    title: str = "First AI Band Sketch",
    style: str = "moody alt-rock",
    tempo_bpm: int = 108,
    key: str = "A",
    scale: str = "minor",
) -> SongState:
    progression = (chord("Am"), chord("F"), chord("C"), chord("G"))
    sections = (
        Section("Intro", 0, 4, 0.35, progression),
        Section("Verse", 4, 4, 0.45, progression),
        Section("Chorus", 8, 4, 0.9, progression),
        Section("Outro", 12, 4, 0.55, progression),
    )
    return SongState(
        title=title,
        style=style,
        tempo_bpm=tempo_bpm,
        key=key,
        scale=scale,
        beats_per_bar=4,
        ticks_per_beat=480,
        sections=sections,
    )

