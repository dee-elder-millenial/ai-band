# AI Band Project Dashboard

Last updated: 2026-06-04

## Current Status

AI Band is a REAPER-first MIDI backing-band prototype. The project can generate editable multi-track MIDI sketches, apply REAPER audition instrument/mix defaults, accept live cue instructions, and optionally use OpenAI to interpret those cues into generation controls.

The current sound-quality focus is reducing robotic MIDI behavior by making the generator cooperate with the installed instruments instead of fighting them.

The Python engine is now split into composition and performance rendering:

- `ai_band.generate.compose_tracks()` creates the existing song/member MIDI structure.
- `ai_band.performance.render_performance()` adds the audition performance layer: sample-instrument hints, mixer CCs, reverb/delay sends, instrument roles, and optional groove/swing/velocity humanization.
- `ai_band.generate.build_tracks()` remains the normal public path and returns rendered tracks.
- `ai_band.sound_guy.advise_sound_guy()` is the first non-playing AI Sound Guy pass. It chooses render/mix defaults from preset and listening notes, then writes an optional metadata track into the MIDI.

## Latest Decision

Rhythm guitar is the current priority.

Ample Guitar M Lite's Strummer is doing useful performance work. The generator should not pre-arpeggiate or fake-strum heartland rhythm guitar MIDI for that workflow. Instead, heartland rhythm guitar now sends clean same-tick chord blocks so the plugin can perform the actual strumming.

Future arrangement workflow should support adding performers and musical parts one at a time. The target behavior is: keep the current song structure, add a new role or track such as second guitar, organ pad, sax support, tambourine, or harmony guide, and preserve existing parts while auditioning the newcomer.

AI Sound Guy is now started as a non-playing band member. Current job: protect what is working, pick first-pass mix/render settings, and route rhythm-guitar troubleshooting toward the right profile. Example:

```powershell
python -m ai_band.generate --preset heartland-rock --title "Sound Guy Pass" --style "heartland hard rock" --tempo 118 --key E --scale major --sound-guy --sound-note "bass is killing it, rhythm guitar sounds strange" --output examples/sound-guy-pass.mid
```

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

Rhythm guitar needs A/B diagnosis because the bass has improved, but the guitar still sounds strange through the current plugin setup.

Import and compare these three files with the same Ample Guitar setup:

- `examples/rhythm-guitar-current-strummer.mid`
  - Current default Ample Strummer chord-block profile.
  - 443 rhythm guitar notes.
- `examples/rhythm-guitar-simple-blocks.mid`
  - Simpler chord-recognition blocks with less color/register complexity.
  - 355 rhythm guitar notes.
- `examples/rhythm-guitar-internal-strum.mid`
  - MIDI-level fallback strumming instead of relying on the plugin Strummer.
  - 1625 rhythm guitar notes.

Test procedure:

1. Put `Ample Guitar M Lite` on `AI Guitar Player`.
2. Solo the rhythm guitar track first.
3. For the two block profiles, try the plugin Strummer mode.
4. For `internal-strum`, try the non-Strummer/Finger mode first.
5. If one file clearly wins, make that profile the heartland default.
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
