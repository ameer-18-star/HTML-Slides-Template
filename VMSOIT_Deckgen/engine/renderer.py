"""
renderer.py
============
Turns (meta dict, list[raw slide dicts]) into a finished deck.html string.

Pipeline per slide:
  raw dict --(TYPE_REGISTRY lookup)--> Pydantic model --(validate)-->
  Jinja2 template render --> <section class="slide"> HTML string

Then all rendered sections are joined and dropped into shell.html.j2,
which holds the fixed CSS tokens + JS engine that never changes between
decks (see Phase 1).

This file does NOT read files off disk (loader.py's job) and does NOT
decide whether warnings are fatal (build.py's job, via a --strict flag).
It raises SlideRenderError for anything that would produce broken HTML;
it returns validate.py's warnings alongside the output for anything that
"builds fine but might not look right."
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound
from pydantic import BaseModel, ValidationError

from .schema import TYPE_REGISTRY, DeckMeta
from .validate import validate_slide, validate_deck
from .loader import RawSlide

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
SLIDES_SUBDIR = "slides"


class SlideRenderError(Exception):
    """Raised when a slide can't be turned into HTML -- unknown type,
    failed schema validation, or a template that references a variable
    the slide doesn't have (StrictUndefined catches that last case)."""


@dataclass
class RenderedSlide:
    index: int              # 1-based position in the deck
    slug: str                # e.g. "slide-004" -- zero-padded to deck size
    type: str
    html: str
    warnings: list[str]


class DeckRenderer:
    def __init__(self, templates_dir: Path = TEMPLATES_DIR):
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            # StrictUndefined turns "template references a field the model
            # doesn't have" into a loud error at build time instead of a
            # silently blank spot in the rendered HTML.
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    # ------------------------------------------------------------
    # Single slide
    # ------------------------------------------------------------
    def validate_and_build_model(self, raw_slide: RawSlide, position: int) -> BaseModel:
        slide_type = raw_slide.get("type")
        if slide_type not in TYPE_REGISTRY:
            known = ", ".join(sorted(TYPE_REGISTRY))
            raise SlideRenderError(
                f"slide {position}: unknown type '{slide_type}'. Known types: {known}"
            )

        model_cls, _template_name = TYPE_REGISTRY[slide_type]
        try:
            return model_cls(**raw_slide)
        except ValidationError as e:
            raise SlideRenderError(
                f"slide {position} (type '{slide_type}') failed validation:\n{e}"
            ) from e

    def render_slide(
        self,
        raw_slide: RawSlide,
        position: int,
        total: int,
        default_footer_label: str = "",
    ) -> RenderedSlide:
        """Validate one raw slide dict and render it to an HTML <section> string."""
        model = self.validate_and_build_model(raw_slide, position)
        _model_cls, template_name = TYPE_REGISTRY[model.type]

        pad_width = max(2, len(str(total)))
        slug = f"slide-{position:0{pad_width}d}"

        try:
            template = self.env.get_template(f"{SLIDES_SUBDIR}/{template_name}")
        except TemplateNotFound as e:
            raise SlideRenderError(
                f"slide {position} (type '{model.type}'): template "
                f"'{SLIDES_SUBDIR}/{template_name}' not found in {TEMPLATES_DIR}."
            ) from e

        context = model.model_dump()
        context["footer_label"] = model.footer_label or default_footer_label
        context["index"] = position
        context["slug"] = slug

        try:
            html = template.render(**context)
        except Exception as e:  # Jinja2 UndefinedError etc.
            raise SlideRenderError(
                f"slide {position} (type '{model.type}') failed to render "
                f"with template {template_name}: {e}"
            ) from e

        return RenderedSlide(
            index=position,
            slug=slug,
            type=model.type,
            html=html,
            warnings=[f"slide {position}: {w}" for w in validate_slide(model)],
        )

    # ------------------------------------------------------------
    # Whole deck
    # ------------------------------------------------------------
    def render_deck(
        self,
        meta_raw: dict,
        raw_slides: list[RawSlide],
        shell_template: str = "shell.html.j2",
    ) -> tuple[str, list[str]]:
        """
        Validate + render every slide, then assemble the full page via
        the fixed shell template. Returns (full_html, all_warnings).
        Raises SlideRenderError on the first slide that can't be built at
        all (unknown type / schema violation / template error) -- those
        are hard failures, unlike validate.py's soft content warnings.
        """
        try:
            meta = DeckMeta(**meta_raw)
        except ValidationError as e:
            raise SlideRenderError(f"'meta:' block failed validation:\n{e}") from e

        total = len(raw_slides)
        rendered: list[RenderedSlide] = []
        all_warnings: list[str] = []

        for position, raw_slide in enumerate(raw_slides, start=1):
            rs = self.render_slide(
                raw_slide, position=position, total=total,
                default_footer_label=meta.section or meta.objective,
            )
            rendered.append(rs)
            all_warnings.extend(rs.warnings)

        # Cross-slide / whole-deck checks need the validated models, not the
        # RenderedSlide wrappers -- rebuild that list cheaply from raw_slides
        # rather than threading models through RenderedSlide as well.
        models = [self.validate_and_build_model(s, i + 1) for i, s in enumerate(raw_slides)]
        all_warnings.extend(validate_deck(meta, models))

        try:
            shell = self.env.get_template(shell_template)
        except TemplateNotFound as e:
            raise SlideRenderError(
                f"shell template '{shell_template}' not found in {TEMPLATES_DIR}."
            ) from e

        full_html = shell.render(
            meta=meta.model_dump(),
            slides="\n\n".join(rs.html for rs in rendered),
            slide_count=total,
        )

        return full_html, all_warnings