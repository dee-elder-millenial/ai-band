# Tone Layer

The generator writes MIDI. REAPER needs instruments on those MIDI tracks before the sketch sounds like music.

Sound quality work should happen in REAPER first. Standalone desktop, mobile, and plugin ideas stay downstream until the backing band feels convincing through real audition instruments.

The emergency sound-check script uses ReaSynth everywhere. That is useful for proving MIDI routing, but it sounds toy-like. The rough tone layer is the next step.

## Rough Tone Setup

Install the JSFX drum helper:

```text
Effects/AI Band GM Drum Synth.jsfx
```

Copy it into REAPER's resource-path `Effects` folder.

Install the REAPER script:

```text
Scripts/ai_band_setup_rough_tones.lua
Scripts/ai_band_tone_helpers.lua
```

Copy both files into REAPER's resource-path `Scripts` folder and load `ai_band_setup_rough_tones.lua` from `Actions > Show action list > New action > Load ReaScript`.

After importing `examples/ehaye-backing-band.mid`, run:

```text
ai_band_setup_rough_tones.lua
```

## What It Does

- AI Drummer: prefers `MT-PowerDrumKit (MANDA AUDIO)`
- AI Percussion Extras: prefers `MT-PowerDrumKit (MANDA AUDIO)` at a lower level
- AI Bass Player: prefers `Ample Bass P Lite II (Ample Sound)`
- AI Keyboard Player: prefers `Splice INSTRUMENT (Splice)`
- AI Lead Player: prefers `Ample Guitar M II Lite (Ample Sound)`
- AI Guitar Player: prefers `Ample Guitar M II Lite (Ample Sound)` if present

This is still a rough audition layer, not the final product tone.

If a preferred instrument cannot be loaded, the script falls back to the built-in rough tone chain.

## One-Click Ehaye Audition

For the fastest audition path, copy these scripts into REAPER's `Scripts` folder:

```text
Scripts/ai_band_ehaye_audition_setup.lua
Scripts/ai_band_tone_helpers.lua
```

Then load and run:

```text
ai_band_ehaye_audition_setup.lua
```

It imports the current cloud-mirror `examples/ehaye-backing-band.mid`, applies rough tones, and labels the project.

## Tone Direction

Future tone work should move toward:

- real drum samples or a drum sampler
- bass instrument or amp-like bass chain
- sparse warm keyboard texture
- lead sound that supports the vocal instead of dominating it
- automatic gain staging and master safety

## Current Listening Priorities

Use REAPER as the granular editing lab:

- adjust bass weight and note timing against the kick
- bring drums forward without clipping or harshness
- choose a keyboard pad that leaves room for vocal and rhythm guitar
- make lead phrases feel less robotic with timing, bends, rests, and shorter motifs
- keep each change traceable back to either a generator rule or an instrument-profile setting

## Starter Effects

`ai_band_tone_helpers.lua` includes a first rough effects pass for audition scripts that opt in:

- drums, bass, guitar, keyboard/sax, and lead can get ReaComp
- drums, guitar, keyboard/sax, lead, and percussion can get ReaVerbate
- opted-in audition scripts set conservative wet/dry starter mixes so the parts get a little depth without hiding the MIDI

These are editable REAPER starter effects, not a finished mix. The goal is to start exploring compression, room, and space while keeping the generated MIDI and instrument choices easy to inspect.
