# VMSOIT Deckgen — Project Report

Complete reference for the architecture, usage, content authoring, and troubleshooting of the VMSOIT slide deck generator.

---

## 1. Purpose

VMSOIT Deckgen turns structured YAML/JSON notes files into complete, interactive CompTIA A+ slide decks — single self-contained HTML files, matching the look, feel, and interactivity of the original hand-built template (23 slide types, click-to-flip cards, tabbed panels, a narrative slider, dot/keyboard navigation), but generated from data instead of hand-edited HTML.

The core idea: **separate content from presentation.**
- **Content** lives in `notes/*.yaml` — plain data, no markup.
- **Presentation** lives in `templates/` — 23 Jinja2 partials (one per slide type) plus one fixed shell (`shell.html.j2`) holding the shared CSS design tokens and JS navigation/interaction engine.

A new lesson is a new YAML file. The rendering code never changes per lesson.

---

## 2. Architecture

### 2.1 Data flow

```
notes/objective-1.1.yaml
        │
        ▼
loader.py ──── reads the file, returns (meta dict, raw_slides list[dict])
        │        no validation, no rendering — just "file → Python data"
        ▼
renderer.py ── for each raw slide dict:
                  1. look up TYPE_REGISTRY[slide["type"]] → (PydanticModel, template_name)
                  2. validate the dict into that model      (schema.py)
                  3. run soft content-limit checks           (validate.py)
                  4. render the model against its Jinja2 template
                ↓
              joins all rendered <section> blocks and injects them into
              shell.html.j2 (fixed CSS/JS, never regenerated per deck)
        │
        ▼
build.py ────── writes the final HTML to output/, copies assets/ alongside it,
                 prints any warnings, exits non-zero on hard failures
```

### 2.2 Why a type registry instead of if/elif chains

`engine/schema.py` defines `TYPE_REGISTRY`, a single dict mapping a `type:` string (as used in the notes file) to its Pydantic model and its template filename:

```python
TYPE_REGISTRY = {
    "title":           (TitleSlide,          "title.html.j2"),
    "agenda":          (AgendaSlide,          "agenda.html.j2"),
    ...
}
```

`renderer.py` and `build.py` never hardcode the list of 23 types — they just look things up in this dict. Adding a 24th slide type is: one new Pydantic model, one new template file, one new registry entry. Nothing else changes.

### 2.3 Why the shell is separate from the slide templates

The CSS tokens (`--accent`, `--bg-primary`, etc.) and the JS engine (`SlidePresentation`, `TabsComponent`, `NarrativeSlider`, `CardFlipController`, `UnordPopController`, `InlineEditor`) are **identical across every deck** — they were extracted once from the original template and never change per lesson. Regenerating them per build would be wasted work and a source of drift. `shell.html.j2` holds them fixed; the only per-build variable is the joined slide HTML dropped into one `{{ slides }}` slot.

The JS engine is also **fully generic** — it queries `document.querySelectorAll('.slide')` at runtime rather than assuming a fixed count of 23, so decks of any length work without code changes (see §9, Scaling).

---

## 3. Directory structure

