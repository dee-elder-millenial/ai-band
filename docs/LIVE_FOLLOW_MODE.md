# Live Follow Mode

Live Follow Mode is the path toward an AI backing band that can respond to Deanna in REAPER.

There are two different capabilities here:

1. Follow instructions.
2. Listen to audio and adapt.

Instruction-following is the near-term target. Real-time audio listening is possible, but it is harder because REAPER scripts, plugins, audio buffers, model calls, and latency all have to cooperate.

## Feasible Near-Term Version

The first usable version should be command/cue driven:

- Deanna records or imports a human rhythm guitar/vocal guide.
- REAPER has a script/action for writing band instructions.
- Instructions are stored as a small JSON cue file.
- The Python generator reads the cue file.
- The bandleader updates arrangement choices.
- The generator rewrites selected MIDI parts.
- REAPER imports or refreshes those parts.

Example instructions:

```text
make bass simpler
drums bigger in chorus
keys leave more space
lead only answers vocal phrases
mute percussion in verse
make the bridge half-time
```

## Real-Time Listening Version

The longer-term version can listen to audio by analyzing short snapshots:

- tempo and beat position
- guitar/vocal activity
- section changes
- loudness and density
- chord/key hints
- rhythmic accent pattern

The AI should not try to recompose every note every audio buffer. A better model is:

- fast analysis runs continuously or on short windows
- band state updates at musical boundaries
- regeneration happens at section/bar boundaries
- emergency controls can mute, simplify, or intensify immediately

## REAPER Architecture

REAPER can be the host and controller:

- ReaScripts expose actions such as `simplify bass`, `bigger chorus`, or `follow guitar`.
- JSFX can do low-latency MIDI/audio utility work.
- Python can do heavier planning and generation outside the audio thread.
- Later, a background local service can watch cue files and regenerate MIDI.

## First Implementation Target

Create a cue file workflow:

```text
state/live_cue.json
```

The cue file should include:

- timestamp
- mode
- instruction text
- target member
- intensity
- project path when available

This is not full real-time listening yet, but it gives us the control surface for an AI band that follows direction while the project is open.

