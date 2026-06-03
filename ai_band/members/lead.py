from __future__ import annotations

from ai_band.arrangement import iter_section_bars, note_duration, velocity
from ai_band.humanize import clamp_midi, expression_curve, phrase_lift, played_duration, played_start, played_velocity, pocket_start, section_groove_offset, section_lift, velocity_shift
from ai_band.midi import MidiEvent, MidiNote, MidiTrack
from ai_band.song_state import SongState
from ai_band.theory import NOTE_NAMES, chord_tones, scale_notes

LEAD_CHANNEL = 3


def generate(song: SongState, sparse: bool = False) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
    if song.preset == "heartland-rock":
        return _generate_heartland_rock(song, sparse=sparse)
    if song.preset == "southern-blues":
        return _generate_southern_blues(song, sparse=sparse)
    if song.preset == "bluesy-alt-country":
        return _generate_bluesy_alt_country(song, sparse=sparse)

    scale = scale_notes(song.key, song.scale, 5)
    hook = (0, 2, 4, 2, 5, 4, 2, 0)
    if song.preset == "bluesy-alt-country":
        hook = (0, 2, 3, 2, 4, 3, 2, 0)
    durations = (
        note_duration(song, 0.42),
        note_duration(song, 0.35),
        note_duration(song, 0.50),
        note_duration(song, 0.30),
    )

    for section, bar, _chord in iter_section_bars(song):
        should_play = section.name in {"Intro", "Chorus", "Outro"}
        if song.preset == "bluesy-alt-country":
            should_play = section.name in {"Intro", "Chorus"}
        if not should_play:
            continue

        local_bar = bar - section.start_bar
        if section.name == "Intro" and local_bar > 1:
            continue
        if section.name == "Outro" and local_bar % 2 == 1:
            continue
        if sparse and section.name == "Chorus" and local_bar % 2 == 1:
            continue

        start_beat = 2 if section.name == "Intro" else 0
        phrase = hook[:4] if section.name == "Outro" else hook
        if section.name == "Chorus" and local_bar % 2 == 1:
            phrase = (0, 2, 4, 5, 4)
        if sparse:
            phrase = phrase[:4]

        bar_lift = section_lift(song, local_bar, section.bars, 2)
        for index, scale_degree in enumerate(phrase):
            beat = _phrase_beat(start_beat + index * 0.5, local_bar, index)
            if beat >= song.beats_per_bar:
                break
            note = scale[_phrase_degree(scale_degree, local_bar, index, len(scale))]
            note_start = played_start(song, bar, beat, 0.75)
            duration = played_duration(song, durations[index % len(durations)], bar, beat, 0.60, note_duration(song, 0.18))
            note_velocity = played_velocity(velocity(50, section.energy, accent=(index % 4) * 3 + bar_lift), song, bar, beat, 2)
            track.notes.append(
                MidiNote(
                    note_start,
                    duration,
                    note,
                    note_velocity,
                    LEAD_CHANNEL,
                )
            )
            _add_expression(track, note_start, duration, section.energy, bar, beat)

    return track


def _generate_bluesy_alt_country(song: SongState, sparse: bool = False) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
    scale = scale_notes(song.key, song.scale, 5)
    lick_shapes = (
        ((0.05, 2, 0.62, 58, True), (0.95, 3, 0.36, 50, False), (1.55, 2, 0.48, 54, False)),
        ((2.10, 4, 0.40, 60, True), (2.82, 3, 0.34, 48, False)),
        ((0.18, 5, 0.50, 56, False), (0.92, 4, 0.36, 48, True), (1.62, 2, 0.56, 52, False)),
    )

    for section, bar, _chord in iter_section_bars(song):
        if section.name not in {"Intro", "Chorus"}:
            continue
        local_bar = bar - section.start_bar
        if section.name == "Intro" and local_bar not in {1, 3}:
            continue
        if section.name == "Chorus" and local_bar % 2 == 1:
            continue
        if sparse and local_bar % 4 == 2:
            continue

        bar_lift = section_lift(song, local_bar, section.bars, 2)
        lick = lick_shapes[local_bar % len(lick_shapes)]
        for index, (beat, degree, beats, base_velocity, bend) in enumerate(lick):
            beat = _phrase_beat(beat, local_bar, index)
            note = scale[_phrase_degree(degree, local_bar, index, len(scale), bend)]
            start = played_start(song, bar, beat, 0.85)
            duration = played_duration(song, note_duration(song, beats), bar, beat, 0.65, note_duration(song, 0.20))
            note_velocity = played_velocity(velocity(base_velocity, section.energy, accent=(index % 2) * 4 + bar_lift), song, bar, beat, 2)
            track.notes.append(
                MidiNote(
                    start,
                    duration,
                    note,
                    note_velocity,
                    LEAD_CHANNEL,
                )
            )
            _add_expression(track, start, duration, section.energy, bar, beat)
            if bend:
                _add_bend(track, start, duration, LEAD_CHANNEL)

    return track