```
VMSOIT_Deckgen/
├── assets/
│   └── vmsoit-logo.png          # copied into output/ alongside every build
├── engine/
│   ├── __init__.py               # marks engine/ as a Python package
│   ├── schema.py                  # 23 Pydantic models + TYPE_REGISTRY + DeckMeta
│   ├── loader.py                   # notes file (YAML/JSON) → raw Python dicts
│   ├── renderer.py                 # validates + renders slides → final deck HTML
│   └── validate.py                  # soft content-limit / business-rule warnings
├── templates/
│   ├── shell.html.j2               # fixed CSS + JS engine, shared by every deck
│   └── slides/
│       ├── _macros.html.j2         # shared Jinja2 macros (chevron, eyebrow, footer, icons)
│       ├── title.html.j2
│       ├── agenda.html.j2
│       ├── topic_list.html.j2
│       ├── major_heading.html.j2
│       ├── section_heading.html.j2
│       ├── minor_heading.html.j2
│       ├── bullet_list.html.j2
│       ├── numbered_list.html.j2
│       ├── unord_pop.html.j2
│       ├── explanation_text.html.j2
│       ├── explanation_image.html.j2
│       ├── background_image.html.j2
│       ├── comparison_2col.html.j2
│       ├── comparison_3col.html.j2
│       ├── table.html.j2
│       ├── important_note.html.j2
│       ├── video_embed.html.j2
│       ├── tabs.html.j2
│       ├── narrative_slider.html.j2
│       ├── image_flip_grid.html.j2
│       ├── image_flip_grid_2col.html.j2
│       ├── cta.html.j2
│       └── outro.html.j2
├── notes/
│   └── objective-1.1.yaml         # your lesson content, one file per objective
├── output/                      # generated decks land here (gitignore this)
├── build.py                       # CLI entrypoint
├── requirements.txt
├── readme.md
└── report.md                      # this file
```

---

## 4. Installation

### 4.1 Requirements
- Python 3.11+
- Windows, macOS, or Linux

### 4.2 Setup (Windows PowerShell)

```powershell
cd "C:\Users\HP\Desktop\Notes\VMSOIT_Deckgen"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Common pitfall:** if your project folder path contains a space (e.g. `VMSOIT Deckgen`), always quote the full path and use the call operator `&` when invoking an executable directly:
```powershell
& "C:\Users\HP\Desktop\Notes\VMSOIT Deckgen\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```
Simpler: just `Activate.ps1` first, then every subsequent `pip`/`python` call in that terminal automatically targets the venv — no manual path-typing needed.

### 4.3 Setup (macOS/Linux)

```bash
cd VMSOIT_Deckgen
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4.4 Dependencies (`requirements.txt`)

| Package | Used for |
|---|---|
| `Jinja2` | rendering the 23 slide partials + shell |
| `PyYAML` | parsing notes YAML files |
| `pydantic` | per-slide-type schema validation |
| `click` | the `build.py` CLI |
| `watchdog` | `--watch` mode: rebuild on file save |
| `livereload` | `--watch` mode: browser auto-refresh |
| `python-frontmatter`, `markdown-it-py` | optional — only needed if you add Markdown-based notes support later |

---

## 5. Usage

### 5.1 Build a single deck

```bash
python build.py notes/objective-1.1.yaml
```
Writes to `output/objective-1.1.html` by default (filename derived from the notes file's stem).

### 5.2 Build to a specific path

```bash
python build.py notes/objective-1.1.yaml -o output/custom-name.html
```

### 5.3 Batch-build every notes file in a folder

```bash
python build.py notes/ --batch -o output/
```
Every `.yaml`/`.yml`/`.json` file directly inside `notes/` gets built to `output/<filename>.html`.

### 5.4 Strict mode

```bash
python build.py notes/objective-1.1.yaml --strict
```
Treats `validate.py`'s soft content warnings (too many bullets, missing recommended fields, etc.) as build failures instead of just printing them. Useful in CI or before a final publish pass.

### 5.5 Watch mode (live preview)

```bash
python build.py notes/objective-1.1.yaml --watch
```
Rebuilds automatically whenever the notes file **or any template** changes, and serves the output folder at `http://localhost:5500` with browser auto-refresh (via `livereload`). Use `--port 5600` to change the port.

### 5.6 Exit codes

| Code | Meaning |
|---|---|
| `0` | Success (warnings may have been printed, unless `--strict`) |
| `1` | Hard failure — bad notes file structure, schema validation error, or template render error |
| `2` | `--strict` was set and warnings were present |

---

## 6. Writing a notes file

### 6.1 File shape

Every notes file has exactly two top-level keys:

