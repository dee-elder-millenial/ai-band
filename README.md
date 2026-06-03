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
