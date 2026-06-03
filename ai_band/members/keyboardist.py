from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, phrase_lift, played_duration, played_start, played_velocity, pocket_start, support_rest, velocity_shift
from ai_band.midi import MidiEvent, MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import chord_tones

KEYS_CHANNEL = 2


def generate(song: SongState, leave_space: bool = False) -> MidiTrack:
    track = MidiTrack("AI Keyboard Player", channel=KEYS_CHANNEL, program=66 if song.preset == "heartland-rock" else 4)

    for section, bar, chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        bar_lift = phrase_lift(local_bar, section.bars, 2) if song.preset == "heartland-rock" else 0
        is_verse = section.name == "Verse" or section.name.startswith("Verse ")
        if leave_space and local_bar % 2 == 1:
            continue
        if section.name in {"Intro", "Outro"} or is_verse:
            if local_bar % 2 == 1:
                continue

        if song.preset == "southern-blues" and section.name == "Bridge" and local_bar % 2 == 1:
            continue

        tones = chord_tones(chord.root, chord.quality, 4)
        voicing = (tones[1], tones[2])
        beats = (2.0,)
        duration = note_duration(song, 1.6)
        if song.preset == "heartland-rock":
            voicing = (tones[0] + 12,)
            beats = (3.0,)
            duration = note_duration(song, 0.75)
            if section.name.startswith("Chorus") or section.name in {"Final Chorus", "Guitar Solo"}:
                voicing = (tones[0] + 12, tones[2] + 12)
                beats = (1.5, 3.0)
                duration = note_duration(song, 0.55)
        elif song.preset == "southern-blues":
            voicing = (tones[0], tones[2])
            beats = (2.75,)
            duration = note_duration(song, 0.9)
        elif song.preset == "bluesy-alt-country":
            voicing = (tones[0], tones[1])
            beats = (2.5,)
            duration = note_duration(song, 1.0)

        if section.energy >= 0.75:
            voicing = (tones[1], tones[2] + 12)
            beats = (1.5, 3.0)
            duration = note_duration(song, 0.45)
            if song.preset == "heartland-rock":
                voicing = (tones[0] + 12,)
                beats = (3.0,)
                duration = note_duration(song, 0.5)
                if section.name.startswith("Chorus") or section.name in {"Final Chorus", "Guitar Solo"}:
                    voicing = (tones[0] + 12, tones[2] + 12)
                    beats = (1.5, 3.0)
            elif song.preset == "southern-blues":
                voicing = (tones[1], tones[2])
                beats = (3.0,)
                duration = note_duration(song, 0.55)
                if section.name in {"Solo", "Final Chorus"}:
                    beats = (1.0, 3.0)
            elif song.preset == "bluesy-alt-country":
                voicing = (tones[0], tones[2])
                beats = (1.0, 3.0)
                duration = note_duration(song, 0.55)
        if leave_space:
            beats = (beats[0],)
            duration = min(duration, note_duration(song, 0.8))

        for beat in beats:
            if support_rest(song, "keys", section.energy, local_bar, section.bars, beat):
                continue
            note_voicing = _heartland_color_voicing(voicing, tones, local_bar, beat) if song.preset == "heartland-rock" else voicing
            for note in note_voicing:
                start = song.beat_tick(bar, beat)
                note_duration_ticks = duration
                note_velocity = velocity(32, section.energy)
                if song.preset == "heartland-rock":
                    start = pocket_start(song, bar, beat, 0.50)
                    note_duration_ticks = max(note_duration(song, 0.30), duration + _heartland_breath(song, bar, beat))
                    note_velocity = clamp_midi(note_velocity + velocity_shift(bar, beat, 2) + bar_lift)
                else:
                    start = played_start(song, bar, beat, 0.45)
                    note_duration_ticks = played_duration(song, duration, bar, beat, 0.50, note_duration(song, 0.25))
                    note_velocity = played_velocity(note_velocity, song, bar, beat, 2)
                track.notes.append(
                    MidiNote(start, note_duration_ticks, note, note_velocity, KEYS_CHANNEL)
                )
                if song.preset == "heartland-rock":
                    _add_heartland_sax_expression(track, start, note_duration_ticks, bar, beat)

    return track


def _heartland_breath(song: SongState, bar: int, beat: float) -> int:
    pattern = (0.04, -0.03, 0.02, -0.02)
    index = (bar + int(beat * 2)) % len(pattern)
    return int(song.ticks_per_beat * pattern[index])


def _heartland_color_voicing(
    voicing: tuple[int, ...],
    tones: tuple[int, int, int],
    local_bar: int,
    beat: float,
) -> tuple[int, ...]:
    root, third, fifth = tones
    if len(voicing) == 1 and local_bar % 4 == 2 and beat >= 2.5:
        return (root + 12, root + 14)
    if len(voicing) > 1 and (local_bar + int(beat * 2)) % 6 == 3:
        return (third + 12, root + 17)
    return voicing


def _add_heartland_sax_expression(track: MidiTrack, start: int, duration: int, bar: int, beat: float) -> None:
    swell = (82, 88, 84, 90)[(bar + int(beat * 2)) % 4]
    fall = max(70, swell - 10)
    scoop = (320, 460, 260, 380)[(bar + int(beat * 2)) % 4]
    direction = -1 if (bar + int(beat * 2)) % 3 else 1
    track.events.extend(
        (
            _control_change(start, 11, max(62, swell - 18)),
            _pitch_bend(start, 8192 + direction * scoop),
            _control_change(start + int(duration * 0.28), 11, swell),
            _pitch_bend(start + int(duration * 0.35), 8192),
            _control_change(start + int(duration * 0.82), 11, fall),
        )
    )


def _control_change(tick: int, controller: int, value: int) -> MidiEvent:
    return MidiEvent(tick=tick, status=0xB0 | KEYS_CHANNEL, data=(controller, max(0, min(127, value))))


def _pitch_bend(tick: int, value: int) -> MidiEvent:
    value = max(0, min(16383, value))
    return MidiEvent(tick=tick, status=0xE0 | KEYS_CHANNEL, data=(value & 0x7F, (value >> 7) & 0x7F))
