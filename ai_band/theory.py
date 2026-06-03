from __future__ import annotations

NOTE_NAMES = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}

MAJOR_SCALE = (0, 2, 4, 5, 7, 9, 11)
MINOR_SCALE = (0, 2, 3, 5, 7, 8, 10)


def note_number(name: str, octave: int) -> int:
    return 12 * (octave + 1) + NOTE_NAMES[name]


def chord_tones(root: int, quality: str, octave: int) -> tuple[int, int, int]:
    base = 12 * (octave + 1) + root
    if quality == "minor":
        return (base, base + 3, base + 7)
    if quality == "dim":
        return (base, base + 3, base + 6)
    return (base, base + 4, base + 7)


def scale_notes(key: str, scale: str, octave: int) -> list[int]:
    root = NOTE_NAMES[key]
    intervals = MINOR_SCALE if scale == "minor" else MAJOR_SCALE
    return [12 * (octave + 1) + ((root + interval) % 12) for interval in intervals]

