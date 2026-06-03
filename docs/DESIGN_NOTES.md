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
