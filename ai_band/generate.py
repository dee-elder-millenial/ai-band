from __future__ import annotations

import argparse
from pathlib import Path

from ai_band.bandleader import create_default_song
from ai_band.controls import GenerationControls, controls_from_cue
from ai_band.ai_feedback import controls_from_cue_with_ai
from ai_band.live_cue import read_live_cue
from ai_band.midi import MidiEvent, MidiMeta, MidiTrack, write_midi
from ai_band.members import bassist, drummer, guitarist, keyboardist, lead, percussion
from ai_band.performance import PerformanceSettings, default_performance_settings, render_performance


def tempo_events_for_preset(preset: str, tempo_bpm: int, ticks_per_beat: int, total_bars: int) -> list[tuple[int, int]]:
    if preset != "heartland-rock":
        return []
    bar_ticks = ticks_per_beat * 4
    contour = (0, 0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0)
    events: list[tuple[int, int]] = []
    for index, bar in enumerate(range(0, total_bars, 4)):
        drift = contour[index % len(contour)]
        if bar >= max(total_bars - 16, 0):
            drift += 1
        drift = max(-1, min(1, drift))
        bpm = max(40, tempo_bpm + drift)
        if not events or events[-1][1] != bpm:
            events.append((bar * bar_ticks, bpm))
    if events and events[0][0] != 0:
        events.insert(0, (0, tempo_bpm))
    return events


def build_tracks(
    title: str = "First AI Band Sketch",
    style: str = "moody alt-rock",
    tempo_bpm: int = 108,
    key: str = "A",
    scale: str = "minor",
    preset: str = "default",
    mode: str = "full-band",
    include_ai_rhythm_guitar: bool | None = None,
    controls: GenerationControls | None = None,
    performance: PerformanceSettings | None = None,
) -> tuple[int, int, list[MidiTrack]]:
    ticks_per_beat, tempo_bpm, tracks = compose_tracks(
        title=title,
        style=style,
        tempo_bpm=tempo_bpm,
        key=key,
        scale=scale,
        preset=preset,
        mode=mode,
        include_ai_rhythm_guitar=include_ai_rhythm_guitar,
        controls=controls,
    )
    rendered_tracks = render_performance(tracks, ticks_per_beat=ticks_per_beat, settings=performance)
    add_pitch_bend_resets(rendered_tracks)
    return ticks_per_beat, tempo_bpm, rendered_tracks


def compose_tracks(
    title: str = "First AI Band Sketch",
    style: str = "moody alt-rock",
    tempo_bpm: int = 108,
    key: str = "A",
    scale: str = "minor",
    preset: str = "default",
    mode: str = "full-band",
    include_ai_rhythm_guitar: bool | None = None,
    controls: GenerationControls | None = None,
) -> tuple[int, int, list[MidiTrack]]:
    song = create_default_song(title=title, style=style, tempo_bpm=tempo_bpm, key=key, scale=scale, preset=preset)
    controls = controls or GenerationControls()
    if include_ai_rhythm_guitar is None:
        include_ai_rhythm_guitar = mode != "ehaye"

    markers = MidiTrack("AI Bandleader")
    for section in song.sections:
        markers.metas.append(MidiMeta(song.bar_tick(section.start_bar), "marker", section.name))
        markers.metas.append(
            MidiMeta(
                song.bar_tick(section.start_bar),
                "text",
                f"{section.name}: preset={song.preset}, energy={section.energy:.2f}, chords={' '.join(chord.symbol for chord in section.chords)}",
            )
        )
    if controls.cue_summary:
        markers.metas.append(MidiMeta(0, "text", f"Live cue applied: {controls.cue_summary}"))
    if mode == "ehaye":
        markers.metas.append(
            MidiMeta(
                0,
                "text",
                "The Ehaye Band mode: Deanna is lead vocal and rhythm guitar; AI members generate backing parts.",
            )
        )
    if preset == "bluesy-alt-country":
        markers.metas.append(MidiMeta(0, "text", "Bluesy alt-country preset: sparse bent lead licks enabled."))
    if preset == "southern-blues":
        markers.metas.append(MidiMeta(0, "text", "Southern blues preset: long protest-roadhouse form, sparse vocal-support lead."))
    if preset == "heartland-rock":
        markers.metas.append(MidiMeta(0, "text", "Heartland rock preset: driving bass, deep drums, rich electric guitar, sax-like pad support."))
        markers.metas.append(
            MidiMeta(
                0,
                "text",
                "REAPER audition hint: run ai_band_apply_audition_mix.lua; try lead-back if lead crowds, warmer-room if dry, drums-forward if groove disappears.",
            )
        )

    tracks = [
        markers,
        drummer.generate(song, bigger=controls.drums_bigger),
        bassist.generate(song, simplify=controls.bass_simplify),
    ]
    if include_ai_rhythm_guitar:
        tracks.append(guitarist.generate(song))
    tracks.extend(
        [
            keyboardist.generate(song, leave_space=controls.keys_leave_space),
            lead.generate(song, sparse=controls.lead_sparse),
            percussion.generate(song),
        ]
    )
    return song.ticks_per_beat, song.tempo_bpm, tracks