```yaml
meta:
  objective: "Objective 1.1"
  subtitle: "..."
  domain: "..."
  section: "..."       # default footer-bar text for every slide

slides:
  - type: title
    ...
  - type: agenda
    ...
  # one entry per slide, in the order they should appear
```

### 6.2 Fields every slide type accepts

| Field | Required? | Notes |
|---|---|---|
| `type` | yes | must match a key in `TYPE_REGISTRY` |
| `eyebrow` | no | small label + chevron shown at the top of most slides |
| `footer_label` | no | overrides the footer-bar text; falls back to `meta.section` |

### 6.3 Field reference for all 23 slide types

**`title`**
`heading` (str), `subtitle` (str), `tagline` (str)

**`agenda`**
`title` (str), `items` (1–6 × `{title, sub}`), `deco_cards` (1–3 × `{tag, val}`)

**`topic_list`**
`title` (str), `items` (list of str, no fixed max — recommended ≤12)

**`major_heading`**
`section_number` (str), `title` (str), `paragraphs` (1–2 × str), `big_num` (str), `big_label` (str)

**`section_heading`**
`ghost_number` (str), `title` (str), `paragraphs` (1–2 × str), `meta` (1–3 × `{label, val}`)

**`minor_heading`**
`title` (str), `paragraphs` (1–3 × str), `key_points` (1–5 × str)

**`bullet_list`**
`title` (str), `items` (1–8 × `{label, sub}`)

**`numbered_list`**
`title` (str), `steps` (1–8 × `{title, desc}`)

**`unord_pop`**
`title` (str), `items` (1–6 × `{title, desc, detail}`)

**`explanation_text`**
`title` (str), `paragraphs` (1–3 × str), `key_points_label` (str, default `"Exam Takeaways"`), `key_points` (1–6 × str)

**`explanation_image`**
`title` (str), `paragraphs` (1–3 × str), `image_src` (str or `null`), `image_alt` (str, optional), `image_caption` (str, optional)

**`background_image`**
`image_src` (str, required — no placeholder fallback for this type), `title` (str), `body` (str)

**`comparison_2col`**
`title` (str), `left` / `right` (each `{heading, points (1–6 × str), style}`) — `style` is one of `yellow` / `red` / `neutral` / `center`

**`comparison_3col`**
`title` (str), `columns` (exactly 3 × same shape as above)

**`table`**
`title` (str), `headers` (list of str), `rows` (list of `{cells: [str, ...], highlight: "accent"|"danger"|null}`)

**`important_note`**
`label` (str, default `"Exam Trap"`), `headline` (str), `detail` (str), `variant` (`"default"` or `"danger"`)

**`video_embed`**
`video_title` (str), `description` (str), `tips` (1–5 × str), `youtube_id` (str)

**`tabs`**
`title` (str), `intro` (str), `tabs` (2–6 × `{label, tag, title, paragraphs (1+ × str), points (list of str, optional), image_src (optional)}`)

**`narrative_slider`**
`title` (str), `intro` (str), `items` (2–6 × `{tag, title, body, image_src (optional)}`)

**`image_flip_grid`**
`title` (str), `cards` (exactly 4 × `{front_label, image_src (optional), back_eyebrow, back_title, back_body, back_points (optional)}`)

**`image_flip_grid_2col`**
`title` (str), `cards` (exactly 2 × same shape as above — `back_points` renders as a bullet list on this variant)

**`cta`**
`heading` (str), `subtext` (str), `tagline` (str), `cards` (1–4 × `{label, primary (bool)}`)

**`outro`**
`channel_name` (str), `tagline` (str), `hint` (str), `next_videos` (0–2 × `{tag, title}`)

### 6.4 A complete, real, working example

`notes/objective-1.1.yaml` in this project is a full working example covering all 23 types with real CompTIA A+ 220-1201 (Domain 1: Mobile Devices) content — use it as the reference when writing a new objective's notes file.

