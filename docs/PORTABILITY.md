# Portability Direction

AI Band should stay portable beyond REAPER.

The core product idea is not "a REAPER script." REAPER is the first host because it is practical, editable, and good for auditioning MIDI against real instruments. The long-term product should be able to become a desktop app, mobile app, plugin, or live backing-band rig without replacing the musical brain.

## Target Architecture

Keep these layers separate:

- `ai_band_core`: song state, bandleader decisions, member personalities, arrangement logic, MIDI/event generation, cue interpretation.
- `ai_band_hosts`: integrations for REAPER, desktop apps, mobile apps, DAWs, and command-line workflows.
- `ai_band_sounds`: instrument maps, sample-library presets, General MIDI fallback sounds, and mobile-safe sound packs.
- `ai_band_models`: optional real AI model calls for style interpretation, regeneration requests, listening summaries, and arrangement choices.

The core should not know whether the final sound comes from REAPER, Ample Sound, Splice, a mobile sampler, or a bundled desktop sound set.

## Sample Strategy

Downloaded or registered sample libraries should be treated as local user assets.

AI Band can store mappings such as "AI Bass Player uses Ample Bass P Lite II in REAPER" or "AI Drummer uses MT-PowerDrumKit in REAPER", but it should not require those exact instruments to generate a song. The generator should always be able to produce standard MIDI first.

Near-term sound layers:

- General MIDI or ReaSynth fallback for smoke tests.
- REAPER VST mappings for Deanna's installed instruments.
- Exportable MIDI for any DAW or sampler.

Later sound layers:

- Desktop bundled audition sounds.
- Mobile-friendly compressed sound pack.
- User-selectable sample-library profiles.
- Rendered stems for playback on devices that cannot host the original plugins.

## Open Mic Mode

The live target is a simple open-mic rig:

- Mixer channel 1: Deanna's vocal mic.
- Mixer channel 2: Deanna's guitar.
- Mixer channel 3: phone or tablet aux output running AI Band.

The phone/tablet should be able to queue a song, count in, and play a reliable stereo backing mix. The backing band should leave space for live vocal and rhythm guitar by default.

Important constraints for this mode:

- It must start quickly and work offline once songs and sounds are on the device.
- It should use pre-generated or cached backing parts instead of depending on slow model calls during performance.
- It needs large, obvious transport controls: queue, count in, play, stop, panic mute, next section.
- It needs conservative output levels.
- It should support exporting a rehearsal mix from REAPER or the desktop app when mobile cannot reproduce the same sample libraries.

## Product Paths

Desktop app first is the most realistic standalone path. It can reuse the Python core, add a UI, preview sounds, manage presets, and export MIDI or stems.

Mobile app is realistic after the core is separated. It should start as a live playback and sketching companion, not a full DAW.

Plugin format is possible later, but it should not be the first standalone target because plugin hosts require stricter real-time behavior, validation, and cross-host testing.

## Engineering Rules

- Keep REAPER Lua scripts thin.
- Keep song generation host-agnostic.
- Keep paid or registered sample-library names in user-editable profiles.
- Prefer standard MIDI as the interchange format.
- Do not put model calls in latency-sensitive audio paths.
- Make generated parts cacheable so live playback is dependable.
