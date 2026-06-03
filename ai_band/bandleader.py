from __future__ import annotations

from ai_band.song_state import Chord, Section, SongState
from ai_band.theory import NOTE_NAMES

NOTE_SYMBOLS = ("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")


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


def _chord_from_degree(key: str, interval: int, quality: str) -> Chord:
    root = (NOTE_NAMES[key] + interval) % 12
    symbol = NOTE_SYMBOLS[root]
    if quality == "minor":
        symbol = f"{symbol}m"
    if quality == "dim":
        symbol = f"{symbol}dim"
    return Chord(symbol=symbol, root=root, quality=quality)


def default_progression(key: str, scale: str) -> tuple[Chord, ...]:
    if scale == "major":
        return (
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 9, "minor"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 7, "major"),
        )
    return (
        _chord_from_degree(key, 0, "minor"),
        _chord_from_degree(key, 8, "major"),
        _chord_from_degree(key, 3, "major"),
        _chord_from_degree(key, 10, "major"),
    )


def create_default_song(
    title: str = "First AI Band Sketch",
    style: str = "moody alt-rock",
    tempo_bpm: int = 108,
    key: str = "A",
    scale: str = "minor",
    preset: str = "default",
) -> SongState:
    if preset == "bluesy-alt-country":
        progression = (
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 10, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 7, "major"),
        )
        sections = (
            Section("Intro", 0, 4, 0.4, progression[:4]),
            Section("Verse", 4, 8, 0.5, progression),
            Section("Chorus", 12, 8, 0.82, progression),
            Section("Outro", 20, 4, 0.55, progression[:4]),
        )
    else:
        progression = default_progression(key, scale)
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
        preset=preset,
    )