def add_pitch_bend_resets(tracks: list[MidiTrack]) -> None:
    for track in tracks:
        if track.channel is None:
            continue
        pitch_bends = [event for event in track.events if event.status == (0xE0 | track.channel)]
        if not pitch_bends:
            continue
        center = _pitch_bend_center(track.channel)
        track.events.append(MidiEvent(tick=0, status=0xE0 | track.channel, data=center))
        last_tick = max(event.tick for event in pitch_bends)
        track.events.append(MidiEvent(tick=last_tick + 1, status=0xE0 | track.channel, data=center))


def _pitch_bend_center(channel: int) -> tuple[int, int]:
    value = 8192
    return (value & 0x7F, (value >> 7) & 0x7F)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a first AI Band MIDI sketch.")
    parser.add_argument("--output", default="examples/first-sketch.mid", help="Output .mid path")
    parser.add_argument("--title", default="First AI Band Sketch", help="Song title stored in the generated sketch")
    parser.add_argument("--style", default="moody alt-rock", help="Human-readable style label")
    parser.add_argument("--tempo", type=int, default=108, help="Tempo in beats per minute")
    parser.add_argument("--key", default="A", choices=("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"))
    parser.add_argument("--scale", default="minor", choices=("major", "minor"))
    parser.add_argument("--preset", default="default", choices=("default", "bluesy-alt-country", "southern-blues", "heartland-rock"))
    parser.add_argument(
        "--mode",
        default="full-band",
        choices=("full-band", "ehaye"),
        help="Generation mode. 'ehaye' treats the AI as backing bandmates for lead vocal and human rhythm guitar.",
    )
    parser.add_argument(
        "--no-ai-rhythm-guitar",
        action="store_true",
        help="Do not generate the AI rhythm guitar track.",
    )
    parser.add_argument(
        "--ai-rhythm-guitar",
        action="store_true",
        help="Generate the AI rhythm guitar track even in modes where it is normally disabled.",
    )
    parser.add_argument("--cue", help="Read a live cue JSON file and apply it to generation controls")
    parser.add_argument("--ai-feedback", action="store_true", help="Use real AI to interpret --cue when OPENAI_API_KEY is set")
    parser.add_argument("--ai-model", default=None, help="OpenAI model for --ai-feedback")
    parser.add_argument("--force-ai-feedback", action="store_true", help="Fail if --ai-feedback cannot call the model")
    parser.add_argument("--groove", type=float, default=0.0, help="Performance timing humanization amount from 0.0 to 1.0")
    parser.add_argument("--swing", type=float, default=0.0, help="Delay off-beat eighth notes from 0.0 to 1.0")
    parser.add_argument("--velocity-humanize", type=float, default=0.0, help="Performance velocity variation amount from 0.0 to 1.0")
    args = parser.parse_args()
    include_ai_rhythm_guitar = None
    if args.no_ai_rhythm_guitar:
        include_ai_rhythm_guitar = False
    if args.ai_rhythm_guitar:
        include_ai_rhythm_guitar = True
    controls = GenerationControls()
    if args.cue:
        cue = read_live_cue(args.cue)
        if args.ai_feedback:
            result = controls_from_cue_with_ai(cue, model=args.ai_model, force_ai=args.force_ai_feedback)
            controls = result.controls
            print(f"AI feedback source: {result.source}" + (f" ({result.error})" if result.error else ""))
            if result.budget_message:
                print(result.budget_message)
        else:
            controls = controls_from_cue(cue)

    ticks_per_beat, tempo_bpm, tracks = build_tracks(
        title=args.title,
        style=args.style,
        tempo_bpm=args.tempo,
        key=args.key,
        scale=args.scale,
        preset=args.preset,
        mode=args.mode,
        include_ai_rhythm_guitar=include_ai_rhythm_guitar,
        controls=controls,
        performance=default_performance_settings(
            groove_amount=args.groove,
            swing_amount=args.swing,
            velocity_humanize_amount=args.velocity_humanize,
        ),
    )
    tempo_events = tempo_events_for_preset(args.preset, tempo_bpm, ticks_per_beat, create_default_song(preset=args.preset).total_bars)
    output = Path(args.output)
    write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm, tempo_events=tempo_events)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
