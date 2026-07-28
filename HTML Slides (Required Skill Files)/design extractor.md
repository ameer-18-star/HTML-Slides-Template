# Design Extraction Reference

Used in **Phase 2, Design Input Path** of `SKILL.md` — when the user has a real brand or design reference to match instead of picking a curated style. Produces a **Design Token Block** in the exact same shape Phase 3 already expects from `STYLE_PRESETS.md`, so nothing downstream needs to know the difference.

The entire point of this file: **never guess a brand's colors or fonts from a generic default.** If something isn't in the reference and can't be confidently inferred, ask — don't invent.

---

## Accepted Input Types

| Type | Examples | How to read it |
|---|---|---|
| **Screenshot / image** | A website, app UI, slide, poster, product photo | Use the agent's image-understanding capability directly |
| **URL** | A company website, landing page | Fetch and inspect it if the agent has web access; otherwise ask the user for a screenshot instead |
| **Brand book / design system doc** | A PDF, an HTML design-system page, a style guide | Read it like a document — it usually states hex codes and font names explicitly, which is the highest-confidence source |
| **Plain-text brand spec** | "Primary is #0a0f1c, accent is #2dd4bf, headlines in Fraunces" | Use stated values directly, no inference needed |
| **Logo file alone** | A `.png`/`.svg` logo with no other material | Infer a restrained palette from the logo's own colors; ask the user for fonts/principles since a logo alone rarely implies typography |

A user may combine more than one of these (e.g., a brand book *and* a screenshot). See **Multi-Source Reconciliation** below.

---

## Step 1: Gather What's Available

Identify which input type(s) you have. If what's available doesn't cover everything you need to extract with confidence, ask only for the missing pieces — do not fill gaps with generic defaults.

If the user says "match my website" but hasn't actually attached or linked anything yet, stop and ask for the screenshot, URL, or file before proceeding. Don't extract from memory or assumption about what a company's site "probably" looks like.

---

## Step 2: Extract Tokens

Extraction priority for every token, in order: **(a)** explicitly stated value → **(b)** confidently inferred from a visual/document source → **(c)** ask the user. Never skip straight to a generic default.

| Token | What to look for | If genuinely unclear |
|---|---|---|
| `--bg-primary` | Dominant background tone — exact hex if visible in a screenshot's color values, or the clearly dominant surface color | Ask: "Should this deck be light or dark?" |
| `--bg-secondary` | A secondary surface tone used for cards/panels — usually one step lighter or darker than `--bg-primary` | Derive ±8% lightness from `--bg-primary` rather than asking, this is a safe inference |
| `--text-primary` | Body/heading text color with strong contrast against `--bg-primary` | Pick the highest-contrast neutral available; flag for the user if contrast looks marginal |
| `--text-secondary` | A muted/secondary text tone (captions, metadata) | Derive a lower-contrast variant of `--text-primary` |
| `--accent` | **The single color** used for CTAs, links, or emphasis in the source | If the brand has 3-4 "brand colors," ask the user to pick the ONE that should carry visual weight in this deck — competing accents at equal weight is the #1 cause of decks that don't feel "on-brand" |
| `--accent-glow` | A low-opacity rgba() version of `--accent`, used for glow/shadow effects | Derive automatically from `--accent` |
| `--font-display` | The headline typeface. If the exact font is licensed/proprietary and not available via Google Fonts or Fontshare, choose the closest distinctive match by category (serif/sans/slab/mono) and weight — never substitute Inter, Arial, Roboto, or another system font as the "close enough" pick | Ask for a vibe word ("bold", "elegant", "technical") and choose from the font-pairing table in `STYLE_PRESETS.md` |
| `--font-body` | The body typeface, same matching rule | Pair sensibly against the chosen `--font-display` |
| Logo | The actual logo file, plus its shape (square mark / wide lockup / icon-only) | Ask the user to attach it directly — don't reconstruct a logo from a description |
| Tone / principles | Words from a brand book's "principles" or "voice" section, or the stated tagline | Ask: "Two or three words for how this should feel?" |
| Iconography style | Line / filled / duotone / none, observed in the reference | Default to **none** — let typography and color carry the design rather than introducing icons that weren't actually in the brand reference |
| Excluded colors/fonts | Anything a brand book explicitly says *not* to use | None — this only applies if stated |