---

## 7. The build pipeline, step by step

1. **`build.py`** parses CLI args, resolves the notes file path and output path.
2. **`loader.load_notes(path)`** reads the file (YAML or JSON by extension), checks it has `meta` and `slides` keys, checks every slide has a `type`, and returns `(meta_dict, raw_slides)` — no validation of individual field values yet.
3. **`renderer.DeckRenderer.render_deck(meta, raw_slides)`**:
   - Validates `meta` against `DeckMeta`.
   - For each raw slide, in order:
     - Looks up `TYPE_REGISTRY[type]` → `(Model, template_name)`.
     - Validates the raw dict into the Pydantic model — this is where a missing/malformed field raises a clear error naming the slide number, type, and field.
     - Computes a zero-padded slug (`slide-001`, width based on total slide count).
     - Renders the model through its Jinja2 template with `StrictUndefined` — a template referencing a field the model doesn't have fails loudly here, rather than silently rendering blank.
   - Runs `validate.validate_slide()` per slide and `validate.validate_deck()` across the whole list, collecting soft warnings (not fatal unless `--strict`).
   - Joins all rendered `<section>` blocks and renders them into `shell.html.j2`.
4. **`build.py`** writes the final HTML to the output path, copies `assets/` alongside it (so relative `<img src="vmsoit-logo.png">` references resolve), prints warnings, and exits with the appropriate code.

---

## 8. The validation system, in two layers

### 8.1 Shape validation (`schema.py`, via Pydantic) — hard failures
Answers "does this slide have the right fields, in the right types?" A missing required field, a field of the wrong type, or a list outside its declared length bounds raises a `ValidationError`, which `renderer.py` converts into a `SlideRenderError` naming the slide number and type. **The build stops.**

### 8.2 Content-limit validation (`validate.py`) — soft warnings
Answers "is this a *sensible* deck, even though it's technically valid?" Examples: a `bullet_list` with 8 items is schema-valid but flagged as likely to overflow the fixed slide stage; a deck that doesn't open with `title` or close with `outro`/`cta` is flagged; a `video_embed` with a placeholder YouTube ID is flagged; a deck over 60 slides is flagged per the scaling considerations in §9. **These never stop the build unless `--strict` is passed.**

---

## 9. Scaling to larger lecture decks

The rendering pipeline and the JS engine both handle any number of slides — `SlidePresentation` builds its nav dots and slide array from `document.querySelectorAll('.slide')` at runtime, not a hardcoded count, and `renderer.py` loops over however many entries are in `slides:`, reusing any of the 23 types as many times as needed, in any order.

Things worth deciding deliberately as decks grow past ~60 slides (flagged automatically by `validate.py`):
- **Dot navigation UX** — a strip of 60+ nav dots becomes visually unusable; consider a progress bar or grouped dots instead.
- **File size** — heavy slide types (`background_image`, `video_embed`, `image_flip_grid`) compound; keep media external rather than inlined.
- **Content organization** — one deck per objective (the current pattern) is usually more usable than one giant merged-lecture file; `--batch` mode supports building many small decks in one command rather than hand-assembling one huge one.

---

## 10. Extending the project

### 10.1 Adding a 24th slide type
1. Add a new Pydantic model to `engine/schema.py`.
2. Add a new Jinja2 template to `templates/slides/`.
3. Add one entry to `TYPE_REGISTRY` mapping the new `type:` string to `(Model, template_filename)`.

`loader.py`, `renderer.py`, and `build.py` never need to change.

### 10.2 Adding Markdown as a notes input format
`loader.py` is deliberately isolated from `renderer.py` — it only produces `(meta dict, raw_slides list[dict])`. A Markdown-with-frontmatter loader could be added as a second function (e.g. `load_notes_markdown()`) returning the same shape, without touching validation or rendering at all.

---

## 11. Troubleshooting

