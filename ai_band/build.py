from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from ai_band import __version__
from ai_band.generate import build_tracks
from ai_band.midi import write_midi

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_NAME = "ai-band-phase1-alpha"
BUILD_DIR = REPO_ROOT / "build" / BUILD_NAME
DIST_DIR = REPO_ROOT / "dist"
DEMO_MIDI = BUILD_DIR / "examples" / "first-sketch.mid"

PACKAGE_PATHS = (
    "README.md",
    "TODO.md",
    "LICENSE",
    "pyproject.toml",
    "ai_band",
    "docs",
    "Effects",
    "Scripts",
    "tests",
)


def main() -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True)
    DIST_DIR.mkdir(exist_ok=True)

    for relative in PACKAGE_PATHS:
        source = REPO_ROOT / relative
        target = BUILD_DIR / relative
        if source.is_dir():
            ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
            shutil.copytree(source, target, ignore=ignore)
        elif source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    ticks_per_beat, tempo_bpm, tracks = build_tracks()
    write_midi(DEMO_MIDI, tracks, ticks_per_beat=ticks_per_beat, tempo_bpm=tempo_bpm)

    manifest = {
        "name": BUILD_NAME,
        "version": __version__,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "demo_midi": str(DEMO_MIDI.relative_to(BUILD_DIR)).replace("\\", "/"),
        "midi": {
            "format": 1,
            "tracks": 8,
            "ticks_per_beat": ticks_per_beat,
            "tempo_bpm": tempo_bpm,
        },
        "entrypoints": {
            "generate": "python -m ai_band.generate --output examples/first-sketch.mid",
            "generate_ehaye": "python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --output examples/ehaye-backing-band.mid",
            "build": "python -m ai_band.build",
            "tests": "python -m unittest discover -s tests",
        },
        "reaper": {
            "script": "Scripts/ai_band_import_generated_midi.lua",
            "sound_check_script": "Scripts/ai_band_add_sound_check_synths.lua",
            "lower_track_levels_script": "Scripts/ai_band_lower_track_levels.lua",
            "rough_tones_script": "Scripts/ai_band_setup_rough_tones.lua",
            "ehaye_audition_script": "Scripts/ai_band_ehaye_audition_setup.lua",
            "tone_helpers": "Scripts/ai_band_tone_helpers.lua",
            "jsfx": "Effects/AI Band Humanizer.jsfx",
            "drum_synth_jsfx": "Effects/AI Band GM Drum Synth.jsfx",
        },
    }
    (BUILD_DIR / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    zip_path = DIST_DIR / f"{BUILD_NAME}-{__version__}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(BUILD_DIR.rglob("*")):
            if file.is_file():
                archive.write(file, Path(BUILD_NAME) / file.relative_to(BUILD_DIR))

    print(f"Wrote {zip_path}")


if __name__ == "__main__":
    main()