---

## Step 3: Confidence Check Before Generating

Never go straight from extraction to a full deck on a guess.

1. **State the extracted tokens back in plain language** before building anything: background tone, the one accent color, the two fonts, and where each came from (stated vs. inferred vs. asked). If something was inferred rather than stated, say so — the user should be able to correct a wrong inference cheaply, before it's baked into 15 slides.
2. **Render exactly one preview slide** using these tokens — same mechanism as the curated-style path's previews: a single self-contained file saved to `.frontend-slides/slide-previews/design-input.html`, opened automatically for the user.
3. **Ask** (header: "Design Match"): _"Does this match your brand?"_ Options: **Looks right** / **Adjust a color or font** / **Show me curated style options instead**

If "Adjust," make the specific change and re-render the single preview — don't regenerate three new options; the user has already told you the brand, you're just refining the read of it.

If "Show me curated style options instead," abandon design-input mode for this deck and fall back to `STYLE_PRESETS.md` / the standard 3-preview flow in `SKILL.md`.

---

## Step 4: Hand Off to Phase 3

Once confirmed, the extracted tokens **are** the style for this deck. Feed them into Phase 3 exactly as a `STYLE_PRESETS.md` preset would be — as a `:root { ... }` block plus the chosen font pairing. No further reference to `STYLE_PRESETS.md`, `bold-template-pack`, or wildcard generation is needed for the rest of this deck.

---

## Design Fidelity Checklist

Run through this before showing the preview to the user:

- [ ] Are these the brand's *own* colors — not a "close enough" generic substitute?
- [ ] Is exactly **one** accent color carrying emphasis, not three or four brand colors competing at equal weight?
- [ ] Did I avoid Inter / Arial / Roboto / system fonts unless the reference itself unambiguously uses one of them?
- [ ] Did I avoid inventing a tagline, principle, or color that wasn't actually in the input?
- [ ] If a logo is present, does it appear at a sensible size — not stretched, not distorted, not pixelated from upscaling?
- [ ] Does the result still follow the Fixed 16:9 Stage rules and include `viewport-base.css` in full, exactly like every other deck this skill produces?

---

## Multi-Source Reconciliation

If the user supplies more than one input and they conflict (e.g., a brand book lists one accent color but a screenshot shows another, possibly because the site is mid-rebrand):

- **Do not silently pick one.** Flag the conflict directly: _"Your brand book lists #2dd4bf as the accent, but the screenshot you shared uses #f59e0b — which should I use?"_
- The most explicit, most current-looking source is a reasonable tie-breaker to *propose*, but the user makes the final call.

---

## Logo & Image Handling

Reuse the existing image pipeline already defined in `html-template.md` (`crop_circle()` / `resize_max()` via Pillow) for any logo or brand imagery pulled in through this path. Embed the logo as base64 in both the preview and the final deck, following the same rules as user-provided images in `SKILL.md` Phase 1, Step 1.2.

---

## Output Format (exact)

Always express the final extracted design as this block before moving to Phase 3:

```css
:root {
    /* Derived from user-provided design input — confirmed in Phase 2 */
    --bg-primary: #______;
    --bg-secondary: #______;
    --text-primary: #______;
    --text-secondary: #______;
    --accent: #______;
    --accent-glow: rgba(__, __, __, 0.3);
    --font-display: '______', sans-serif; /* swap serif/monospace as appropriate */
    --font-body: '______', sans-serif;
}
```

Plus a one-line summary for the user, e.g.:

> Design Input: *Acme Corp* — dark theme, Fraunces + IBM Plex Sans, single teal accent (#2dd4bf). Logo: wide lockup, top-left on title slide.