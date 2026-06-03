# REAPER Notes

AI Band starts as a MIDI sketch generator. The generated `.mid` files can be imported into REAPER and edited like normal MIDI.

## Generate A Sketch

From the repo root:

```powershell
python -m ai_band.generate --output examples/first-sketch.mid
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

