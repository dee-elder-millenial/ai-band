# AI Band

AI Band is a REAPER-oriented toolkit for generating editable song sketches from a coordinated group of AI-assisted band members.

The first prototype is intentionally MIDI-first. A bandleader creates a shared song plan, then each member generates parts from that plan:

- AI Bandleader
- AI Drummer
- AI Bass Player
- AI Guitar Player
- AI Keyboard Player
- AI Lead Player
- AI Percussion / Extras

Phase 1 starts with deterministic player logic so the REAPER workflow is solid before model calls are added. The design leaves room for real AI models to drive arrangement, style interpretation, prompts, and regeneration commands.

## Quick Start

Generate the first 16-bar sketch:

```powershell
python -m ai_band.generate --output examples/first-sketch.mid
```

Then import `examples/first-sketch.mid` into REAPER.

Generate a custom sketch:

```powershell
python -m ai_band.generate --output examples/c-major-sketch.mid --title "C Major Sketch" --style "clean indie rock" --tempo 124 --key C --scale major
```

Generate The Ehaye Band backing-band sketch, with Deanna on lead vocal and human rhythm guitar:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --output examples/ehaye-backing-band.mid
```

Apply the latest REAPER live cue while generating:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --cue state/live_cue.json --output examples/ehaye-cue-response.mid
```

Interpret a REAPER live cue with real AI when `OPENAI_API_KEY` is set:

```powershell
python -m ai_band.ai_feedback --cue state/live_cue.json --force-ai
```

Generate from a REAPER live cue using the AI feedback interpreter:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --cue state/live_cue.json --ai-feedback --output examples/ehaye-ai-response.mid
```

Run the current cue through the full feedback loop: AI decision JSON plus response MIDI:

```powershell
python -m ai_band.respond --cue state/live_cue.json --force-ai --output examples/ai-feedback-response.mid
```

Check AI Band's local estimated API spend:

```powershell
python -m ai_band.api_budget
```

Generate a bluesy alt-country backing sketch:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --preset bluesy-alt-country --title "County Line Ghosts" --style "bluesy alt-country" --tempo 96 --key D --scale major --output examples/county-line-ghosts.mid
```

Generate a longer southern-blues backing song:

```powershell
python -m ai_band.generate --mode ehaye --no-ai-rhythm-guitar --preset southern-blues --title "Hard Flag Blues" --style "southern blues" --tempo 86 --key E --scale minor --output examples/hard-flag-blues.mid
```

Generate the same southern-blues song with AI rhythm guitar included:

```powershell
python -m ai_band.generate --mode ehaye --ai-rhythm-guitar --preset southern-blues --title "Hard Flag Blues" --style "southern blues" --tempo 86 --key E --scale minor --output examples/hard-flag-blues-with-rhythm-guitar.mid
```

Generate a harder-rocking heartland-rock audition song:

```powershell
python -m ai_band.generate --preset heartland-rock --title "Main Street Thunder" --style "heartland hard rock" --tempo 118 --key E --scale major --output examples/main-street-thunder.mid
```

Create the Phase 1 alpha build package:

```powershell
python -m ai_band.build
```

The build command writes:

- `build/ai-band-phase1-alpha/`
- `dist/ai-band-phase1-alpha-0.1.0.zip`

Run the current smoke test:

```powershell
python -m unittest discover -s tests
```

## Project Shape

```text
ai-band/
  TODO.md
  README.md
  pyproject.toml
  Scripts/
    ai_band_import_generated_midi.lua
    ai_band_add_sound_check_synths.lua
    ai_band_lower_track_levels.lua
    ai_band_apply_reaper_audition_settings.lua
    ai_band_setup_rough_tones.lua
    ai_band_apply_audition_mix.lua
    ai_band_ehaye_audition_setup.lua
    ai_band_county_line_audition_setup.lua
    ai_band_hard_flag_blues_audition_setup.lua
    ai_band_hard_flag_blues_with_guitar_audition_setup.lua
    ai_band_main_street_thunder_audition_setup.lua
    ai_band_tone_helpers.lua
    ai_band_write_live_cue.lua
  Effects/
    AI Band Humanizer.jsfx
    AI Band GM Drum Synth.jsfx
  ai_band/
    api_budget.py
    build.py
    bandleader.py
    ai_feedback.py
    generate.py
    live_cue.py
    midi.py
    respond.py
    song_state.py
    members/
      drummer.py
      bassist.py
      guitarist.py
      keyboardist.py
      lead.py
      percussion.py
  docs/
    FIRST_BUILD.md
    LIVE_FOLLOW_MODE.md
    REAPER.md
    TONE_LAYER.md
  state/
    .gitkeep
  examples/
    .gitkeep
```

## Current Milestone

The current prototype generates a type-1 Standard MIDI File with separate tracks for:

- conductor markers
- drums
- bass
- guitar
- keyboard
- lead
- percussion

The generated MIDI is editable in REAPER and does not require paid third-party plugins.

See [docs/FIRST_BUILD.md](docs/FIRST_BUILD.md) for the current alpha build contents and limitations.

See [docs/DESIGN_NOTES.md](docs/DESIGN_NOTES.md) for the human-fronted band direction, including The Ehaye Band mode.

For a less toy-like REAPER audition setup, see [docs/TONE_LAYER.md](docs/TONE_LAYER.md).

For the longer-term desktop/mobile/live-rig direction, see [docs/PORTABILITY.md](docs/PORTABILITY.md).
