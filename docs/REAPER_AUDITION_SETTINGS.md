# REAPER Audition Settings

These settings are for making AI Band sketches easier to judge in REAPER before the generator is musically finished.

## Fast Path

1. Import or set up the generated MIDI.
2. Run `ai_band_apply_reaper_audition_settings.lua`.
3. Run `ai_band_apply_audition_mix.lua`.
4. Start with `warmer-room` if the parts sound fake or dry.
5. Try `lead-back` if the lead guitar crowds the song.
6. Try `drums-forward` if the groove disappears.

## Check First

- Master fader should not be above unity.
- Playback rate should be `1.0`.
- The master meter should not stay red.
- Monitor FX should not contain a loud enhancer, clipper, or amp sim.
- MT-PowerDrumKit may need to be opened and activated before it plays.
- Make sure each MIDI track is feeding the intended instrument, not a fallback synth.

## Starting Mix Targets

- Drums: center, loud enough to carry the pulse, with some room but not washed out.
- Bass: center and supportive, not louder than the kick/snare relationship.
- Rhythm guitar: panned left, lower mids present, less bright than the lead.
- Keys or sax pad: panned right, tucked behind guitar and vocal space.
- Lead guitar: slightly right, quieter than instinct says, with room/reverb to hide MIDI edges.
- Percussion extras: low and wide enough to add motion without sounding like a second drummer.

## When It Sounds Robotic

- Lower the lead guitar before changing anything else.
- Add a little room to guitar and keys instead of turning them up.
- Use darker guitar tones before brighter ones.
- Keep bass compression gentle and avoid excessive low-end gain.
- Prefer pads with slow attack for keys/sax support.
- Do not judge the MIDI through ReaSynth unless you are only checking note routing.

## Current Rough Instrument Map

- `AI Drummer`: `MT-PowerDrumKit`
- `AI Bass Player`: `Ample Bass P Lite II`
- `AI Guitar Player`: `Ample Guitar M II Lite`
- `AI Keyboard Player`: `Splice INSTRUMENT`
- `AI Lead Player`: `Ample Guitar M II Lite`
- `AI Percussion Extras`: `MT-PowerDrumKit`