### 11.1 `ModuleNotFoundError: No module named 'engine'`
`engine/init.py` is misnamed — it must be `engine/__init__.py` (double underscores both sides). Rename it:
```powershell
Rename-Item "engine\init.py" "__init__.py"
```

### 11.2 PowerShell: `The term '...' is not recognized`
Usually caused by an unquoted path containing a space (e.g. a folder named `VMSOIT Deckgen`). Quote the full path and prefix with the call operator:
```powershell
& "C:\path with spaces\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```
Simplest fix: activate the venv first (`.venv\Scripts\Activate.ps1`), then use bare `python`/`pip` afterward.

### 11.3 `1 validation error for <SlideType> ... Input should be a valid string [type=string_type, input_value=None]`
A field declared as a required `str` in `schema.py` was given `null` in the notes file. Either:
- Supply a real value in the notes file, **or**
- If that field is genuinely meant to be optional (e.g. an image that isn't ready yet, and the template already has a placeholder fallback for it), change the field in `schema.py` from `field_name: str` to `field_name: Optional[str] = None`.

Check the template before loosening the schema — only make a field optional if the template actually has a graceful fallback for a missing value (most image fields do; `background_image.image_src` deliberately does not, since that slide type has no placeholder state).

### 11.4 `'dict object' has no attribute '<field_name>'` during template render
The template references a field the Pydantic model doesn't currently define. This happens if `schema.py` and the templates in `templates/slides/` drift out of sync (e.g. after a manual edit to one but not the other). Fix by adding the missing field to the relevant model in `schema.py`, with a sensible default if it's optional:
```python
field_name: list[str] = Field(default_factory=list)
```
Make sure `Field` is imported at the top of `schema.py`:
```python
from pydantic import BaseModel, Field, conlist
```

### 11.5 `NotesFileError: ... is missing a top-level 'slides:' list` (or similar)
The notes YAML/JSON file's structure is malformed — check indentation, make sure `meta:` and `slides:` are both top-level keys, and that `slides:` is a list (`-` prefixed entries), not a mapping.

### 11.6 A slide type's schema and template disagree on something
Since `schema.py`, `loader.py`, `renderer.py`, `validate.py`, and all 23 templates were originally hand-written together (not generated from a single source of truth), the most reliable fix after any manual edit is: re-check the specific slide type's model in `schema.py` against its template in `templates/slides/` side by side, field by field.

### 11.7 Deck opens but interactivity (tabs, flip cards, slider) doesn't work
Confirm `templates/shell.html.j2` is the unmodified extraction from the original `Slides.html` — it contains the entire JS engine (`SlidePresentation`, `TabsComponent`, `NarrativeSlider`, `CardFlipController`, `UnordPopController`). If it's missing or truncated, none of the `data-*`-attribute-driven interactivity will initialize.

### 11.8 Logo/images missing in the built deck
`build.py` copies everything in `assets/` into the output folder alongside the generated HTML, since the shell/templates reference images with relative paths like `vmsoit-logo.png`. Confirm the real asset files exist in `assets/` (not placeholders) before building.

---

## 12. Known limitations / deliberate simplifications

- **No Markdown notes support yet** — only YAML and JSON are implemented in `loader.py`, though the architecture supports adding it without touching the rest of the pipeline (§10.2).
- **Icons in comparison/CTA/flip-grid slides are keyed by a small fixed vocabulary**, not arbitrary per-slide SVG — e.g. `comparison_2col`'s `style` field picks from `yellow`/`red`/`neutral`/`center`, and `cta` card icons are looked up by label (`subscribe`, `like`, `comment`, `join community`). An unrecognized CTA label falls back to a generic icon rather than failing the build.
- **Dot navigation is not redesigned for very large decks** — see §9.
- **No automated visual regression testing** — schema and template correctness are verified structurally (every field a template references exists on its model), but pixel-level visual output should still be spot-checked in a browser after significant template changes.
