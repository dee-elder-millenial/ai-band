# AI Band

AI Band is a REAPER-oriented toolkit for generating editable song sketches from a coordinated group of AI-assisted band members.

The first prototype is intentionally MIDI-first. A bandleader creates a shared song plan, then each member generates parts from that plan:

- AI Bandleader
- AI Drummer
- AI Bass Player
- AI Guitar Player
- AI Keyboard Player
- AI Lead Player
- AI Percussion / Extras

Phase 1 starts with deterministic player logic so the REAPER workflow is solid before model calls are added. The design leaves room for real AI models to drive arrangement, style interpretation, prompts, and regeneration commands.

## Quick Start

Generate the first 16-bar sketch:

```powershell
python -m ai_band.generate --output examples/first-sketch.mid
```

Then import `examples/first-sketch.mid` into REAPER.

Generate a custom sketch:

```powershell
python -m ai_band.generate --output examples/c-major-sketch.mid --title "C Major Sketch" --style "clean indie rock" --tempo 124 --key C --scale major
```

Create the Phase 1 alpha build package:

```powershell
python -m ai_band.build
```

The build command writes:

- `build/ai-band-phase1-alpha/`
- `dist/ai-band-phase1-alpha-0.1.0.zip`

Run the current smoke test:

```powershell
python -m unittest discover -s tests
```

## Project Shape

```text
ai-band/
  TODO.md
  README.md
  pyproject.toml
  Scripts/
    ai_band_import_generated_midi.lua
  Effects/
    AI Band Humanizer.jsfx
  ai_band/
    build.py
    bandleader.py
    generate.py
    midi.py
    song_state.py
    members/
      drummer.py
      bassist.py
      guitarist.py
      keyboardist.py
      lead.py
      percussion.py
  docs/
    FIRST_BUILD.md
    REAPER.md
  examples/
    .gitkeep
```

## Current Milestone

The current prototype generates a type-1 Standard MIDI File with separate tracks for:

- conductor markers
- drums
- bass
- guitar
- keyboard
- lead
- percussion

The generated MIDI is editable in REAPER and does not require paid third-party plugins.

See [docs/FIRST_BUILD.md](docs/FIRST_BUILD.md) for the current alpha build contents and limitations.

See [docs/DESIGN_NOTES.md](docs/DESIGN_NOTES.md) for the human-fronted band direction, including The Ehaye Band mode.
