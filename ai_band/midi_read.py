from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ReadTrack:
    name: str | None = None
    markers: list[str] = field(default_factory=list)
    text: list[str] = field(default_factory=list)
    note_count: int = 0
    channels: set[int] = field(default_factory=set)
    programs: list[int] = field(default_factory=list)
    last_tick: int = 0


@dataclass(frozen=True)
class MidiSummary:
    format: int
    track_count: int
    ticks_per_beat: int
    tracks: tuple[ReadTrack, ...]


def read_midi_summary(path: str | Path) -> MidiSummary:
    data = Path(path).read_bytes()
    cursor = 0
    if data[cursor : cursor + 4] != b"MThd":
        raise ValueError("Not a Standard MIDI File")
    cursor += 4
    header_length = _read_u32(data, cursor)
    cursor += 4
    if header_length != 6:
        raise ValueError(f"Unsupported MIDI header length: {header_length}")
    midi_format = _read_u16(data, cursor)
    track_count = _read_u16(data, cursor + 2)
    ticks_per_beat = _read_u16(data, cursor + 4)
    cursor += header_length

    tracks: list[ReadTrack] = []
    for _index in range(track_count):
        if data[cursor : cursor + 4] != b"MTrk":
            raise ValueError("Expected MIDI track chunk")
        cursor += 4
        length = _read_u32(data, cursor)
        cursor += 4
        chunk = data[cursor : cursor + length]
        cursor += length
        tracks.append(_read_track(chunk))

    return MidiSummary(
        format=midi_format,
        track_count=track_count,
        ticks_per_beat=ticks_per_beat,
        tracks=tuple(tracks),
    )


def _read_track(chunk: bytes) -> ReadTrack:
    track = ReadTrack()
    cursor = 0
    tick = 0
    running_status: int | None = None

    while cursor < len(chunk):
        delta, cursor = _read_vlq(chunk, cursor)
        tick += delta
        status = chunk[cursor]
        cursor += 1

        if status < 0x80:
            if running_status is None:
                raise ValueError("Running status used before status byte")
            cursor -= 1
            status = running_status
        elif status < 0xF0:
            running_status = status

        if status == 0xFF:
            meta_type = chunk[cursor]
            cursor += 1
            length, cursor = _read_vlq(chunk, cursor)
            payload = chunk[cursor : cursor + length]
            cursor += length
            if meta_type == 0x2F:
                break
            if meta_type in {0x01, 0x03, 0x06}:
                text = payload.decode("utf-8", errors="replace")
                if meta_type == 0x03:
                    track.name = text
                elif meta_type == 0x06:
                    track.markers.append(text)
                else:
                    track.text.append(text)
            continue

        event_type = status & 0xF0
        channel = status & 0x0F
        if event_type in {0x80, 0x90, 0xA0, 0xB0, 0xE0}:
            note_or_control = chunk[cursor]
            value = chunk[cursor + 1]
            cursor += 2
            if event_type == 0x90 and value > 0:
                track.note_count += 1
                track.channels.add(channel)
            _ = note_or_control
        elif event_type in {0xC0, 0xD0}:
            value = chunk[cursor]
            cursor += 1
            if event_type == 0xC0:
                track.programs.append(value)
                track.channels.add(channel)
        else:
            raise ValueError(f"Unsupported MIDI event status: 0x{status:02X}")

    track.last_tick = tick
    return track


def _read_u16(data: bytes, cursor: int) -> int:
    return int.from_bytes(data[cursor : cursor + 2], "big")


def _read_u32(data: bytes, cursor: int) -> int:
    return int.from_bytes(data[cursor : cursor + 4], "big")


def _read_vlq(data: bytes, cursor: int) -> tuple[int, int]:
    value = 0
    while True:
        byte = data[cursor]
        cursor += 1
        value = (value << 7) | (byte & 0x7F)
        if byte & 0x80 == 0:
            return value, cursor