def _generate_southern_blues(song: SongState, sparse: bool = False) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
    scale = scale_notes(song.key, "minor", 5)
    low_scale = scale_notes(song.key, "minor", 4)
    answer_shapes = (
        ((2.05, 2, 0.46, 52, False), (2.78, 4, 0.62, 56, True)),
        ((2.20, 5, 0.52, 58, True), (3.02, 4, 0.36, 50, False), (3.48, 2, 0.34, 50, False)),
        ((2.35, 3, 0.42, 54, False), (3.05, 4, 0.70, 58, True)),
        ((2.12, 2, 0.40, 52, False), (2.72, 0, 0.80, 56, True)),
    )
    solo_shapes = (
        ((0.20, 0, 0.44, 55, True), (0.92, 2, 0.34, 49, False), (1.45, 3, 0.36, 52, False), (2.25, 4, 0.62, 59, True)),
        ((0.55, 5, 0.48, 60, True), (1.28, 4, 0.34, 50, False), (2.10, 2, 0.42, 53, False), (3.02, 0, 0.56, 57, True)),
        ((1.05, 3, 0.40, 55, False), (1.72, 4, 0.58, 58, True), (2.72, 5, 0.36, 57, False)),
        ((0.28, 2, 0.38, 52, False), (1.08, 0, 0.50, 54, True), (2.35, 4, 0.46, 58, True), (3.18, 2, 0.36, 51, False)),
    )

    for section, bar, _chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        section_is_solo = section.name == "Solo"
        section_is_big = section.name.startswith("Chorus") or section.name == "Final Chorus"
        section_is_call = section.name in {"Intro", "Bridge", "Outro"}
        if not section_is_big and not section_is_call and not section_is_solo:
            continue
        if section.name == "Intro" and local_bar not in {1, 3}:
            continue
        if section.name == "Bridge" and local_bar not in {3, 7}:
            continue
        if section.name == "Outro" and local_bar not in {1, 3}:
            continue
        if section_is_solo and local_bar % 3 == 1:
            continue
        if section_is_big and local_bar % 2 == 0:
            continue
        if sparse and local_bar % 4 == 2:
            continue

        bar_lift = section_lift(song, local_bar, section.bars, 2)
        lick = solo_shapes[local_bar % len(solo_shapes)] if section_is_solo else answer_shapes[local_bar % len(answer_shapes)]
        note_pool = low_scale if section.name in {"Bridge", "Outro"} else scale
        for index, (beat, degree, beats, base_velocity, bend) in enumerate(lick):
            beat = _phrase_beat(beat, local_bar, index)
            note = note_pool[_phrase_degree(degree, local_bar, index, len(note_pool), bend)]
            start = played_start(song, bar, beat, 0.90)
            duration = played_duration(song, note_duration(song, beats), bar, beat, 0.70, note_duration(song, 0.18))
            note_velocity = played_velocity(velocity(base_velocity, section.energy, accent=(index % 2) * 5 + bar_lift), song, bar, beat, 2)
            track.notes.append(
                MidiNote(
                    start,
                    duration,
                    note,
                    note_velocity,
                    LEAD_CHANNEL,
                )
            )
            _add_expression(track, start, duration, section.energy, bar, beat)
            if bend:
                _add_bend(track, start, duration, LEAD_CHANNEL)

    return track


