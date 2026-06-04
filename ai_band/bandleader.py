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
    if preset == "heartland-rock":
        verse = (
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 10, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 7, "major"),
        )
        chorus = (
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 10, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 10, "major"),
            _chord_from_degree(key, 7, "major"),
            _chord_from_degree(key, 7, "major"),
        )
        bridge = (
            _chord_from_degree(key, 9, "minor"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 7, "major"),
            _chord_from_degree(key, 9, "minor"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 10, "major"),
            _chord_from_degree(key, 7, "major"),
        )
        sections = (
            Section("Intro", 0, 4, 0.72, verse[:4]),
            Section("Verse 1", 4, 12, 0.68, verse),
            Section("Pre-Chorus 1", 16, 4, 0.78, bridge[:4]),
            Section("Chorus 1", 20, 8, 0.92, chorus),
            Section("Verse 2", 28, 12, 0.74, verse),
            Section("Pre-Chorus 2", 40, 4, 0.82, bridge[:4]),
            Section("Chorus 2", 44, 8, 0.95, chorus),
            Section("Bridge", 52, 8, 0.70, bridge),
            Section("Guitar Solo", 60, 12, 0.97, chorus),
            Section("Final Chorus", 72, 12, 0.98, chorus),
            Section("Outro", 84, 4, 0.82, verse[:4]),
        )
    elif preset == "southern-blues":
        intro = (
            _chord_from_degree(key, 0, "minor"),
            _chord_from_degree(key, 3, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "minor"),
        )
        verse = (
            _chord_from_degree(key, 0, "minor"),
            _chord_from_degree(key, 0, "minor"),
            _chord_from_degree(key, 3, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "minor"),
            _chord_from_degree(key, 0, "minor"),
            _chord_from_degree(key, 8, "major"),
            _chord_from_degree(key, 7, "major"),
        )
        chorus = (
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 8, "major"),
            _chord_from_degree(key, 0, "minor"),
            _chord_from_degree(key, 0, "minor"),
            _chord_from_degree(key, 3, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 8, "major"),
            _chord_from_degree(key, 7, "major"),
        )
        bridge = (
            _chord_from_degree(key, 8, "major"),
            _chord_from_degree(key, 3, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "minor"),
            _chord_from_degree(key, 8, "major"),
            _chord_from_degree(key, 3, "major"),
            _chord_from_degree(key, 7, "major"),
            _chord_from_degree(key, 7, "major"),
        )
        sections = (
            Section("Intro", 0, 4, 0.45, intro),
            Section("Verse 1", 4, 12, 0.52, verse),
            Section("Chorus 1", 16, 8, 0.78, chorus),
            Section("Verse 2", 24, 12, 0.58, verse),
            Section("Chorus 2", 36, 8, 0.84, chorus),
            Section("Bridge", 44, 8, 0.62, bridge),
            Section("Solo", 52, 12, 0.88, chorus),
            Section("Final Chorus", 64, 8, 0.9, chorus),
            Section("Outro", 72, 4, 0.55, intro),
        )
    elif preset == "bluesy-alt-country":
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
    elif preset == "texas-alt-country":
        verse = (
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 9, "minor"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 7, "major"),
        )
        chorus = (
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 7, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 9, "minor"),
            _chord_from_degree(key, 7, "major"),
        )
        bridge = (
            _chord_from_degree(key, 9, "minor"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 7, "major"),
            _chord_from_degree(key, 10, "major"),
            _chord_from_degree(key, 5, "major"),
            _chord_from_degree(key, 0, "major"),
            _chord_from_degree(key, 7, "major"),
        )
        sections = (
            Section("Intro", 0, 4, 0.36, verse[:4]),
            Section("Verse 1", 4, 12, 0.44, verse),
            Section("Chorus 1", 16, 8, 0.68, chorus),
            Section("Verse 2", 24, 12, 0.48, verse),
            Section("Chorus 2", 36, 8, 0.72, chorus),
            Section("Bridge", 44, 8, 0.54, bridge),
            Section("Final Chorus", 52, 12, 0.78, chorus),
            Section("Outro", 64, 4, 0.42, verse[:4]),
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
