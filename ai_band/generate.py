from __future__ import annotations

import argparse
from pathlib import Path

from ai_band.bandleader import create_default_song
from ai_band.controls import GenerationControls, controls_from_cue
from ai_band.live_cue import read_live_cue
from ai_band.midi import MidiMeta, MidiTrack, write_midi
from ai_band.members import bassist, drummer, guitarist, keyboardist, lead, percussion


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
    args = parser.parse_args()
    include_ai_rhythm_guitar = None
    if args.no_ai_rhythm_guitar:
        include_ai_rhythm_guitar = False
    if args.ai_rhythm_guitar:
        include_ai_rhythm_guitar = True
    controls = controls_from_cue(read_live_cue(args.cue)) if args.cue else GenerationControls()

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
    )
    output = Path(args.output)
    write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
