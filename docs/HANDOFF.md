# AI Band Handoff

## Where We Are

Repo and cloud mirror:

```text
\\dees-workbench\cloud-mirror\ai-band
```

GitHub:

```text
dee-elder-millenial/ai-band
```

The project is now focused on making the REAPER output sound less robotic through instrument-aware MIDI, not by piling on more notes or effects.

## Tonight's Key Discovery

The Ample Guitar M Lite Strummer can handle strumming well by itself. The generated rhythm guitar had been sending pre-arpeggiated/fake-strummed MIDI, which likely caused the plugin to strum an already-strummed pattern.

Fix committed:

```text
2075a0d Make heartland rhythm guitar strummer friendly
```

Heartland rhythm guitar now emits same-tick chord blocks, around 443 notes instead of roughly 2300 MIDI-level strum notes.

## Files To Test

```text
examples\factory-flag-thunder.mid
examples\main-street-thunder.mid
examples\porch-light-in-g-six-string-guitar.mid
```

For `porch-light-in-g-six-string-guitar.mid`, the main six-note chords are not arpeggiated in MIDI. All six chord tones start on exactly the same tick. There are separate light bass-string pulses between chord blocks.

## REAPER Test Procedure

For heartland full-band tests:

1. Import `examples\factory-flag-thunder.mid`.
2. Put Ample Guitar M Lite on `AI Guitar Player`.
3. Use Strummer mode.
4. Solo rhythm guitar first.
5. If the rhythm guitar is no longer messy, unsolo and run:
   - `ai_band_apply_reaper_audition_settings.lua`
   - `ai_band_apply_audition_mix.lua`
6. Try `drums-forward`.

For the folk guitar-only test:

1. Import `examples\porch-light-in-g-six-string-guitar.mid`.
2. Put Ample Guitar M Lite on the guitar track.
3. Try Finger mode first.
4. Try Strummer if Finger is too static.

## AI Feedback Commands

Run from the repo root and from the PowerShell tab where `OPENAI_API_KEY` is set:

```powershell
python -m ai_band.respond --cue state/live_cue.json --force-ai --output examples/ai-feedback-response.mid
```

Check local estimated API spend:

```powershell
python -m ai_band.api_budget
```

The local ledger estimates only calls made through AI Band. The OpenAI dashboard remains authoritative.

## Next Engineering Move

Do not start with lead guitar yet unless the rhythm guitar Strummer test passes.

Next likely implementation:

- Add instrument profiles for rhythm guitar.
- Route heartland rhythm guitar through `strummer-friendly chord blocks` when using Ample Strummer.
- Preserve internal MIDI strumming only as a fallback for generic instruments or non-Strummer modes.
- Then revisit lead guitar realism.
