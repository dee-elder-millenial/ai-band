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
    if song.preset == "texas-alt-country":
        return 0.72
    return 0.65


def pocket_offset(song: SongState, bar: int, beat: float, amount: float = 1.0) -> int:
    subdivision = int(round(beat * 4))
    index = (bar * 7 + subdivision * 3) % len(_POCKET)
    return int(song.ticks_per_beat * _POCKET[index] * amount)


def pocket_start(song: SongState, bar: int, beat: float, amount: float = 1.0) -> int:
    return max(song.beat_tick(bar, beat) + pocket_offset(song, bar, beat, amount), song.bar_tick(bar))


def section_groove_offset(song: SongState, local_bar: int, section_bars: int, amount: float = 1.0) -> int:
    if song.preset != "heartland-rock":
        return 0
    phrase_shape = (0.008, 0.003, -0.002, -0.007)
    offset = phrase_shape[local_bar % len(phrase_shape)]
    if local_bar == 0:
        offset += 0.004
    if local_bar >= max(section_bars - 2, 0):
        offset -= 0.004
    return int(song.ticks_per_beat * offset * amount)


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


def support_rest(song: SongState, role: str, energy: float, local_bar: int, section_bars: int, beat: float) -> bool:
    if local_bar == 0 or local_bar >= max(section_bars - 1, 0):
        return False
    if beat in {0, 1, 2, 3} and role in {"bass", "drums"}:
        return False
    density_bias = {
        "hat": 6,
        "guitar": 6,
        "keys": 6,
        "percussion": 6,
        "bass": 5,
    }.get(role, 3)
    energy_offset = 1 if energy >= 0.88 else 0 if energy >= 0.70 else -1
    preset_offset = 1 if song.preset == "heartland-rock" else 0
    threshold = max(1, min(7, density_bias + energy_offset + preset_offset))
    score = (local_bar * 3 + int(round(beat * 4)) * 5 + len(role)) % 8
    return score >= threshold


def transition_pickup(energy: float, local_bar: int, section_bars: int) -> bool:
    if energy < 0.52:
        return False
    if local_bar == section_bars - 1:
        return True
    return energy >= 0.76 and local_bar % 4 == 3


def expression_curve(start: int, duration: int, energy: float, bar: int, beat: float) -> tuple[tuple[int, int], ...]:
    if duration < 96:
        return ()
    shape = (0, 4, -2, 6, 1, -3)
    contour = shape[(bar + int(round(beat * 2))) % len(shape)]
    center = clamp_midi(72 + int(energy * 20) + contour)
    lift = 8 + int(energy * 8)
    return (
        (start, clamp_midi(center - 8)),
        (start + int(duration * 0.35), clamp_midi(center + lift)),
        (start + int(duration * 0.82), clamp_midi(center - 4)),
    )


def phrase_lift(local_bar: int, section_bars: int, amount: int = 3) -> int:
    four_bar_shape = (-1, 0, 1, 2)
    lift = four_bar_shape[local_bar % len(four_bar_shape)]
    if local_bar == 0:
        lift -= 1
    if local_bar >= max(section_bars - 2, 0):
        lift += 2
    return int(lift * amount / 3)


def section_lift(song: SongState, local_bar: int, section_bars: int, amount: int = 3) -> int:
    return int(phrase_lift(local_bar, section_bars, amount) * feel_amount(song))


def clamp_midi(value: int) -> int:
    return max(1, min(127, value))
