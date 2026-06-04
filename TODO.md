# AI Band TODO

## Phase 1: Individual Band Members

Goal: build the first working versions of each AI band member as separate, testable REAPER-oriented modules. Each member should generate useful MIDI parts from the same shared song state: tempo, key, chords, section, bar position, energy, and style.

### Shared Phase 1 Foundation

- [ ] Define the shared song state format.
- [ ] Define section types: intro, verse, pre-chorus, chorus, bridge, breakdown, outro.
- [ ] Define common musical controls: style, tempo, key, scale, chords, swing, density, humanize, and energy.
- [ ] Create a minimal REAPER project generation script.
- [ ] Create tracks for each AI member automatically.
- [ ] Generate MIDI items into the correct tracks.
- [ ] Add REAPER regions or markers for song sections.
- [ ] Add a simple command-line or ReaScript entrypoint for generating a band sketch.

### AI Bandleader

- [ ] Generate the overall song structure.
- [ ] Choose or accept tempo, key, scale, and chord progression.
- [ ] Assign each band member a role for every section.
- [ ] Control section-level energy, density, and dynamics.
- [ ] Decide when parts should enter, drop out, simplify, or intensify.
- [ ] Coordinate drummer and bass player groove priorities.
- [ ] Coordinate guitar and keyboard voicings so they do not overcrowd each other.
- [ ] Decide when the lead player gets hooks, fills, or solos.
- [ ] Reuse motifs across sections so the song feels intentional.
- [ ] Store the shared song state that every member reads from.

### AI Sound Guy

- [x] Add a first deterministic Sound Guy pass that chooses render/mix settings from preset and listening notes.
- [x] Let Sound Guy choose a rhythm-guitar diagnostic profile when the plugin sounds strange.
- [x] Add a non-playing `AI Sound Guy` MIDI metadata track when enabled.
- [ ] Let Sound Guy write REAPER mix-profile recommendations directly into audition scripts.
- [ ] Add EQ/compression preset decisions per track.
- [ ] Add exported-mix or REAPER snapshot analysis so Sound Guy can react to actual audio balance.
- [ ] Preserve musician decisions that are working, such as a strong bass pocket, unless the user asks to change them.

### Human Frontperson / The Ehaye Band Mode

- [ ] Treat Deanna as the lead singer and rhythm guitarist by default.
- [ ] Let the AI band generate around a human rhythm guitar part instead of replacing it.
- [ ] Support importing or recording a human guide track.
- [ ] Extract or accept tempo, section boundaries, key, chords, and groove feel from the human guide.
- [ ] Let the AI drummer, bass player, keyboard player, lead player, and percussion extras follow the human performance.
- [ ] Keep AI rhythm guitar optional so it does not fight the human rhythm guitar part.
- [ ] Add controls for "support the singer", "follow my guitar", and "fill the empty space".
- [ ] Preserve a mode for The Ehaye Band where the AI members act as backing bandmates.

### AI Drummer

- [ ] Generate basic kick, snare, and hi-hat patterns.
- [ ] Support style presets: rock, funk, pop, metal, hip-hop, electronic.
- [ ] Lock groove to tempo and section energy.
- [ ] Add fill generation at section transitions.
- [ ] Add velocity variation and timing humanize.
- [ ] Add controls for complexity, swing, ghost notes, and fill frequency.
- [ ] Output General MIDI drum notes by default.

### AI Bass Player

- [ ] Generate basslines from chord progressions.
- [ ] Lock bass rhythm to the drummer's kick pattern.
- [ ] Support root-note, walking, syncopated, octave, and riff-based modes.
- [ ] Add note length and articulation variation.
- [ ] Add controls for movement, density, octave range, and groove tightness.
- [ ] Avoid clashing with chord changes and section boundaries.
- [ ] Output monophonic MIDI by default.

### AI Guitar Player

- [ ] Generate rhythm guitar chord parts.
- [ ] Support power chords, open chords, barre-style voicings, arpeggios, and muted strums.
- [ ] Generate simple riffs from the current key and chord tones.
- [ ] Add controls for strum density, palm mute amount, register, and distortion-friendly spacing.
- [ ] Add variation between verse and chorus parts.
- [ ] Leave rhythmic space for vocals or lead instruments.
- [ ] Output MIDI suitable for guitar VSTs or sampled instruments.

### AI Keyboard Player

- [ ] Generate chord pads from the progression.
- [ ] Generate comping patterns for piano, electric piano, organ, and synth.
- [ ] Support sustained, rhythmic, arpeggiated, and stab-based modes.
- [ ] Add controls for voicing spread, inversion movement, density, and register.
- [ ] Avoid overcrowding the guitar part.
- [ ] Add simple section-aware texture changes.

### AI Lead Player

- [ ] Generate short melodic hooks.
- [ ] Generate lead fills between vocal phrases.
- [ ] Generate solo phrases for selected sections.
- [ ] Favor chord tones on strong beats.
- [ ] Add controls for range, busyness, repetition, and motif reuse.
- [ ] Avoid playing constantly across the whole song.

### AI Percussion / Extras

- [ ] Generate optional shaker, tambourine, claps, toms, and cymbal accents.
- [ ] Add accents that reinforce section changes.
- [ ] Add controls for density and stereo placement.
- [ ] Keep percussion optional so the core band can stay uncluttered.

### Member Personality Presets

