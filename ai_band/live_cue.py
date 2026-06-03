from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LiveCue:
    mode: str
    instruction: str
    target: str
    intensity: float
    play_position_seconds: float
    project_path: str


def read_live_cue(path: str | Path = "state/live_cue.json") -> LiveCue:
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return LiveCue(
        mode=str(data.get("mode", "live-cue")),
        instruction=str(data.get("instruction", "")),
        target=str(data.get("target", "bandleader")),
        intensity=float(data.get("intensity", 0.5)),
        play_position_seconds=float(data.get("play_position_seconds", 0)),
        project_path=str(data.get("project_path", "")),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the current AI Band live cue.")
    parser.add_argument("--path", default="state/live_cue.json")
    args = parser.parse_args()

    cue = read_live_cue(args.path)
    print(f"{cue.target}: {cue.instruction} (intensity={cue.intensity:.2f})")


if __name__ == "__main__":
    main()
