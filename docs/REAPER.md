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

Option 1a: for The Ehaye Band backing sketch, load and run:

```text
Scripts/ai_band_ehaye_audition_setup.lua
```

That script imports `examples/ehaye-backing-band.mid` from the cloud mirror, applies rough tones, and labels the project.

Option 2: install the helper script:

1. In REAPER, choose `Options > Show REAPER resource path in explorer/finder`.
2. Copy `Scripts/ai_band_import_generated_midi.lua` into the REAPER `Scripts` folder.
3. In REAPER, open `Actions > Show action list`.
4. Choose `New action > Load ReaScript`.
5. Select `ai_band_import_generated_midi.lua`.
6. Run the action and choose the generated `.mid` file.

## Quick Sound Check

If the MIDI imports and plays but you hear silence, the file probably has notes but the tracks do not have instruments yet.

Recommended rough-tone setup:

1. Copy `Effects/AI Band GM Drum Synth.jsfx` into REAPER's resource-path `Effects` folder.
2. Copy `Scripts/ai_band_setup_rough_tones.lua` and `Scripts/ai_band_tone_helpers.lua` into REAPER's resource-path `Scripts` folder.
3. In REAPER, open `Actions > Show action list`.
4. Choose `New action > Load ReaScript`.
5. Select `ai_band_setup_rough_tones.lua`.
6. Import the generated AI Band MIDI.
7. Run `ai_band_setup_rough_tones.lua`.

This uses a simple AI Band drum synth for drums/percussion and calmer ReaSynth settings for bass, keys, lead, and optional guitar.

Install the sound-check helper script:

1. Copy `Scripts/ai_band_add_sound_check_synths.lua` into the REAPER `Scripts` folder.
2. In REAPER, open `Actions > Show action list`.
3. Choose `New action > Load ReaScript`.
4. Select `ai_band_add_sound_check_synths.lua`.
5. Import the generated AI Band MIDI.
6. Run `ai_band_add_sound_check_synths.lua`.

The script adds REAPER's built-in `ReaSynth` to each playable AI Band track and skips the bandleader marker track. This is only for testing that MIDI notes are reaching instruments; it is not the final sound of the product.

If the sound-check tracks clip or hit the master too hard, run the updated `ai_band_add_sound_check_synths.lua` again. It lowers track faders and cools existing ReaSynth instances. You can also load and run:

```text
Scripts/ai_band_lower_track_levels.lua
```

That script only lowers and pans the imported AI Band tracks. It does not add or remove instruments.

The current sound-check mix intentionally pushes drums a little forward and keeps keys quieter because the first listening pass showed the keys crowding the backing arrangement.

## Install JSFX Helpers

JSFX effects belong in REAPER's resource-path `Effects` folder.

Copy:

```text
Effects/AI Band Humanizer.jsfx
Effects/AI Band GM Drum Synth.jsfx
```

to:

```text
<REAPER resource path>/Effects/
```

Then choose `FX > Add FX` and search for `AI Band Humanizer` or `AI Band GM Drum Synth`.

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

This creates `dist/ai-band-phase1-alpha-0.1.0.zip`, including the generated demo MIDI, REAPER helper scripts, JSFX helpers, docs, tests, and source code.

## Live Cue Scaffold

To write an instruction cue from REAPER:

1. Copy `Scripts/ai_band_write_live_cue.lua` into REAPER's resource-path `Scripts` folder.
2. Load it from `Actions > Show action list > New action > Load ReaScript`.
3. Run `ai_band_write_live_cue.lua`.
4. Enter an instruction such as:

```text
simplify bass,bass,0.7
```

This writes:

```text
state/live_cue.json
```

The current build can read that cue with:

```powershell
python -m ai_band.live_cue
```

The current build can apply that cue while generating a response MIDI:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --cue state/live_cue.json --output examples/ehaye-cue-response.mid
```
