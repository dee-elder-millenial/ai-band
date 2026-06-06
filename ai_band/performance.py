from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from ai_band.humanize import clamp_midi
from ai_band.midi import MidiEvent, MidiMeta, MidiNote, MidiTrack


@dataclass(frozen=True)
class MixerControls:
    volume: int
    pan: int = 64
    mute: bool = False
    solo: bool = False
    reverb_send: int = 0
    delay_send: int = 0


@dataclass(frozen=True)
class InstrumentPreset:
    role: str
    program: int | None
    sample_hint: str
    mixer: MixerControls
    timing_amount: float = 1.0
    velocity_amount: int = 3
    preserve_chord_timing: bool = False


@dataclass(frozen=True)
class PerformanceSettings:
    groove_amount: float = 0.0
    swing_amount: float = 0.0
    velocity_humanize_amount: float = 0.0
    track_presets: dict[str, InstrumentPreset] = field(default_factory=dict)


DEFAULT_PRESETS: dict[str, InstrumentPreset] = {
    "AI Drummer": InstrumentPreset(
        role="drums",
        program=None,
        sample_hint="MT-PowerDrumKit or another multi-sampled drum instrument",
        mixer=MixerControls(volume=100, pan=64, reverb_send=26, delay_send=0),
        timing_amount=0.45,
        velocity_amount=4,
    ),
    "AI Percussion Extras": InstrumentPreset(
        role="drums",
        program=None,
        sample_hint="MT-PowerDrumKit percussion or a sampled tambourine/shaker patch",
        mixer=MixerControls(volume=76, pan=78, reverb_send=34, delay_send=8),
        timing_amount=0.55,
        velocity_amount=3,
    ),
    "AI Bass Player": InstrumentPreset(
        role="bass",
        program=33,
        sample_hint="Ample Bass P Lite II or another sampled electric bass",
        mixer=MixerControls(volume=90, pan=64, reverb_send=8, delay_send=0),
        timing_amount=0.35,
        velocity_amount=3,
    ),
    "AI Guitar Player": InstrumentPreset(
        role="chords",
        program=29,
        sample_hint="Ample Guitar M Lite Strummer; feed it chord blocks, not pre-strummed MIDI",
        mixer=MixerControls(volume=82, pan=46, reverb_send=24, delay_send=10),
        timing_amount=0.0,
        velocity_amount=2,
        preserve_chord_timing=True,
    ),
    "AI Keyboard Player": InstrumentPreset(
        role="chords",
        program=66,
        sample_hint="Splice Instrument pad/sax texture or another sampled keys layer",
        mixer=MixerControls(volume=70, pan=82, reverb_send=36, delay_send=12),
        timing_amount=0.30,
        velocity_amount=2,
    ),
    "AI Lead Player": InstrumentPreset(
        role="melody",
        program=81,
        sample_hint="Ample Guitar M Lite or another sampled lead instrument with bends enabled",
        mixer=MixerControls(volume=74, pan=58, reverb_send=30, delay_send=18),
        timing_amount=0.40,
        velocity_amount=4,
    ),
}


def default_performance_settings(
    groove_amount: float = 0.0,
    swing_amount: float = 0.0,
    velocity_humanize_amount: float = 0.0,
) -> PerformanceSettings:
    return PerformanceSettings(
        groove_amount=max(0.0, min(1.0, groove_amount)),
        swing_amount=max(0.0, min(1.0, swing_amount)),
        velocity_humanize_amount=max(0.0, min(1.0, velocity_humanize_amount)),
        track_presets=DEFAULT_PRESETS,
    )


def render_performance(
    tracks: Iterable[MidiTrack],
    ticks_per_beat: int,
    settings: PerformanceSettings | None = None,
) -> list[MidiTrack]:
    settings = settings or default_performance_settings()
    source_tracks = list(tracks)
    solo_active = any(
        settings.track_presets.get(track.name, DEFAULT_PRESETS.get(track.name, _fallback_preset(track))).mixer.solo
        for track in source_tracks
    )
    rendered: list[MidiTrack] = []
    for track in source_tracks:
        preset = settings.track_presets.get(track.name, DEFAULT_PRESETS.get(track.name, _fallback_preset(track)))
        rendered.append(_render_track(track, preset, ticks_per_beat, settings, solo_active))
    return rendered


