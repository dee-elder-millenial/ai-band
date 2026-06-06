# AI Band Handoff

## Where We Are

Repo and cloud mirror:

```text
\\dees-workbench\cloud-mirror\ai-band
```

GitHub:

```text
dee-elder-millenial/ai-band
```

The project is now focused on making the REAPER output sound less robotic through instrument-aware MIDI, natural musician-language AI cue interpretation, and a REAPER workflow that can refresh generated MIDI without reloading instruments.

## Latest Known Pushed Commit

```text
109bfa6 Add REAPER response MIDI refresh action
```

Recent commits:

```text
109bfa6 Add REAPER response MIDI refresh action
a1f62b0 Make AI cue interpreter musician-friendly
f36aa21 Add audible live cue controls
598252d Stamp live cues onto REAPER timeline
d1356e0 Add slow Texas alt-country preset
```

Verification at wrap-up:

```text
python -B -m unittest discover -s tests
69 passing tests

python -B -m compileall ai_band tests
OK

python -B -m ai_band.build
dist\ai-band-phase1-alpha-0.1.0.zip rebuilt
```

## Current Working Direction

Do not hand-code thousands of cue phrases. Let the user talk naturally to the band, then map that language into a smaller musical intent/control layer.

Current real-AI feedback path:

- User writes a natural cue such as `bass player, walk me up into the chorus`.
- `ai_band.ai_feedback` asks OpenAI to respond like a bandmate/producer.
- The model returns `musician_reply`, `musical_plan`, `section_scope`, `confidence`, and current renderable controls.
- `ai_band.respond` writes `state/last_ai_feedback.json` and `examples/ai-feedback-response.mid`.

Keep future memory/training work lightweight:

- Log cue, song context, AI interpretation, render controls, and user feedback as JSONL/SQLite-style structured records.
- Retrieve only relevant examples for future prompts.
- Do not load audio libraries or cue history into RAM as a giant local model.
- Let REAPER/plugins stream samples; AI Band should store decisions and patterns.

## Files To Test

```text
examples\ai-feedback-response.mid
examples\sunshine-pocket-jam.mid
examples\llano-county-rain.mid
examples\factory-flag-thunder.mid
examples\main-street-thunder.mid
```

Generated MIDI is ignored by Git but lives in the cloud-mirror checkout for REAPER testing.

Latest new jam:

```powershell
python -m ai_band.generate --preset funk-reggae-jam --title "Sunshine Pocket Jam" --style "upbeat funk reggae jam with fun guitar" --tempo 104 --key A --scale major --sound-guy --sound-note "real jam, funky lick, fun guitar, upbeat with a little reggae influence" --output examples/sunshine-pocket-jam.mid
```

`funk-reggae-jam` is an upbeat reusable preset with a syncopated bass hook, offbeat guitar chops, clav/organ-style keys, bright percussion, and short fun lead phrases.

## REAPER Test Procedure

For the new live cue refresh bridge:

1. Open an already-instrumented AI Band REAPER project.
2. Run `ai_band_write_live_cue.lua` and enter a natural cue.
3. In PowerShell from the repo root, run:

```powershell
python -m ai_band.respond --cue state/live_cue.json --force-ai --output examples/ai-feedback-response.mid
```

4. Confirm the command reports `AI feedback source: openai`.
5. In REAPER, run `ai_band_refresh_response_midi.lua`.
6. The refresh script imports the response MIDI into temporary tracks, moves the new MIDI items onto matching existing AI Band tracks, and deletes the temporary tracks.
7. Existing instruments, FX, volume, and pan should stay in place.

Important: this is a manual live-update bridge, not a background watcher yet. REAPER will not hear the new MIDI until the refresh action runs.

## AI Feedback Commands

Run from the repo root and from the PowerShell tab where `OPENAI_API_KEY` is set:

```powershell
python -m ai_band.respond --cue state/live_cue.json --force-ai --output examples/ai-feedback-response.mid
```

Check local estimated API spend:

```powershell
python -m ai_band.api_budget
```

The local ledger estimates only calls made through AI Band. The OpenAI dashboard remains authoritative.

## Project Dashboard Update Procedure

The Workbench project dashboard now has an ingest tool. Do not hand-edit dashboard `data/projects.json` for normal project status updates.

From AI Band, create a small JSON payload under ignored `state/`, for example:

```text
state/dashboard-ai-band-update.json
```

Then update the dashboard with:

```powershell
python H:\project-dashboard\bin\project-dashboard-ingest "\\dees-workbench\cloud-mirror\ai-band\state\dashboard-ai-band-update.json" --dashboard-root H:\project-dashboard --dry-run
python H:\project-dashboard\bin\project-dashboard-ingest "\\dees-workbench\cloud-mirror\ai-band\state\dashboard-ai-band-update.json" --dashboard-root H:\project-dashboard
```

This validates the update, writes `data/projects.json` atomically, and creates a timestamped backup under `H:\project-dashboard\data\backups\`.

Latest dashboard ingest result:

```text
mode=merge, added=0, updated=1, projects=16
backup=\\dees-workbench\cloud-mirror\project-dashboard\data\backups\projects.20260605T014032Z.json
```

The dashboard repo currently has unrelated unpublished UI and data changes. Do not commit or push dashboard changes blindly.

## Next Engineering Move

Test the manual live update bridge in REAPER first.

Next likely implementation:

- If refresh works, consider a REAPER-side action/watcher that runs the response command and refresh action as a tighter loop.
- Add cue history logging with user feedback so natural language examples become training/retrieval fuel.
- Continue rhythm guitar/plugin profile diagnosis.
- Then revisit lead guitar realism.