def _generate_heartland_rock(song: SongState, sparse: bool = False) -> MidiTrack:
    track = MidiTrack("AI Lead Player", channel=LEAD_CHANNEL, program=81)
    hook_shapes = (
        ((2.00, 2, 0.42, 52, False), (2.70, 4, 0.36, 50, False), (3.18, 2, 0.50, 53, False)),
        ((1.65, 0, 0.44, 51, False), (2.35, 2, 0.42, 54, False), (3.08, 4, 0.46, 52, False)),
        ((2.10, 4, 0.42, 55, False), (2.82, 2, 0.36, 49, False)),
    )
    solo_shapes = (
        ((0.22, 0, 0.40, 54, False), (0.88, 2, 0.34, 50, False), (1.48, 4, 0.42, 56, False), (2.48, 2, 0.52, 53, False)),
        ((0.40, 4, 0.40, 56, False), (1.08, 2, 0.32, 50, False), (1.82, 0, 0.46, 52, False), (2.72, 4, 0.44, 55, False)),
        ((0.28, 2, 0.38, 53, False), (1.05, 4, 0.38, 56, False), (1.78, 5, 0.34, 54, False), (2.58, 2, 0.54, 52, False)),
    )

    for section, bar, chord in iter_section_bars(song):
        local_bar = bar - section.start_bar
        section_is_solo = section.name == "Guitar Solo"
        section_is_hook = section.name in {"Intro", "Outro"} or section.name.startswith("Chorus") or section.name == "Final Chorus"
        if not section_is_solo and not section_is_hook:
            continue
        if section.name == "Intro" and local_bar not in {1, 3}:
            continue
        if section.name == "Outro" and local_bar not in {0, 2, 3}:
            continue
        if section_is_hook and local_bar % 2 == 0 and section.name not in {"Intro", "Outro"}:
            continue
        if section_is_hook and section.name not in {"Intro", "Outro"} and local_bar % 4 == 3:
            continue
        if section_is_solo and local_bar % 4 == 2:
            continue
        if sparse and local_bar % 4 == 1:
            continue

        bar_lift = phrase_lift(local_bar, section.bars, 3)
        groove_offset = section_groove_offset(song, local_bar, section.bars, 0.45)
        lick = solo_shapes[local_bar % len(solo_shapes)] if section_is_solo else hook_shapes[local_bar % len(hook_shapes)]
        phrase_notes = _heartland_phrase_notes(song.key, chord.root, chord.quality, local_bar, len(lick), section_is_solo)
        for index, (beat, degree, beats, base_velocity, bend) in enumerate(lick):
            beat = _phrase_beat(beat, local_bar, index)
            note = phrase_notes[index]
            start = max(_heartland_lead_start(song, bar, beat, index) + groove_offset, song.bar_tick(bar))
            duration = played_duration(
                song,
                note_duration(song, beats + _heartland_phrase_length(index, local_bar)),
                bar,
                beat,
                0.55,
                note_duration(song, 0.18),
            )
            note_velocity = played_velocity(
                clamp_midi(
                    velocity(base_velocity, section.energy, accent=(index % 2) * 4)
                    + velocity_shift(bar, beat, 3)
                    + bar_lift
                    + _heartland_phrase_accent(index, local_bar, section_is_solo)
                ),
                song,
                bar,
                beat,
                2,
            )
            if _should_add_heartland_grace(section.name, local_bar, index, bend):
                _add_heartland_grace(track, song, start, note, note_velocity, bar, index)
            track.notes.append(
                MidiNote(
                    start,
                    duration,
                    note,
                    note_velocity,
                    LEAD_CHANNEL,
                )
            )
            _add_expression(track, start, duration, section.energy, bar, beat)
            if bend:
                _add_bend(track, start, duration, LEAD_CHANNEL, _heartland_bend_profile(bar, index))
            elif duration >= note_duration(song, 0.38):
                _add_heartland_vibrato(track, start, duration, bar, index)

    return track


def _heartland_pentatonic_pool(key: str, section_is_solo: bool) -> tuple[int, ...]:
    root = 48 + NOTE_NAMES[key]
    notes = (root, root + 2, root + 4, root + 7, root + 9)
    if section_is_solo:
        return notes + (root + 12,)
    return notes


def _heartland_lead_note_pool(key: str, chord_root: int, chord_quality: str, section_is_solo: bool) -> tuple[int, ...]:
    chord_notes = tuple(sorted(chord_tones(chord_root, chord_quality, 3)))
    key_root = 48 + NOTE_NAMES[key]
    anchors = tuple(note for note in (key_root, key_root + 7, key_root + 12) if note not in chord_notes)
    if section_is_solo:
        return chord_notes + anchors[:2]
    return chord_notes + anchors[:1]


