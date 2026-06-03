# REAPER Notes

AI Band starts as a MIDI sketch generator. The generated `.mid` files can be imported into REAPER and edited like normal MIDI.

## Generate A Sketch

From the repo root:

```powershell
python -m ai_band.generate --output examples/first-sketch.mid
```

Optional controls:

```powershell
python -m ai_band.generate --output examples/c-major-sketch.mid --title "C Major Sketch" --style "clean indie rock" --tempo 124 --key C --scale major
```

The Ehaye Band backing-band mode:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --output examples/ehaye-backing-band.mid
```

## Import The MIDI

Option 1: drag `examples/first-sketch.mid` into REAPER.

Option 2: install the helper script:

1. In REAPER, choose `Options > Show REAPER resource path in explorer/finder`.
2. Copy `Scripts/ai_band_import_generated_midi.lua` into the REAPER `Scripts` folder.
3. In REAPER, open `Actions > Show action list`.
4. Choose `New action > Load ReaScript`.
5. Select `ai_band_import_generated_midi.lua`.
6. Run the action and choose the generated `.mid` file.

## Quick Sound Check

If the MIDI imports and plays but you hear silence, the file probably has notes but the tracks do not have instruments yet.

Install the sound-check helper script:

1. Copy `Scripts/ai_band_add_sound_check_synths.lua` into the REAPER `Scripts` folder.
2. In REAPER, open `Actions > Show action list`.
3. Choose `New action > Load ReaScript`.
4. Select `ai_band_add_sound_check_synths.lua`.
5. Import the generated AI Band MIDI.
6. Run `ai_band_add_sound_check_synths.lua`.

The script adds REAPER's built-in `ReaSynth` to each playable AI Band track and skips the bandleader marker track. This is only for testing that MIDI notes are reaching instruments; it is not the final sound of the product.

## Install JSFX Helpers

JSFX effects belong in REAPER's resource-path `Effects` folder.

Copy:

```text
Effects/AI Band Humanizer.jsfx
```

to:

```text
<REAPER resource path>/Effects/
```

Then choose `FX > Add FX` and search for `AI Band Humanizer`.

## Current Prototype Behavior

The first generator creates:

- one bandleader/marker track
- one drum track using General MIDI drum notes
- one bass track
- one guitar track
- one keyboard track
- one lead track
- one percussion extras track

REAPER may ask how to import the MIDI file. Choose the option that preserves separate tracks when available.

## Phase 1 Alpha Build

From the repo root, run:

```powershell
python -m ai_band.build
```

This creates `dist/ai-band-phase1-alpha-0.1.0.zip`, including the generated demo MIDI, REAPER helper script, JSFX humanizer, docs, tests, and source code.
