"""
validate.py
============
Business-rule validation that sits ABOVE schema.py's shape validation.

schema.py answers: "does this slide have the right fields, in the right
shape?" (missing field, wrong type, list too long -> Pydantic ValidationError).

validate.py answers: "is this a *sensible* deck?" -- things Pydantic can't
express on its own, or checks that span multiple slides / the whole file.
Examples: a bullet_list slide crammed with 8 items will overflow the fixed
1920x1080 stage even though schema.py's conlist(max_length=8) technically
allows it; a deck with zero slides is valid JSON but not a valid deck.

Two entry points:
- validate_slide(slide)  -> list[str] of warnings for one already-schema-
  validated slide model.
- validate_deck(meta, slides) -> list[str] of warnings for the whole deck.

Neither raises by default -- callers (renderer.py / build.py) decide whether
warnings should be fatal (e.g. --strict CLI flag) or just printed.
"""

from __future__ import annotations
from pydantic import BaseModel

from .schema import (
    AgendaSlide, TopicListSlide, BulletListSlide, NumberedListSlide,
    UnordPopSlide, MinorHeadingSlide, ExplanationTextSlide, TableSlide,
    VideoEmbedSlide, TabsSlide, NarrativeSliderSlide, CtaSlide,
    TYPE_REGISTRY,
)


# ============================================================
# Soft content limits per type.
# These are recommendations baked into the original template's comments
# (e.g. "Max 8 steps recommended", "agenda: max 6 items") -- staying under
# them keeps content from overflowing the fixed-size 1920x1080 stage.
# Values are (recommended_max, hard_cap). Hard cap should always match (or be
# looser than) the conlist max_length already enforced in schema.py; it's
# repeated here so validate.py can explain *why* in a friendly message.
# ============================================================

LIMITS: dict[str, dict[str, tuple[int, int]]] = {
    "agenda":            {"items": (6, 6)},
    "topic_list":        {"items": (12, 20)},
    "bullet_list":       {"items": (8, 8)},
    "numbered_list":     {"steps": (8, 8)},
    "unord_pop":         {"items": (5, 6)},
    "minor_heading":     {"key_points": (4, 5)},
    "explanation_text":  {"key_points": (5, 6)},
    "table":             {"rows": (8, 12)},
    "video_embed":       {"tips": (3, 5)},
    "tabs":              {"tabs": (4, 6)},
    "narrative_slider":  {"items": (4, 6)},
    "cta":               {"cards": (4, 4)},
}


def _check_field_length(slide: BaseModel, field: str, recommended: int, hard: int) -> list[str]:
    value = getattr(slide, field, None)
    if value is None:
        return []
    n = len(value)
    warnings = []
    if n > hard:
        # Shouldn't normally happen -- schema.py's conlist should already have
        # rejected this -- but guards against future schema loosening.
        warnings.append(
            f"{slide.type}: '{field}' has {n} items, exceeding the hard cap of {hard}."
        )
    elif n > recommended:
        warnings.append(
            f"{slide.type}: '{field}' has {n} items -- {recommended} is the recommended "
            f"max before content risks overflowing the fixed slide stage."
        )
    return warnings


def validate_slide(slide: BaseModel) -> list[str]:
    """Run soft content-limit checks for a single already-schema-validated slide."""
    warnings: list[str] = []
    limits_for_type = LIMITS.get(slide.type, {})
    for field, (recommended, hard) in limits_for_type.items():
        warnings.extend(_check_field_length(slide, field, recommended, hard))

    # Type-specific structural checks that don't fit the generic length check above.
    if isinstance(slide, TableSlide):
        n_headers = len(slide.headers)
        for i, row in enumerate(slide.rows):
            if len(row.cells) != n_headers:
                warnings.append(
                    f"table: row {i} has {len(row.cells)} cells but the header "
                    f"row has {n_headers} columns -- these must match."
                )

    if isinstance(slide, VideoEmbedSlide):
        if slide.youtube_id in ("", "VIDEO_ID_HERE"):
            warnings.append(
                "video_embed: youtube_id is a placeholder -- replace before publishing."
            )

    if isinstance(slide, (TabsSlide,)):
        labels = [t.label for t in slide.tabs]
        if len(labels) != len(set(labels)):
            warnings.append("tabs: duplicate tab labels found -- each should be unique.")

    if isinstance(slide, CtaSlide):
        primaries = [c for c in slide.cards if c.primary]
        if len(primaries) > 1:
            warnings.append("cta: more than one card marked primary -- only one should be highlighted.")

    return warnings


def validate_deck(meta, slides: list[BaseModel]) -> list[str]:
    """Whole-deck checks that require looking across slides, not just within one."""
    warnings: list[str] = []

    if not slides:
        warnings.append("deck: notes file contains zero slides.")
        return warnings

    if slides[0].type != "title":
        warnings.append(
            "deck: first slide is not type 'title' -- decks conventionally open with one."
        )

    if slides[-1].type not in ("outro", "cta"):
        warnings.append(
            "deck: last slide is not type 'outro' or 'cta' -- decks conventionally end with one."
        )

    unknown_types = [s.type for s in slides if s.type not in TYPE_REGISTRY]
    if unknown_types:
        warnings.append(f"deck: unrecognised slide types found: {sorted(set(unknown_types))}")

    if len(slides) > 60:
        warnings.append(
            f"deck: {len(slides)} slides is large for a single file -- consider the dot-nav "
            f"overflow and DOM-weight tradeoffs before generating, or split into multiple decks."
        )

    # Per-slide checks, aggregated with a 1-based slide number for readability.
    for i, slide in enumerate(slides, start=1):
        for w in validate_slide(slide):
            warnings.append(f"slide {i}: {w}")

    return warnings