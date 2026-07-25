# VMSOIT Deckgen

Generate polished, interactive CompTIA A+ (220-1201 / 220-1202) slide decks from plain YAML notes files — no manual HTML editing required.

Write your lesson content once as structured data, run one command, and get a fully interactive, self-contained HTML deck: click-to-flip cards, tabbed panels, a narrative slider, keyboard/dot navigation — all driven by a shared, unmodified rendering engine.

## Why this exists

The original slide deck was a single hand-built HTML file — 23 slides, each with hardcoded content baked directly into the markup. Editing meant hunting through thousands of lines of HTML. This project separates **content** (YAML notes files) from **presentation** (a fixed CSS/JS shell + 23 reusable Jinja2 templates), so new lessons are just new data files.

## Features

- **23 distinct slide types** — title, agenda, bullet lists, numbered steps, comparisons (2-col/3-col), data tables, tabbed panels, a narrative slider, click-to-flip card grids, video embeds, and more.
- **Schema-validated content** — every slide type is a Pydantic model; a missing or malformed field fails the build with a clear error instead of producing broken HTML.
- **Soft content-limit warnings** — get warned (not blocked) when a slide is likely to overflow the fixed slide stage (e.g. too many bullet points).
- **One shared rendering engine** — the CSS design tokens and JS navigation/interaction engine live in one shell template and are never duplicated per deck.
- **Batch builds** — render every notes file in a folder in one command.
- **Live preview** — `--watch` rebuilds and auto-refreshes your browser on every save.

## Project structure

```
VMSOIT_Deckgen/
├── assets/                  # static files copied into every build (logo, images)
├── engine/
│   ├── __init__.py
│   ├── schema.py             # Pydantic models for all 23 slide types + TYPE_REGISTRY
│   ├── loader.py              # reads notes YAML/JSON off disk
│   ├── renderer.py            # validates + renders slides into the final deck
│   └── validate.py            # soft content-limit / business-rule warnings
├── templates/
│   ├── shell.html.j2          # fixed CSS tokens + JS engine, shared by every deck
│   └── slides/                # one Jinja2 template per slide type (23 files)
├── notes/                   # your lesson content, one YAML file per objective
├── output/                  # generated decks land here
├── build.py                  # CLI entrypoint
└── requirements.txt
```

## Requirements

- Python 3.11+
- See `requirements.txt` for dependencies (Jinja2, PyYAML, pydantic, click, watchdog, livereload)

## Installation

```bash
git clone <your-repo-url>
cd VMSOIT_Deckgen
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
```

## Quick start

```bash
python build.py notes/objective-1.1.yaml
```

Opens as `output/objective-1.1.html` — a single self-contained file, no server required.

## Usage

```bash
# Build one deck
python build.py notes/objective-1.1.yaml

# Build to a specific output path
python build.py notes/objective-1.1.yaml -o output/custom-name.html

# Build every notes file in a folder
python build.py notes/ --batch -o output/

# Fail the build on content warnings, not just print them
python build.py notes/objective-1.1.yaml --strict

# Live rebuild + browser auto-refresh while editing
python build.py notes/objective-1.1.yaml --watch
```

## Writing a notes file

Each notes file is one YAML document with a `meta:` block and a `slides:` list. Each slide entry needs a `type:` matching one of the 23 registered types, plus that type's required fields. See `notes/objective-1.1.yaml` for a complete, working, real-content example covering all 23 types.

```yaml
meta:
  objective: "Objective 1.1"
  subtitle: "Install and Configure Laptop Hardware and Components"
  domain: "Domain 1: Mobile Devices"
  section: "Mobile Device Hardware"

slides:
  - type: title
    eyebrow: "CompTIA A+ Core 1 · 220-1201 (V15)"
    heading: "Mobile Device Hardware"
    subtitle: "Objective 1.1"
    tagline: "Let's get started."
  # ...more slides
```

Full field reference, error troubleshooting, and the complete architecture are documented in [`report.md`](./report.md).

## License

Internal training material — not licensed for redistribution.
