from __future__ import annotations

from dataclasses import dataclass

from ai_band.live_cue import LiveCue


@dataclass(frozen=True)
class GenerationControls:
    bass_simplify: bool = False
    drums_bigger: bool = False
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
    keys_leave_space = _mentions_any(instruction, ("keys leave", "less keys", "keys space", "keys quieter", "keys sparse")) or (
        target in {"keys", "keyboard", "keyboardist", "ai keyboard player"} and _mentions_any(instruction, ("space", "less", "sparse", "quiet"))
    )
    drums_bigger = _mentions_any(instruction, ("drums bigger", "bigger drums", "more drums", "drums louder")) or (
        target in {"drums", "drummer", "ai drummer"} and _mentions_any(instruction, ("bigger", "more", "louder", "harder"))
    )
    lead_sparse = _mentions_any(instruction, ("less lead", "lead sparse", "lead less", "lead answer", "lead space")) or (
        target in {"lead", "lead guitar", "ai lead player"} and _mentions_any(instruction, ("less", "sparse", "space", "answer"))
    )

    return GenerationControls(
        bass_simplify=bass_simplify,
        drums_bigger=drums_bigger,
        keys_leave_space=keys_leave_space,
        lead_sparse=lead_sparse,
        cue_summary=f"{cue.target}: {cue.instruction} (intensity={cue.intensity:.2f})",
    )


def _mentions_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)

