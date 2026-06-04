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

## Current Cue Response

The current build can read the latest cue:

```powershell
python -m ai_band.live_cue
```

It can also apply the cue while generating with the deterministic keyword interpreter:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --cue state/live_cue.json --output examples/ehaye-cue-response.mid
```

## Real AI Feedback Loop

The first real AI integration is an optional bandleader interpreter. It reads the REAPER cue, asks an OpenAI model to map the instruction into generation controls, and falls back to the deterministic interpreter when no API key is available.

Set the API key in the same PowerShell window where you will run AI Band:

```powershell
$env:OPENAI_API_KEY = Get-Clipboard
```

Then test the AI interpreter directly:

```powershell
python -m ai_band.ai_feedback --cue state/live_cue.json --force-ai
```

Generate a cue response MIDI using real AI with the lower-level generator:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --cue state/live_cue.json --ai-feedback --output examples/ehaye-ai-response.mid
```

Run the full feedback loop in one command:

```powershell
python -m ai_band.respond --cue state/live_cue.json --force-ai --output examples/ai-feedback-response.mid
```

This writes:

- `state/last_ai_feedback.json`: the AI decision, selected controls, rationale, and budget estimate.
- `examples/ai-feedback-response.mid`: the MIDI response to import into REAPER.

Check AI Band's local estimated API spend:

```powershell
python -m ai_band.api_budget
```

The local ledger is `state/api_usage.json`. It is intentionally ignored by Git and estimates only calls made through AI Band. The OpenAI billing dashboard remains the source of truth.

The default local budget is `$5.00`. Override it for a shell session:

```powershell
$env:AI_BAND_API_BUDGET_USD = "5.00"
```

The default model is `gpt-5.4-mini`, chosen as a lower-cost interpreter. Override it when needed:

```powershell
$env:AI_BAND_OPENAI_MODEL = "gpt-5.5"
```

Initial cue behavior:

- `simplify bass` makes the bass part sparser.
- `keys leave more space` thins keyboard hits further.
- `drums bigger` raises chorus drum intensity.
- `lead answer the vocal` makes lead phrases sparser.

When `--ai-feedback` is enabled, these same controls can be triggered by more natural instructions such as:

- `the keys and lead are stepping on my vocal`
- `make the drummer push the chorus harder`
- `bass is too busy under the verse`
- `lead guitar should answer me, not talk over me`

## Current Test Procedure

1. In REAPER, run `ai_band_write_live_cue.lua` and enter a cue.
2. In the PowerShell tab where `OPENAI_API_KEY` is set, run:

```powershell
python -m ai_band.respond --cue state/live_cue.json --force-ai --output examples/ai-feedback-response.mid
```

3. Confirm the command says `AI feedback source: openai`.
4. Import `examples/ai-feedback-response.mid` into REAPER.
5. Run `ai_band_apply_reaper_audition_settings.lua`.
6. Run `ai_band_apply_audition_mix.lua`.