def _heartland_phrase_notes(
    key: str,
    chord_root: int,
    chord_quality: str,
    local_bar: int,
    length: int,
    section_is_solo: bool,
) -> tuple[int, ...]:
    chord_notes = tuple(sorted(chord_tones(chord_root, chord_quality, 3)))
    chord_pcs = tuple(note % 12 for note in chord_notes)
    root_pc = chord_root % 12
    third_pc = chord_pcs[1]
    fifth_pc = chord_pcs[2]
    key_pc = NOTE_NAMES[key]
    key_fifth_pc = (key_pc + 7) % 12
    phrase_third_pc = root_pc if (third_pc - key_pc) % 12 == 11 else third_pc

    if section_is_solo:
        shapes = (
            (root_pc, phrase_third_pc, fifth_pc, root_pc),
            (fifth_pc, phrase_third_pc, root_pc, fifth_pc),
            (phrase_third_pc, fifth_pc, _neighbor_pc(fifth_pc, local_bar, key_pc, chord_pcs), root_pc),
            (root_pc, _neighbor_pc(root_pc, local_bar, key_pc, chord_pcs), phrase_third_pc, fifth_pc),
        )
        center = 62 + (local_bar % 2) * 2
    else:
        shapes = (
            (root_pc, fifth_pc, root_pc),
            (phrase_third_pc, fifth_pc, root_pc),
            (fifth_pc, _neighbor_pc(fifth_pc, local_bar, key_pc, chord_pcs), root_pc),
            (key_fifth_pc, phrase_third_pc, root_pc),
        )
        center = 57

    pcs = shapes[local_bar % len(shapes)]
    notes: list[int] = []
    previous = center
    for index in range(length):
        pc = pcs[index % len(pcs)]
        if index == length - 1:
            pc = root_pc if local_bar % 3 != 1 else fifth_pc
        note = _nearest_guitar_pitch(pc, previous, section_is_solo)
        notes.append(note)
        previous = note
    return tuple(notes)


def _neighbor_pc(pc: int, local_bar: int, key_pc: int, chord_pcs: tuple[int, ...]) -> int:
    preferred = (pc + (2 if local_bar % 2 == 0 else -2)) % 12
    allowed = set(chord_pcs)
    allowed.update({key_pc, (key_pc + 2) % 12, (key_pc + 4) % 12, (key_pc + 7) % 12, (key_pc + 9) % 12})
    if preferred in allowed:
        return preferred
    options = sorted(allowed - {pc})
    return min(options, key=lambda candidate: (_pitch_class_distance(candidate, preferred), candidate))


def _pitch_class_distance(left: int, right: int) -> int:
    distance = abs(left - right) % 12
    return min(distance, 12 - distance)


def _nearest_guitar_pitch(pc: int, previous: int, section_is_solo: bool) -> int:
    low, high = (52, 71) if section_is_solo else (50, 66)
    candidates = [octave * 12 + pc for octave in range(3, 7) if low <= octave * 12 + pc <= high]
    if not candidates:
        candidates = [octave * 12 + pc for octave in range(3, 7)]
    return min(candidates, key=lambda note: (abs(note - previous), note))


def _phrase_beat(beat: float, local_bar: int, index: int) -> float:
    offsets = (0.00, 0.035, -0.020, 0.045, -0.010)
    shifted = beat + offsets[(local_bar * 2 + index) % len(offsets)]
    return max(0.0, min(3.95, shifted))


def _phrase_degree(degree: int, local_bar: int, index: int, note_count: int, bend: bool = False) -> int:
    if bend or index == 0:
        return degree % note_count
    shifts = (0, 1, 0, -1, 0, 0, 1, -1)
    return (degree + shifts[(local_bar + index * 2) % len(shifts)]) % note_count


def _heartland_lead_start(song: SongState, bar: int, beat: float, index: int) -> int:
    phrase_drag = 0.012 if index in {0, 3} else -0.006 if index == 1 else 0.004
    return max(pocket_start(song, bar, beat, 0.45) + int(song.ticks_per_beat * phrase_drag), song.bar_tick(bar))


