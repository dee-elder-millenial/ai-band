# First Build: Phase 1 Alpha

This is the first usable AI Band build. It is a deterministic MIDI-first prototype that proves the core REAPER workflow:

1. The bandleader creates a shared song plan.
2. Individual band members generate separate MIDI parts from that plan.
3. The project exports a type-1 Standard MIDI File that REAPER can import as editable MIDI.
4. REAPER helper files are packaged with the build.

## Build Command

From the repo root:

```powershell
python -m ai_band.build
```

Expected outputs:

```text
build/ai-band-phase1-alpha/
dist/ai-band-phase1-alpha-0.1.0.zip
```

## Build Contents

The zip contains:

- source code for the prototype generator
- `examples/first-sketch.mid`
- `BUILD_MANIFEST.json`
- REAPER import helper script
- REAPER sound-check synth helper script
- REAPER track-level safety helper script
- REAPER rough-tone setup script
- JSFX MIDI humanizer helper
- JSFX GM drum synth helper
- REAPER setup notes
- smoke tests
- project TODO

## Current Musical Behavior

The generated song is a 16-bar sketch with:

- Intro
- Verse
- Chorus
- Outro

The generated tracks are:

- AI Bandleader markers
- AI Drummer
- AI Bass Player
- AI Guitar Player
- AI Keyboard Player
- AI Lead Player
- AI Percussion Extras

## What Is Real AI vs Prototype Logic

This first build uses deterministic player logic. That is intentional: it gives us reliable MIDI generation, REAPER import behavior, and a stable shared song-state contract.

The next layer can add real model calls for:

- interpreting natural-language style prompts
- changing the bandleader's arrangement plan
- setting member personalities
- regenerating one member at a time
- critiquing and revising generated parts

## Known Limitations

- No real model/API calls yet.
- The song form is fixed to 16 bars.
- MIDI instruments depend on whatever REAPER routes the imported tracks to.
- Guitar, keyboard, and lead parts are simple sketch parts, not performance-grade instrument emulations.
- The JSFX humanizer is a helper effect, not required for generation.
