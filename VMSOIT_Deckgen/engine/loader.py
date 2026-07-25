"""
loader.py
==========
Reads a notes file (YAML or JSON) off disk and returns it as plain Python
data -- a meta dict and a list of raw slide dicts. Deliberately does NO
validation here (that's schema.py's job) and NO rendering (that's
renderer.py's job) -- loader.py's only responsibility is "file on disk ->
Python dicts", so it stays trivial to unit test and trivial to extend with
a new input format later (e.g. Markdown-with-frontmatter) without touching
anything downstream.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

import yaml

RawSlide = dict[str, Any]


class NotesFileError(Exception):
    """Raised for structural problems with a notes file itself
    (missing file, bad extension, missing required top-level keys) --
    distinct from a Pydantic ValidationError, which means the file
    parsed fine but a slide's *content* didn't match its schema."""


SUPPORTED_EXTENSIONS = {".yaml", ".yml", ".json"}


def _read_raw(path: Path) -> dict:
    if not path.exists():
        raise NotesFileError(f"Notes file not found: {path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise NotesFileError(
            f"Unsupported notes file extension '{suffix}' for {path}. "
            f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    text = path.read_text(encoding="utf-8")

    try:
        if suffix == ".json":
            data = json.loads(text)
        else:  # .yaml / .yml
            data = yaml.safe_load(text)
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise NotesFileError(f"Failed to parse {path}: {e}") from e

    if not isinstance(data, dict):
        raise NotesFileError(
            f"{path} must contain a top-level object/mapping with "
            f"'meta' and 'slides' keys -- got {type(data).__name__}."
        )

    return data


def load_notes(path: str | Path) -> tuple[dict, list[RawSlide]]:
    """
    Load a notes file and return (meta, raw_slides).

    - meta: the raw dict under the `meta:` key (validated later against
      schema.DeckMeta by renderer.py/build.py).
    - raw_slides: the raw list under the `slides:` key, each entry an
      un-validated dict still carrying its `type:` field. Order is
      preserved -- slide order in the file IS slide order in the deck.
    """
    path = Path(path)
    data = _read_raw(path)

    if "slides" not in data:
        raise NotesFileError(f"{path} is missing a top-level 'slides:' list.")

    slides = data["slides"]
    if not isinstance(slides, list):
        raise NotesFileError(
            f"{path}: 'slides' must be a list, got {type(slides).__name__}."
        )

    for i, slide in enumerate(slides):
        if not isinstance(slide, dict):
            raise NotesFileError(
                f"{path}: slide {i + 1} must be a mapping/object, got {type(slide).__name__}."
            )
        if "type" not in slide:
            raise NotesFileError(
                f"{path}: slide {i + 1} is missing a required 'type:' field."
            )

    meta = data.get("meta", {})
    if not isinstance(meta, dict):
        raise NotesFileError(f"{path}: 'meta' must be a mapping/object.")

    return meta, slides


def load_notes_dir(dir_path: str | Path) -> dict[str, tuple[dict, list[RawSlide]]]:
    """Convenience helper for batch builds: load every .yaml/.yml/.json file
    in a directory, keyed by filename stem (e.g. 'objective-1.1')."""
    dir_path = Path(dir_path)
    results: dict[str, tuple[dict, list[RawSlide]]] = {}
    for file in sorted(dir_path.iterdir()):
        if file.suffix.lower() in SUPPORTED_EXTENSIONS:
            results[file.stem] = load_notes(file)
    return results