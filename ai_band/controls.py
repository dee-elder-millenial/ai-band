from __future__ import annotations

from dataclasses import dataclass

from ai_band.live_cue import LiveCue


@dataclass(frozen=True)
class GenerationControls:
    bass_simplify: bool = False
    bass_run: bool = False
    drums_bigger: bool = False
    drum_fill: bool = False
    drum_solo: bool = False
    keys_leave_space: bool = False
    lead_sparse: bool = False
    cue_summary: str | None = None


def controls_from_cue(cue: LiveCue | None) -> GenerationControls:
    if cue is None:
        return GenerationControls()

    instruction = cue.instruction.lower()
    target = cue.target.lower()
    bass_simplify = _mentions_any(instruction, ("simplify bass", "bass simpler", "less bass", "bass lighter")) or (
        target in {"bass", "bassist", "ai bass player"} and _mentions_any(instruction, ("simplify", "less", "lighter", "space"))
    )
    bass_run = _mentions_any(instruction, ("bass run", "bass walk", "walking bass", "bass fill", "bass pickup")) or (
        target in {"bass", "bassist", "bass player", "ai bass player"}
        and _mentions_any(instruction, ("run", "walk", "fill", "pickup"))
    )
    space_request = _mentions_any(instruction, ("leave more room", "more room", "leave space", "stepping on", "too crowded", "crowding"))
    keys_leave_space = _mentions_any(instruction, ("keys leave", "less keys", "keys space", "keys quieter", "keys sparse")) or (
        target in {"keys", "keyboard", "keyboardist", "ai keyboard player"} and _mentions_any(instruction, ("space", "less", "sparse", "quiet"))
    ) or ("key" in instruction and space_request)
    lead_sparse = _mentions_any(instruction, ("less lead", "lead sparse", "lead less", "lead answer", "lead space")) or (
        target in {"lead", "lead guitar", "ai lead player"} and _mentions_any(instruction, ("less", "sparse", "space", "answer"))
    ) or ("lead" in instruction and space_request)
    if target in {"bandleader", "band", "all"} and space_request and _mentions_any(instruction, ("vocal", "sing", "voice")):
        keys_leave_space = True
        lead_sparse = True
    drums_bigger = _mentions_any(instruction, ("drums bigger", "bigger drums", "more drums", "drums louder")) or (
        target in {"drums", "drummer", "ai drummer"} and _mentions_any(instruction, ("bigger", "more", "louder", "harder"))
    )
    drum_fill = _mentions_any(instruction, ("drum fill", "drummer fill", "fill at", "fill into", "drum pickup")) or (
        target in {"drums", "drummer", "ai drummer"} and _mentions_any(instruction, ("fill", "pickup"))
    )
    drum_solo = _mentions_any(instruction, ("drum solo", "drummer solo", "solo drums")) or (
        target in {"drums", "drummer", "ai drummer"} and "solo" in instruction
    )

    return GenerationControls(
        bass_simplify=bass_simplify,
        bass_run=bass_run,
        drums_bigger=drums_bigger,
        drum_fill=drum_fill,
        drum_solo=drum_solo,
        keys_leave_space=keys_leave_space,
        lead_sparse=lead_sparse,
        cue_summary=f"{cue.target}: {cue.instruction} (intensity={cue.intensity:.2f})",
    )


def _mentions_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