- [ ] Define a personality profile for each member.
- [ ] Give each member a conservative default mode.
- [ ] Add an "overplay" control for intentionally busier parts.
- [ ] Add a "listen more" control for leaving more space.
- [ ] Make personalities affect rhythm, note choice, repetition, and dynamics.

### Incremental Performers And Parts

- [ ] Let a user add or remove individual performers without regenerating the whole band.
- [ ] Let a user add specific musical parts, such as second guitar, harmony vocal guide, organ pad, tambourine, hand claps, or sax support.
- [ ] Let added parts choose an existing role type: drums, bass, chords, melody, texture, percussion, or guide.
- [ ] Let added performers inherit song state, section boundaries, groove, and mixer defaults from the current project.
- [ ] Let the bandleader decide whether a new part should double, answer, support, or stay out of the way.
- [ ] Keep each added part editable as its own REAPER/MIDI track.
- [ ] Preserve existing tracks when auditioning a newly added performer or part.

### Phase 1 Acceptance Criteria

- [ ] A user can generate a complete short song sketch with drums, bass, guitar, keys, and lead.
- [ ] The bandleader creates or maintains the shared song plan before member parts are generated.
- [ ] Each member can be regenerated independently.
- [ ] All generated parts stay in the same key, tempo, chord progression, and section structure.
- [ ] Bass and drums feel rhythmically connected.
- [ ] Guitar and keys do not play the same full-register chord part by default.
- [ ] The output is editable as normal MIDI inside REAPER.
- [ ] The project can run without paid third-party plugins.
- [ ] The repo includes install and usage notes for the phase 1 prototype.

## Phase 1.5: REAPER Sound And Feel

Goal: make the generated band sound and feel good in REAPER before investing heavily in standalone desktop, mobile, or plugin packaging.

### REAPER Audition Quality

- [ ] Keep REAPER as the main listening and editing environment while the arrangements mature.
- [ ] Prioritize tone, groove, dynamics, and arrangement feel over app-shell work.
- [ ] Tune generated MIDI against Deanna's installed instruments before generalizing instrument profiles.
- [ ] Keep generated parts editable so rough notes can be fixed directly inside REAPER.
- [ ] Add a repeatable listening checklist for bass weight, drum audibility, lead realism, key crowding, and overall level.
- [ ] Capture REAPER feedback as small generator changes instead of one-off MIDI edits when the lesson should apply to future songs.

### Instrument And Mix Polish

- [ ] Add per-member default velocity and register settings for the current preferred instruments.
- [ ] Add safer bass defaults for Ample Bass P Lite II.
- [ ] Improve drum presence for MT-PowerDrumKit without raising the whole mix too much.
- [ ] Add keyboard pad profile notes for Splice INSTRUMENT.
- [ ] Add lead guitar phrasing profiles that reduce robotic repetition with Ample Guitar M II Lite.
- [ ] Document sample-library mappings separately from the musical core.

## Phase 2: Live Follow And Instruction Mode

Goal: let the AI band respond to Deanna's direction and, later, to live/project audio context inside REAPER.

### Instruction Following

- [x] Add a REAPER script for writing AI Band cue instructions.
- [x] Store instructions in `state/live_cue.json`.
- [x] Let commands target the bandleader or a specific member.
- [x] Support commands such as "simplify bass", "drums bigger in chorus", "keys leave more space", and "lead answer the vocal".
- [x] Add a Python command reader that turns cue instructions into generator settings.
- [x] Add an optional real-AI cue interpreter behind `OPENAI_API_KEY`.
- [x] Add local estimated API spend tracking for the AI cue loop.
- [x] Add a one-command cue response loop that writes decision JSON and MIDI.
- [ ] Regenerate selected members without rebuilding the whole sketch.
- [ ] Add a command path for inserting a new performer or part into the current sketch.
- [ ] Preserve previous generated parts until replacements are confirmed.

### Live Listening

- [ ] Define audio/project features the AI can safely use: tempo, bar position, section, density, loudness, vocal activity, and rhythm guitar activity.
- [ ] Prototype project-state snapshots from REAPER.
- [ ] Prototype audio-analysis snapshots outside the real-time audio thread.
- [ ] Update band behavior only at musical boundaries where possible.
- [ ] Add emergency controls for mute, simplify, and reduce intensity.
- [ ] Keep latency-sensitive audio/MIDI handling out of slow model calls.

## Phase 3: Portable App Foundation

Goal: keep AI Band ready for a standalone desktop app, mobile app, or live playback rig without tying the musical core to REAPER or to any one paid sample library.

### Core Separation

- [ ] Move shared musical logic toward a host-agnostic `ai_band_core` boundary.
- [ ] Keep REAPER Lua scripts as thin host adapters.
- [ ] Keep standard MIDI as the first interchange format.
- [ ] Add user-editable instrument profiles for installed sample libraries.
- [ ] Support General MIDI or bundled fallback sounds for smoke tests.
- [ ] Keep paid/registered sample assets out of the repo and out of the core generator.

### Open Mic Mode

- [ ] Design a queue-and-play workflow for phone/tablet use.
- [ ] Support a live rig where mixer channel 1 is vocal mic, channel 2 is guitar, and channel 3 is phone/tablet aux backing band.
- [ ] Add count-in, play, stop, panic mute, next section, and setlist controls.
- [ ] Cache generated backing parts so live playback does not depend on slow model calls.
- [ ] Keep default arrangements sparse enough for live vocal and rhythm guitar.
- [ ] Support rendered stereo backing mixes for songs that rely on desktop-only sample libraries.
