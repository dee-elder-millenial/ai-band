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
