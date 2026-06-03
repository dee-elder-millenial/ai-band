from __future__ import annotations

import argparse
from pathlib import Path

from ai_band.bandleader import create_default_song
from ai_band.midi import MidiMeta, MidiTrack, write_midi
from ai_band.members import bassist, drummer, guitarist, keyboardist, lead, percussion


def build_tracks() -> tuple[int, int, list[MidiTrack]]:
    song = create_default_song()
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
    args = parser.parse_args()

    ticks_per_beat, tempo_bpm, tracks = build_tracks()
    output = Path(args.output)
    write_midi(output, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

