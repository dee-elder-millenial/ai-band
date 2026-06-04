from __future__ import annotations

from dataclasses import dataclass, replace

from ai_band.performance import InstrumentPreset, MixerControls, PerformanceSettings, default_performance_settings


@dataclass(frozen=True)
class SoundGuyDecision:
    mix_profile: str
    rhythm_guitar_profile: str
    performance: PerformanceSettings
    notes: tuple[str, ...]


def advise_sound_guy(
    preset: str,
    style: str = "",
    listening_note: str = "",
    requested_rhythm_guitar_profile: str = "auto",
) -> SoundGuyDecision:
    text = f"{preset} {style} {listening_note}".lower()
    settings = default_performance_settings()
    notes: list[str] = []
    mix_profile = "balanced"
    rhythm_guitar_profile = requested_rhythm_guitar_profile

    if preset == "heartland-rock":
        settings = _with_feel(settings, groove=0.22, swing=0.04, velocity=0.35)
        mix_profile = "drums-forward"
        notes.append("Heartland profile: keep the rhythm section forward and add modest render feel.")
    elif preset == "texas-alt-country":
        settings = _with_feel(settings, groove=0.16, swing=0.06, velocity=0.28)
        settings = _set_mixer(settings, "AI Bass Player", volume=88, reverb_send=5)
        settings = _set_mixer(settings, "AI Drummer", volume=94, reverb_send=18)
        settings = _set_mixer(settings, "AI Guitar Player", volume=76, reverb_send=22, delay_send=6)
        settings = _set_mixer(settings, "AI Keyboard Player", volume=60, reverb_send=34, delay_send=10)
        settings = _set_mixer(settings, "AI Lead Player", volume=66, reverb_send=32, delay_send=16)
        mix_profile = "vocal-space"
        notes.append("Texas alt-country profile: slow pocket, vocal space, bass and drums as the floor.")

    if _mentions_any(text, ("bass is killing it", "bass killing it", "love the bass", "bass is working")):
        settings = _set_mixer(settings, "AI Bass Player", volume=91, reverb_send=6)
        settings = _set_mixer(settings, "AI Drummer", volume=102)
        settings = _set_mixer(settings, "AI Keyboard Player", volume=66)
        settings = _set_mixer(settings, "AI Lead Player", volume=70)
        mix_profile = "bass-anchor"
        notes.append("Protect the bass pocket; tuck keys and lead around it.")

    if _mentions_any(text, ("drums buried", "can't hear the drums", "drums too quiet", "drums need")):
        settings = _set_mixer(settings, "AI Drummer", volume=106, reverb_send=22)
        mix_profile = "drums-forward"
        notes.append("Bring drums forward without pushing the whole master.")

    if _mentions_any(text, ("bass heavy", "too much bass", "bass too loud")):
        settings = _set_mixer(settings, "AI Bass Player", volume=84)
        notes.append("Ease bass volume while keeping the part intact.")

    if _mentions_any(text, ("keys crowd", "keys are crowding", "too much keys", "keys too loud")):
        settings = _set_mixer(settings, "AI Keyboard Player", volume=62)
        notes.append("Pull keys back to leave room for vocal and guitar.")

    if _mentions_any(text, ("lead robotic", "lead sounds robotic", "lead too much", "lead crowds")):
        settings = _set_mixer(settings, "AI Lead Player", volume=68, reverb_send=34, delay_send=22)
        notes.append("Tuck lead back and give it more space until phrase generation improves.")

    if _mentions_any(text, ("rhythm guitar", "guitar strange", "guitar weird", "strange", "plugin", "strummer")):
        if requested_rhythm_guitar_profile == "auto":
            rhythm_guitar_profile = "simple-blocks"
        settings = _set_mixer(settings, "AI Guitar Player", volume=78, reverb_send=28, delay_send=8)
        notes.append("Diagnose rhythm guitar with simpler chord blocks before changing the arrangement.")

    if rhythm_guitar_profile == "auto":
        rhythm_guitar_profile = "ample-strummer" if preset == "heartland-rock" else "auto"

    if not notes:
        notes.append("Balanced default: preserve arrangement and apply conservative audition settings.")

    return SoundGuyDecision(
        mix_profile=mix_profile,
        rhythm_guitar_profile=rhythm_guitar_profile,
        performance=settings,
        notes=tuple(notes),
    )


def _with_feel(settings: PerformanceSettings, groove: float, swing: float, velocity: float) -> PerformanceSettings:
    return PerformanceSettings(
        groove_amount=groove,
        swing_amount=swing,
        velocity_humanize_amount=velocity,
        track_presets=settings.track_presets,
    )


def _set_mixer(
    settings: PerformanceSettings,
    track_name: str,
    volume: int | None = None,
    pan: int | None = None,
    mute: bool | None = None,
    solo: bool | None = None,
    reverb_send: int | None = None,
    delay_send: int | None = None,
) -> PerformanceSettings:
    preset = settings.track_presets[track_name]
    mixer = preset.mixer
    updated_mixer = MixerControls(
        volume=mixer.volume if volume is None else volume,
        pan=mixer.pan if pan is None else pan,
        mute=mixer.mute if mute is None else mute,
        solo=mixer.solo if solo is None else solo,
        reverb_send=mixer.reverb_send if reverb_send is None else reverb_send,
        delay_send=mixer.delay_send if delay_send is None else delay_send,
    )
    updated_preset: InstrumentPreset = replace(preset, mixer=updated_mixer)
    updated_presets = dict(settings.track_presets)
    updated_presets[track_name] = updated_preset
    return PerformanceSettings(
        groove_amount=settings.groove_amount,
        swing_amount=settings.swing_amount,
        velocity_humanize_amount=settings.velocity_humanize_amount,
        track_presets=updated_presets,
    )


def _mentions_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
