"""
schema.py
=========
Pydantic models for every one of the 23 VMSOIT slide types, plus the
TYPE_REGISTRY that maps a notes-file `type:` string to (Model, template).

This is the single source of truth for "what fields does slide type X need".
- loader.py reads raw dicts out of the notes file.
- renderer.py looks up TYPE_REGISTRY[raw["type"]], validates the raw dict
  through the model, and renders the matching Jinja2 template with it.
- validate.py runs additional cross-field / business-rule checks that don't
  belong in the shape-validation Pydantic already does (max items, etc.)

Adding a 24th slide type later = one new model + one registry entry.
Nothing in loader.py or renderer.py needs to change.
"""

from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, conlist


# ============================================================
# Shared building blocks (reused across multiple slide types)
# ============================================================

class BaseSlide(BaseModel):
    """Fields every slide type may carry. `type` is always required and is
    what the registry keys off. `eyebrow` is the small label + chevron icon
    at the top of most slides. `footer_label` overrides the right-hand
    footer-bar text; if omitted, the renderer falls back to `meta.section`."""
    type: str
    eyebrow: Optional[str] = None
    footer_label: Optional[str] = None


class AgendaItem(BaseModel):
    title: str
    sub: str


class DecoCard(BaseModel):
    tag: str
    val: str


class MetaItem(BaseModel):
    label: str
    val: str


class BulletItem(BaseModel):
    label: str
    sub: str


class Step(BaseModel):
    title: str
    desc: str


class UnordItem(BaseModel):
    title: str
    desc: str
    detail: str


class ComparisonColumn(BaseModel):
    heading: str
    points: conlist(str, min_length=1, max_length=6)
    # "yellow" / "red" / "neutral" / "center" — maps to the cmp-card colour class
    style: Literal["yellow", "red", "neutral", "center"] = "neutral"


class TableRow(BaseModel):
    cells: conlist(str, min_length=1)
    # optional per-row highlight style applied to the first cell (td-accent / td-danger)
    highlight: Optional[Literal["accent", "danger"]] = None


class TabItem(BaseModel):
    label: str                 # short text on the tab button
    tag: str                   # e.g. "Component 01"
    title: str
    paragraphs: conlist(str, min_length=1)
    points: list[str] = Field(default_factory=list)
    image_src: Optional[str] = None


class NarrativeItem(BaseModel):
    tag: str                   # e.g. "Tool 01 of 04"
    title: str
    body: str
    image_src: Optional[str] = None


class FlipCard(BaseModel):
    front_label: str
    image_src: Optional[str] = None
    back_eyebrow: str          # e.g. "Card 01"
    back_title: str
    back_body: str
    back_points: list[str] = Field(default_factory=list)  # used by the 2-col (tall) variant


class CtaCard(BaseModel):
    label: str                  # "Subscribe", "Like", "Comment", "Join Community"
    primary: bool = False


class OutroVideo(BaseModel):
    tag: str                    # "Watch Next" / "Popular"
    title: str


# ============================================================
# The 23 slide types
# ============================================================

class TitleSlide(BaseSlide):
    type: Literal["title"] = "title"
    heading: str
    subtitle: str
    tagline: str


class AgendaSlide(BaseSlide):
    type: Literal["agenda"] = "agenda"
    title: str
    items: conlist(AgendaItem, min_length=1, max_length=6)
    deco_cards: conlist(DecoCard, min_length=1, max_length=3)


class TopicListSlide(BaseSlide):
    type: Literal["topic_list"] = "topic_list"
    title: str
    items: conlist(str, min_length=1)


class MajorHeadingSlide(BaseSlide):
    type: Literal["major_heading"] = "major_heading"
    section_number: str         # "01"
    title: str
    paragraphs: conlist(str, min_length=1, max_length=2)
    big_num: str
    big_label: str


class SectionHeadingSlide(BaseSlide):
    type: Literal["section_heading"] = "section_heading"
    ghost_number: str            # large background number, e.g. "01"
    title: str
    paragraphs: conlist(str, min_length=1, max_length=2)
    meta: conlist(MetaItem, min_length=1, max_length=3)


class MinorHeadingSlide(BaseSlide):
    type: Literal["minor_heading"] = "minor_heading"
    title: str
    paragraphs: conlist(str, min_length=1, max_length=3)
    key_points: conlist(str, min_length=1, max_length=5)


class BulletListSlide(BaseSlide):
    type: Literal["bullet_list"] = "bullet_list"
    title: str
    items: conlist(BulletItem, min_length=1, max_length=8)


class NumberedListSlide(BaseSlide):
    type: Literal["numbered_list"] = "numbered_list"
    title: str
    steps: conlist(Step, min_length=1, max_length=8)


class UnordPopSlide(BaseSlide):
    type: Literal["unord_pop"] = "unord_pop"
    title: str
    items: conlist(UnordItem, min_length=1, max_length=6)


class ExplanationTextSlide(BaseSlide):
    type: Literal["explanation_text"] = "explanation_text"
    title: str
    paragraphs: conlist(str, min_length=1, max_length=3)
    key_points_label: str = "Exam Takeaways"
    key_points: conlist(str, min_length=1, max_length=6)


