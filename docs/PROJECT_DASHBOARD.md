# AI Band Project Dashboard

Last updated: 2026-06-04

## Current Status

AI Band is a REAPER-first MIDI backing-band prototype. The project can generate editable multi-track MIDI sketches, apply REAPER audition instrument/mix defaults, accept live cue instructions, and optionally use OpenAI to interpret those cues into generation controls.

The current sound-quality focus is reducing robotic MIDI behavior by making the generator cooperate with the installed instruments instead of fighting them.

The Python engine is now split into composition and performance rendering:

- `ai_band.generate.compose_tracks()` creates the existing song/member MIDI structure.
- `ai_band.performance.render_performance()` adds the audition performance layer: sample-instrument hints, mixer CCs, reverb/delay sends, instrument roles, and optional groove/swing/velocity humanization.
- `ai_band.generate.build_tracks()` remains the normal public path and returns rendered tracks.

## Latest Decision

Rhythm guitar is the current priority.

Ample Guitar M Lite's Strummer is doing useful performance work. The generator should not pre-arpeggiate or fake-strum heartland rhythm guitar MIDI for that workflow. Instead, heartland rhythm guitar now sends clean same-tick chord blocks so the plugin can perform the actual strumming.

## Latest Working Artifacts

- `examples/factory-flag-thunder.mid`
  - Original Boss-adjacent heartland-rock audition sketch.
  - Rhythm guitar regenerated as strummer-friendly chord blocks.
- `examples/main-street-thunder.mid`
  - Earlier heartland-rock audition sketch.
  - Rhythm guitar regenerated as strummer-friendly chord blocks.
- `examples/porch-light-in-g-six-string-guitar.mid`
  - Guitar-only folk test in G major.
  - Main six-note chord blocks start exactly on the same MIDI tick.
  - Includes light bass-string pulses between chord blocks.

Generated MIDI files are intentionally ignored by Git, but they live in the cloud-mirror folder for REAPER testing.

## Current REAPER Test

1. Import `examples/factory-flag-thunder.mid`.
2. Put `Ample Guitar M Lite` on `AI Guitar Player`.
3. Enable the plugin's Strummer mode.
4. Solo the rhythm guitar track first.
5. Confirm the rhythm track no longer sounds like a double-arpeggiated mess.
6. Then run:
   - `ai_band_apply_reaper_audition_settings.lua`
   - `ai_band_apply_audition_mix.lua`
7. Try `drums-forward` for the full-band heartland test.

## AI Feedback Loop

The first real AI feedback loop is implemented:

```powershell
python -m ai_band.respond --cue state/live_cue.json --force-ai --output examples/ai-feedback-response.mid
```

It writes:

- `state/last_ai_feedback.json`
- `examples/ai-feedback-response.mid`

Local estimated API spend:

```powershell
python -m ai_band.api_budget
```

Current observed local estimate: about `$0.0004 / $5.00`, 1 tracked call.

## Next Session

1. Ear-test the strummer-friendly rhythm guitar in REAPER.
2. Try opt-in render feel on a copy, for example `--groove 0.35 --swing 0.10 --velocity-humanize 0.50`, and listen for whether it helps or smears the pocket.
3. If the Strummer profile works, expand instrument presets into an explicit user-selectable profile:
   - Ample Strummer: chord blocks.
   - Ample Finger/Main: picked/arpeggiated MIDI.
   - Generic fallback: internal strum simulation.
4. After rhythm guitar is stable, return to lead guitar realism.
5. Keep every good listening lesson as a generator/process change, not a one-off MIDI edit.
