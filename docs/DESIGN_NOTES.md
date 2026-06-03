# Design Notes

## Human-Fronted Band

AI Band should support a human-fronted workflow, not only fully generated songs.

The key use case is The Ehaye Band:

- Deanna is the lead singer.
- Deanna is the rhythm guitarist.
- The AI members act as backing bandmates.

This changes the product direction in an important way. The AI band should be able to generate around a human guide performance, especially a rhythm guitar or vocal/rhythm sketch.

## Product Implications

- AI rhythm guitar must be optional.
- The bandleader should be able to follow a human-provided song structure.
- Drums and bass should support the human rhythm guitar, not overwrite it.
- Lead guitar should fill between vocal phrases instead of playing constantly.
- Keyboard and percussion should be texture layers unless invited forward.
- Future audio analysis should detect or accept tempo, key, chords, section boundaries, and groove feel from a guide track.
- Live control should start with explicit instructions and cues before attempting true real-time audio listening.

## MVP Direction

Before full audio analysis exists, the product can support this workflow with manual inputs:

- tempo
- key
- chord progression
- section map
- human rhythm guitar track reference
- vocal presence sections

Then the AI members can generate parts around those constraints.

## Current CLI Support

The generator supports an early backing-band mode:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --output examples/ehaye-backing-band.mid
```

In `ehaye` mode, AI rhythm guitar is off by default so the generated arrangement leaves room for Deanna's rhythm guitar part. It can be forced back on with `--ai-rhythm-guitar`.

## First Listening Notes

Early REAPER audition feedback:

- overall level must stay safe and conservative
- drums need to be easier to hear in the audition mix
- lead is close enough to keep for now
- keys should be sparse because they can crowd the backing arrangement
- the backing-band direction is starting to work
- the first ReaSynth-only audition sounded like The Legend of Zelda, so rough tone setup needs separate drum/percussion treatment and calmer synth settings
- with better instruments, the bass was a little heavy and slightly off, so backing mode should keep bass simpler and more kick-locked
- lead guitar sounded robotic, so generated lead needs phrase gaps, varied timing, and less repetition
- current preferred audition instruments are MT-PowerDrumKit, Ample Bass P Lite II, Splice INSTRUMENT, and Ample Guitar M II Lite
- added a bluesy alt-country preset for rootsy backing sketches without copying a specific band or song
- added a longer southern-blues preset for protest-song energy without requiring lyrics

## Live Follow Direction

The AI band should eventually feel like it can listen and respond, but the first useful version should follow explicit instructions from REAPER:

- write a cue such as "simplify bass" or "drums bigger in chorus"
- let the bandleader interpret the cue
- regenerate only the affected member or section
- update the MIDI in REAPER

True audio listening should come after this control loop exists. It should analyze snapshots and update at musical boundaries rather than trying to call a slow AI model inside the audio thread.
