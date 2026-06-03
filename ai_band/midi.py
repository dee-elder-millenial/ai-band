from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class MidiNote:
    start: int
    duration: int
    note: int
    velocity: int
    channel: int


@dataclass(frozen=True)
class MidiMeta:
    tick: int
    kind: str
    text: str


@dataclass
class MidiTrack:
    name: str
    channel: int | None = None
    program: int | None = None
    notes: list[MidiNote] | None = None
    metas: list[MidiMeta] | None = None

    def __post_init__(self) -> None:
        if self.notes is None:
            self.notes = []
        if self.metas is None:
            self.metas = []


def write_midi(path: str | Path, tracks: Iterable[MidiTrack], ticks_per_beat: int, tempo_bpm: int) -> None:
    track_data = [_render_conductor_track(tempo_bpm)]
    track_data.extend(_render_track(track) for track in tracks)

    header = b"MThd" + (6).to_bytes(4, "big")
    header += (1).to_bytes(2, "big")
    header += len(track_data).to_bytes(2, "big")
    header += ticks_per_beat.to_bytes(2, "big")

    body = b"".join(b"MTrk" + len(data).to_bytes(4, "big") + data for data in track_data)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(header + body)


def _render_conductor_track(tempo_bpm: int) -> bytes:
    micros_per_quarter = int(60_000_000 / tempo_bpm)
    events = [
        (0, b"\xff\x51\x03" + micros_per_quarter.to_bytes(3, "big")),
        (0, b"\xff\x58\x04\x04\x02\x18\x08"),
    ]
    return _events_to_track(events)


def _render_track(track: MidiTrack) -> bytes:
    events: list[tuple[int, bytes]] = [(0, _text_event(0x03, track.name))]
    if track.channel is not None and track.program is not None:
        events.append((0, bytes([0xC0 | track.channel, track.program])))

    for meta in track.metas or []:
        meta_type = 0x06 if meta.kind == "marker" else 0x01
        events.append((meta.tick, _text_event(meta_type, meta.text)))

    for note in track.notes or []:
        events.append((note.start, bytes([0x90 | note.channel, note.note, note.velocity])))
        events.append((note.start + note.duration, bytes([0x80 | note.channel, note.note, 0])))

    events.sort(key=lambda item: (item[0], _event_order(item[1])))
    return _events_to_track(events)


def _events_to_track(events: list[tuple[int, bytes]]) -> bytes:
    output = bytearray()
    last_tick = 0
    for tick, data in events:
        output.extend(_vlq(tick - last_tick))
        output.extend(data)
        last_tick = tick
    output.extend(_vlq(0))
    output.extend(b"\xff\x2f\x00")
    return bytes(output)


def _text_event(kind: int, text: str) -> bytes:
    encoded = text.encode("utf-8")
    return bytes([0xFF, kind]) + _vlq(len(encoded)) + encoded


def _event_order(data: bytes) -> int:
    status = data[0] & 0xF0
    if data[0] == 0xFF or status == 0xC0:
        return 0
    if status == 0x80:
        return 1
    return 2


def _vlq(value: int) -> bytes:
    if value < 0:
        raise ValueError("MIDI delta times cannot be negative")
    buffer = value & 0x7F
    value >>= 7
    while value:
        buffer <<= 8
        buffer |= ((value & 0x7F) | 0x80)
        value >>= 7
    result = bytearray()
    while True:
        result.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
        else:
            break
    return bytes(result)