def _render_track(
    track: MidiTrack,
    preset: InstrumentPreset,
    ticks_per_beat: int,
    settings: PerformanceSettings,
    solo_active: bool,
) -> MidiTrack:
    output = MidiTrack(
        name=track.name,
        channel=track.channel,
        program=track.program if track.program is not None else preset.program,
        metas=list(track.metas or ()),
        events=list(track.events or ()),
    )
    output.notes = _render_notes(track, preset, ticks_per_beat, settings)
    if track.channel is not None:
        output.events.extend(_mixer_events(track.channel, preset.mixer, solo_active))
    output.metas.append(MidiMeta(0, "text", f"render-role={preset.role}; sample-preferred={preset.sample_hint}"))
    output.metas.append(
        MidiMeta(
            0,
            "text",
            (
                "mixer="
                f"volume:{_effective_volume(preset.mixer, solo_active)} "
                f"pan:{preset.mixer.pan} mute:{str(preset.mixer.mute).lower()} "
                f"solo:{str(preset.mixer.solo).lower()} "
                f"reverb:{preset.mixer.reverb_send} delay:{preset.mixer.delay_send}"
            ),
        )
    )
    return output


def _render_notes(
    track: MidiTrack,
    preset: InstrumentPreset,
    ticks_per_beat: int,
    settings: PerformanceSettings,
) -> list[MidiNote]:
    if not track.notes:
        return []
    rendered: list[MidiNote] = []
    start_offsets = {
        start: _timing_offset(track.name, start, ticks_per_beat, settings, preset)
        for start in {note.start for note in track.notes}
    }
    index_by_start: dict[int, int] = {}
    for note in track.notes:
        note_index = index_by_start.get(note.start, 0)
        index_by_start[note.start] = note_index + 1
        offset = 0 if preset.preserve_chord_timing else start_offsets[note.start]
        velocity_offset = _velocity_offset(
            track.name,
            note.start,
            note.note,
            note_index,
            int(preset.velocity_amount * settings.velocity_humanize_amount),
        )
        rendered.append(
            MidiNote(
                start=max(0, note.start + offset),
                duration=max(1, note.duration),
                note=note.note,
                velocity=clamp_midi(note.velocity + velocity_offset),
                channel=note.channel,
            )
        )
    return rendered


def _mixer_events(channel: int, mixer: MixerControls, solo_active: bool) -> list[MidiEvent]:
    return [
        MidiEvent(0, 0xB0 | channel, (7, _effective_volume(mixer, solo_active))),
        MidiEvent(0, 0xB0 | channel, (10, max(0, min(127, mixer.pan)))),
        MidiEvent(0, 0xB0 | channel, (91, max(0, min(127, mixer.reverb_send)))),
        MidiEvent(0, 0xB0 | channel, (94, max(0, min(127, mixer.delay_send)))),
    ]


def _effective_volume(mixer: MixerControls, solo_active: bool) -> int:
    if mixer.mute or (solo_active and not mixer.solo):
        return 0
    return max(0, min(127, mixer.volume))


def _timing_offset(
    track_name: str,
    start: int,
    ticks_per_beat: int,
    settings: PerformanceSettings,
    preset: InstrumentPreset,
) -> int:
    amount = settings.groove_amount * preset.timing_amount
    pocket = 0
    if amount > 0:
        raw = _deterministic_wave(track_name, start, modulo=9) - 4
        pocket = int(raw * ticks_per_beat * 0.008 * amount)
    return pocket + _swing_offset(start, ticks_per_beat, settings.swing_amount)


def _swing_offset(start: int, ticks_per_beat: int, swing_amount: float) -> int:
    if swing_amount <= 0:
        return 0
    within_beat = start % ticks_per_beat
    eighth = ticks_per_beat // 2
    if abs(within_beat - eighth) > max(12, ticks_per_beat // 12):
        return 0
    return int(ticks_per_beat * 0.12 * max(0.0, min(1.0, swing_amount)))


def _velocity_offset(track_name: str, start: int, note: int, note_index: int, amount: int) -> int:
    if amount <= 0:
        return 0
    raw = _deterministic_wave(track_name, start + note * 17 + note_index * 31, modulo=11) - 5
    return int(raw * amount / 5)


def _deterministic_wave(seed: str, value: int, modulo: int) -> int:
    checksum = sum((index + 1) * ord(char) for index, char in enumerate(seed))
    return (checksum + value * 37) % modulo


def _fallback_preset(track: MidiTrack) -> InstrumentPreset:
    return InstrumentPreset(
        role="utility",
        program=track.program,
        sample_hint="external sampled instrument preferred when available",
        mixer=MixerControls(volume=88, pan=64, reverb_send=18, delay_send=0),
        timing_amount=0.20,
        velocity_amount=2,
    )
