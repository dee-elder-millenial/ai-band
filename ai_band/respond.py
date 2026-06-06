from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from ai_band.ai_feedback import AiFeedbackResult, controls_from_cue_with_ai, result_to_dict
from ai_band.bandleader import create_default_song
from ai_band.generate import build_tracks, tempo_events_for_preset
from ai_band.live_cue import LiveCue, read_live_cue
from ai_band.midi import write_midi

DEFAULT_RESPONSE_MIDI = Path("examples/ai-feedback-response.mid")
DEFAULT_DECISION_JSON = Path("state/last_ai_feedback.json")


@dataclass(frozen=True)
class FeedbackResponse:
    cue: LiveCue
    feedback: AiFeedbackResult
    midi_output: Path
    decision_output: Path


def write_feedback_response(
    *,
    cue_path: str | Path = "state/live_cue.json",
    midi_output: str | Path = DEFAULT_RESPONSE_MIDI,
    decision_output: str | Path = DEFAULT_DECISION_JSON,
    model: str | None = None,
    force_ai: bool = False,
    title: str = "AI Band Feedback Response",
    style: str = "responsive backing band",
    tempo_bpm: int = 108,
    key: str = "A",
    scale: str = "minor",
    preset: str = "default",
    mode: str = "ehaye",
    include_ai_rhythm_guitar: bool | None = False,
) -> FeedbackResponse:
    cue = read_live_cue(cue_path)
    feedback = controls_from_cue_with_ai(cue, model=model, force_ai=force_ai)
    midi_path = Path(midi_output)
    decision_path = Path(decision_output)

    ticks_per_beat, actual_tempo, tracks = build_tracks(
        title=title,
        style=style,
        tempo_bpm=tempo_bpm,
        key=key,
        scale=scale,
        preset=preset,
        mode=mode,
        include_ai_rhythm_guitar=include_ai_rhythm_guitar,
        controls=feedback.controls,
    )
    total_bars = create_default_song(preset=preset).total_bars
    tempo_events = tempo_events_for_preset(preset, actual_tempo, ticks_per_beat, total_bars)
    write_midi(midi_path, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=actual_tempo, tempo_events=tempo_events)

    decision_path.parent.mkdir(parents=True, exist_ok=True)
    decision_path.write_text(
        json.dumps(_decision_payload(cue, feedback, midi_path), indent=2) + "\n",
        encoding="utf-8",
    )
    return FeedbackResponse(cue, feedback, midi_path, decision_path)


def _decision_payload(cue: LiveCue, feedback: AiFeedbackResult, midi_output: Path) -> dict[str, object]:
    payload = result_to_dict(feedback)
    payload["cue"] = {
        "mode": cue.mode,
        "instruction": cue.instruction,
        "target": cue.target,
        "intensity": cue.intensity,
        "play_position_seconds": cue.play_position_seconds,
        "project_path": cue.project_path,
    }
    payload["midi_output"] = str(midi_output)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI Band cue feedback loop and write response MIDI.")
    parser.add_argument("--cue", default="state/live_cue.json", help="Cue JSON path")
    parser.add_argument("--output", default=str(DEFAULT_RESPONSE_MIDI), help="Response MIDI output path")
    parser.add_argument("--decision-json", default=str(DEFAULT_DECISION_JSON), help="AI decision JSON output path")
    parser.add_argument("--model", default=None, help="OpenAI model. Defaults to AI_BAND_OPENAI_MODEL or ai_feedback default.")
    parser.add_argument("--force-ai", action="store_true", help="Fail instead of falling back when the AI call cannot run")
    parser.add_argument("--title", default="AI Band Feedback Response")
    parser.add_argument("--style", default="responsive backing band")
    parser.add_argument("--tempo", type=int, default=108)
    parser.add_argument("--key", default="A", choices=("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"))
    parser.add_argument("--scale", default="minor", choices=("major", "minor"))
    parser.add_argument(
        "--preset",
        default="default",
        choices=("default", "bluesy-alt-country", "texas-alt-country", "southern-blues", "heartland-rock", "funk-reggae-jam"),
    )
    parser.add_argument("--mode", default="ehaye", choices=("full-band", "ehaye"))
    parser.add_argument("--ai-rhythm-guitar", action="store_true", help="Include AI rhythm guitar in the response MIDI")
    args = parser.parse_args()

    response = write_feedback_response(
        cue_path=args.cue,
        midi_output=args.output,
        decision_output=args.decision_json,
        model=args.model,
        force_ai=args.force_ai,
        title=args.title,
        style=args.style,
        tempo_bpm=args.tempo,
        key=args.key,
        scale=args.scale,
        preset=args.preset,
        mode=args.mode,
        include_ai_rhythm_guitar=True if args.ai_rhythm_guitar else False,
    )
    print(f"AI feedback source: {response.feedback.source}" + (f" ({response.feedback.error})" if response.feedback.error else ""))
    if response.feedback.rationale:
        print(f"Rationale: {response.feedback.rationale}")
    if response.feedback.budget_message:
        print(response.feedback.budget_message)
    print(f"Wrote decision JSON: {response.decision_output}")
    print(f"Wrote response MIDI: {response.midi_output}")


if __name__ == "__main__":
    main()