def _heartland_phrase_length(index: int, local_bar: int) -> float:
    phrase_shape = (0.00, 0.035, -0.025, 0.020)[local_bar % 4]
    return (0.04, -0.03, 0.02, 0.05, -0.02)[index % 5] + phrase_shape


def _heartland_phrase_accent(index: int, local_bar: int, section_is_solo: bool) -> int:
    answer_shape = (-4, 1, 4, -1)
    solo_shape = (-3, 2, 5, 1)
    shape = solo_shape if section_is_solo else answer_shape
    return shape[(index + local_bar) % len(shape)]


def _should_add_heartland_grace(section_name: str, local_bar: int, index: int, bend: bool) -> bool:
    if section_name == "Guitar Solo":
        return index in {1, 3} or (bend and local_bar % 3 == 0)
    return bend and index == 0 and local_bar % 4 in {1, 3}


def _add_heartland_grace(
    track: MidiTrack,
    song: SongState,
    start: int,
    note: int,
    note_velocity: int,
    bar: int,
    index: int,
) -> None:
    offset_pattern = (0.085, 0.070, 0.095)
    grace_offset = int(song.ticks_per_beat * offset_pattern[(bar + index) % len(offset_pattern)])
    grace_start = max(start - grace_offset, song.bar_tick(bar))
    if grace_start >= start:
        return
    grace_note = _heartland_grace_note(song.key, note)
    duration = max(18, min(44, start - grace_start - 2))
    velocity = max(38, note_velocity - 22 - ((bar + index) % 5))
    track.notes.append(MidiNote(grace_start, duration, grace_note, velocity, LEAD_CHANNEL))


def _heartland_grace_note(key: str, note: int) -> int:
    pool = tuple(sorted(_heartland_pentatonic_pool(key, True) + tuple(n - 12 for n in _heartland_pentatonic_pool(key, True))))
    lower_notes = [candidate for candidate in pool if candidate < note]
    return lower_notes[-1] if lower_notes else note


def _heartland_bend_profile(bar: int, index: int) -> tuple[tuple[float, int], ...]:
    shapes = (
        ((0.18, 420), (0.40, 760), (0.66, 520), (0.86, 0)),
        ((0.22, 520), (0.46, 900), (0.70, 640), (0.88, 0)),
        ((0.18, 360), (0.40, 680), (0.66, 460), (0.84, 0)),
        ((0.24, 580), (0.50, 840), (0.72, 600), (0.90, 0)),
    )
    return shapes[(bar + index) % len(shapes)]


def _add_heartland_vibrato(track: MidiTrack, start: int, duration: int, bar: int, index: int) -> None:
    depth = (50, 70, 45, 60)[(bar + index) % 4]
    onset = 0.46 if duration < 220 else 0.38
    profile = (
        (onset, depth),
        (onset + 0.12, -depth),
        (onset + 0.24, int(depth * 0.7)),
        (min(0.90, onset + 0.36), 0),
    )
    track.events.extend(
        _pitch_bend(start + int(duration * timing), LEAD_CHANNEL, 8192 + amount)
        for timing, amount in profile
    )


def _add_bend(
    track: MidiTrack,
    start: int,
    duration: int,
    channel: int,
    profile: tuple[tuple[float, int], ...] | None = None,
) -> None:
    if profile is None:
        profile = ((0.22, 500), (0.48, 850), (0.82, 0))
    track.events.extend(
        _pitch_bend(start + int(duration * timing), channel, 8192 + amount)
        for timing, amount in profile
    )


def _add_expression(track: MidiTrack, start: int, duration: int, energy: float, bar: int, beat: float) -> None:
    track.events.extend(
        _control_change(tick, LEAD_CHANNEL, 11, value)
        for tick, value in expression_curve(start, duration, energy, bar, beat)
    )


def _control_change(tick: int, channel: int, controller: int, value: int) -> MidiEvent:
    return MidiEvent(tick=tick, status=0xB0 | channel, data=(controller, max(0, min(127, value))))


def _pitch_bend(tick: int, channel: int, value: int) -> MidiEvent:
    value = max(0, min(16383, value))
    return MidiEvent(tick=tick, status=0xE0 | channel, data=(value & 0x7F, (value >> 7) & 0x7F))
