from __future__ import annotations

import argparse
from pathlib import Path

from ai_band.bandleader import create_default_song
from ai_band.midi import MidiMeta, MidiTrack, write_midi
from ai_band.members import bassist, drummer, guitarist, keyboardist, lead, percussion


def build_tracks(
    title: str = "First AI Band Sketch",
    style: str = "moody alt-rock",
    tempo_bpm: int = 108,
    key: str = "A",
    scale: str = "minor",
) -> tuple[int, int, list[MidiTrack]]:
    song = create_default_song(title=title, style=style, tempo_bpm=tempo_bpm, key=key, scale=scale)
    markers = MidiTrack("AI Bandleader")
    for section in song.sections:
        markers.metas.append(MidiMeta(song.bar_tick(section.start_bar), "marker", section.name))
        markers.metas.append(
            MidiMeta(
                song.bar_tick(section.start_bar),
                "text",
                f"{section.name}: energy={section.energy:.2f}, chords={' '.join(chord.symbol for chord in section.chords)}",
            )
        )

    tracks = [
        markers,
        drummer.generate(song),
        bassist.generate(song),
        guitarist.generate(song),
        keyboardist.generate(song),
        lead.generate(song),
        percussion.generate(song),
    ]
    return song.ticks_per_beat, song.tempo_bpm, tracks


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a first AI Band MIDI sketch.")
    parser.add_argument("--output", default="examples/first-sketch.mid", help="Output .mid path")
    parser.add_argument("--title", default="First AI Band Sketch", help="Song title stored in the generated sketch")
    parser.add_argument("--style", default="moody alt-rock", help="Human-readable style label")
    parser.add_argument("--tempo", type=int, default=108, help="Tempo in beats per minute")
    parser.add_argument("--key", default="A", choices=("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"))
    parser.add_argument("--scale", default="minor", choices=("major", "minor"))
    args = parser.parse_args()

    ticks_per_beat, tempo_bpm, tracks = build_tracks(
        title=args.title,
        style=args.style,
        tempo_bpm=args.tempo,
        key=args.key,
        scale=args.scale,
    )
    output = Path(args.output)
    write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
