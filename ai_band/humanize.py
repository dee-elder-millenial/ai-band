from __future__ import annotations

from ai_band.song_state import SongState

_POCKET = (-0.006, 0.004, 0.010, -0.003, 0.006, -0.008)
_VELOCITY = (0, -3, 2, -2, 3, -1, 1, -4)
_DURATION = (0.02, -0.03, 0.01, -0.02, 0.03, -0.01)


def feel_amount(song: SongState) -> float:
    if song.preset == "heartland-rock":
        return 1.0
    if song.preset == "southern-blues":
        return 0.9
    if song.preset == "bluesy-alt-country":
        return 0.8
    return 0.65


def pocket_offset(song: SongState, bar: int, beat: float, amount: float = 1.0) -> int:
    subdivision = int(round(beat * 4))
    index = (bar * 7 + subdivision * 3) % len(_POCKET)
    return int(song.ticks_per_beat * _POCKET[index] * amount)


def pocket_start(song: SongState, bar: int, beat: float, amount: float = 1.0) -> int:
    return max(song.beat_tick(bar, beat) + pocket_offset(song, bar, beat, amount), song.bar_tick(bar))


def played_start(song: SongState, bar: int, beat: float, amount: float = 1.0) -> int:
    return pocket_start(song, bar, beat, amount * feel_amount(song))


def velocity_shift(bar: int, beat: float, amount: int = 3) -> int:
    subdivision = int(round(beat * 4))
    raw = _VELOCITY[(bar * 5 + subdivision) % len(_VELOCITY)]
    return int(raw * amount / 3)


def played_velocity(value: int, song: SongState, bar: int, beat: float, amount: int = 3) -> int:
    return clamp_midi(value + velocity_shift(bar, beat, max(1, int(amount * feel_amount(song)))))


def played_duration(
    song: SongState,
    duration: int,
    bar: int,
    beat: float,
    amount: float = 1.0,
    minimum: int | None = None,
) -> int:
    subdivision = int(round(beat * 4))
    raw = _DURATION[(bar * 3 + subdivision) % len(_DURATION)]
    shifted = duration + int(song.ticks_per_beat * raw * amount * feel_amount(song))
    return max(minimum or 1, shifted)


def phrase_lift(local_bar: int, section_bars: int, amount: int = 3) -> int:
    four_bar_shape = (-1, 0, 1, 2)
    lift = four_bar_shape[local_bar % len(four_bar_shape)]
    if local_bar == 0:
        lift -= 1
    if local_bar >= max(section_bars - 2, 0):
        lift += 2
    return int(lift * amount / 3)


def clamp_midi(value: int) -> int:
    return max(1, min(127, value))