class ExplanationImageSlide(BaseSlide):
    type: Literal["explanation_image"] = "explanation_image"
    title: str
    paragraphs: conlist(str, min_length=1, max_length=3)
    image_src: Optional[str] = None
    image_alt: str = ""
    image_caption: Optional[str] = None


class BackgroundImageSlide(BaseSlide):
    type: Literal["background_image"] = "background_image"
    image_src: str
    title: str
    body: str


class Comparison2ColSlide(BaseSlide):
    type: Literal["comparison_2col"] = "comparison_2col"
    title: str
    left: ComparisonColumn
    right: ComparisonColumn


class Comparison3ColSlide(BaseSlide):
    type: Literal["comparison_3col"] = "comparison_3col"
    title: str
    columns: conlist(ComparisonColumn, min_length=3, max_length=3)


class TableSlide(BaseSlide):
    type: Literal["table"] = "table"
    title: str
    headers: conlist(str, min_length=1)
    rows: conlist(TableRow, min_length=1)


class ImportantNoteSlide(BaseSlide):
    type: Literal["important_note"] = "important_note"
    label: str = "Exam Trap"
    headline: str
    detail: str
    variant: Literal["default", "danger"] = "default"


class VideoEmbedSlide(BaseSlide):
    type: Literal["video_embed"] = "video_embed"
    video_title: str
    description: str
    tips: conlist(str, min_length=1, max_length=5)
    youtube_id: str


class TabsSlide(BaseSlide):
    type: Literal["tabs"] = "tabs"
    title: str
    intro: str
    tabs: conlist(TabItem, min_length=2, max_length=6)


class NarrativeSliderSlide(BaseSlide):
    type: Literal["narrative_slider"] = "narrative_slider"
    title: str
    intro: str
    items: conlist(NarrativeItem, min_length=2, max_length=6)


class ImageFlipGridSlide(BaseSlide):
    type: Literal["image_flip_grid"] = "image_flip_grid"
    title: str
    cards: conlist(FlipCard, min_length=4, max_length=4)   # fixed 2x2


class ImageFlipGrid2ColSlide(BaseSlide):
    type: Literal["image_flip_grid_2col"] = "image_flip_grid_2col"
    title: str
    cards: conlist(FlipCard, min_length=2, max_length=2)


class CtaSlide(BaseSlide):
    type: Literal["cta"] = "cta"
    heading: str
    subtext: str
    tagline: str
    cards: conlist(CtaCard, min_length=1, max_length=4)


class OutroSlide(BaseSlide):
    type: Literal["outro"] = "outro"
    channel_name: str
    tagline: str
    hint: str
    next_videos: conlist(OutroVideo, min_length=0, max_length=2)


# ============================================================
# TYPE_REGISTRY — the dispatch table renderer.py and validate.py use
# ============================================================
# key   -> the `type:` string used in notes YAML/JSON
# value -> (PydanticModel, template_filename)

TYPE_REGISTRY: dict[str, tuple[type[BaseModel], str]] = {
    "title":                 (TitleSlide,             "title.html.j2"),
    "agenda":                (AgendaSlide,             "agenda.html.j2"),
    "topic_list":             (TopicListSlide,          "topic_list.html.j2"),
    "major_heading":          (MajorHeadingSlide,       "major_heading.html.j2"),
    "section_heading":        (SectionHeadingSlide,     "section_heading.html.j2"),
    "minor_heading":          (MinorHeadingSlide,       "minor_heading.html.j2"),
    "bullet_list":            (BulletListSlide,         "bullet_list.html.j2"),
    "numbered_list":          (NumberedListSlide,       "numbered_list.html.j2"),
    "unord_pop":              (UnordPopSlide,           "unord_pop.html.j2"),
    "explanation_text":       (ExplanationTextSlide,    "explanation_text.html.j2"),
    "explanation_image":      (ExplanationImageSlide,   "explanation_image.html.j2"),
    "background_image":       (BackgroundImageSlide,    "background_image.html.j2"),
    "comparison_2col":        (Comparison2ColSlide,     "comparison_2col.html.j2"),
    "comparison_3col":        (Comparison3ColSlide,     "comparison_3col.html.j2"),
    "table":                  (TableSlide,              "table.html.j2"),
    "important_note":         (ImportantNoteSlide,      "important_note.html.j2"),
    "video_embed":            (VideoEmbedSlide,         "video_embed.html.j2"),
    "tabs":                   (TabsSlide,               "tabs.html.j2"),
    "narrative_slider":       (NarrativeSliderSlide,    "narrative_slider.html.j2"),
    "image_flip_grid":        (ImageFlipGridSlide,      "image_flip_grid.html.j2"),
    "image_flip_grid_2col":   (ImageFlipGrid2ColSlide,  "image_flip_grid_2col.html.j2"),
    "cta":                    (CtaSlide,                "cta.html.j2"),
    "outro":                  (OutroSlide,              "outro.html.j2"),
}


class DeckMeta(BaseModel):
    """The top-level `meta:` block in a notes file."""
    objective: str
    subtitle: str = ""
    domain: str = ""
    section: str = ""    # default footer-bar text when a slide has no footer_labels