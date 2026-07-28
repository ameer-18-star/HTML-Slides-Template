# Design Aesthetics Reference

Consulted in **Phase 2** of `SKILL.md`, after the foundation interview, when synthesizing a concrete style proposal. This file is the taste backstop — it's what keeps a "generated from scratch" style from collapsing into generic AI-slop.

---

## The Core Risk

When extracting from a real brand reference, the reference itself prevents genericness — you're matching something real. When generating from scratch, there's nothing external forcing specificity, and the path of least resistance is always the same handful of safe, overused defaults. Actively resist that. A from-scratch style should feel just as deliberate and specific as an extracted one — arguably more, since every choice here is a real creative decision with no excuse to default.

**Never produce, unless the interview answers explicitly point there:**

- Fonts: Inter, Roboto, Arial, system-ui, or any default OS font as a *display* font
- Colors: `#6366f1` (generic indigo), purple-on-white gradients, the default Tailwind palette unmodified
- Layout: centered-everything, generic hero-section structure, identical card grids with no visual hierarchy
- Icons: generic outline icon sets with no relationship to the rest of the system (Font Awesome defaults, Material Icons defaults)
- A logo concept that's just "the brand name in the display font, centered" with nothing else considered

If a synthesized proposal could be produced by typing the mood word into a generic template generator, it hasn't gone far enough.

---

## Mood → Direction Mapping

Use the interview's mood answer to anchor the proposal, then make one or two specific, slightly unexpected choices within that direction rather than the single most obvious one.

| Mood | Color direction | Type direction | Animation direction (see table below) | Icon direction |
|---|---|---|---|---|
| Bold & confident | Dark base, one saturated accent (orange/red/electric blue), high contrast | Heavy display weight (800-900), confident sans | Professional/Corporate or Techy/Futuristic | None, or simple filled shapes — let type carry it |
| Calm & minimal | Light or warm-dark base, muted single accent, generous negative space | Elegant serif display + clean sans body, or a single refined sans throughout | Calm/Minimal | None — typography and spacing do the work |
| Playful & energetic | Bright base or bold split-color background, 2 accents max, high saturation | Rounded/friendly display font, approachable body | Playful/Friendly | Hand-drawn or simple rounded filled icons |
| Technical & precise | Dark base (terminal-adjacent) or stark white/black, one functional accent color | Monospace accents for labels/data, clean sans for body | Techy/Futuristic or Professional/Corporate | Line icons, or none — let monospace labels carry technical feel |
| Elegant & editorial | Cream/warm-light or deep dark, restrained accent, strong light/dark text contrast | Distinctive serif display, classic sans or serif body | Editorial/Magazine | None — typography hierarchy is the entire visual language |
| Futuristic & techy | Deep navy/black base, neon or electric accent (cyan, magenta, acid green) | Geometric sans display, technical mono accents | Techy/Futuristic | Duotone or none — avoid generic "AI" circuit/network icon clichés |

These are starting points, not menus to pick from verbatim — combine, bend, or deliberately contradict one axis (e.g. "Bold & confident" with a serif display instead of the expected heavy sans) when it produces something more specific to the stated purpose.

---

## Animation Style Reference

Condensed from `brand-slides`' `animation-patterns.md` — full implementation snippets live there if `brand-slides` is also installed; this table is for choosing the *direction* during synthesis.

| Feeling | Animation character | Visual cues that should accompany it |
|---|---|---|
| Dramatic / Cinematic | Slow fades (1-1.5s), large scale transitions, spotlight reveals | Dark backgrounds, full-bleed treatment |
| Techy / Futuristic | Neon glow, glitch/scramble text, grid reveals | Particle/grid backgrounds, monospace accents |
| Playful / Friendly | Bouncy spring easing, floating/bobbing motion | Rounded corners, bright palette |
| Professional / Corporate | Fast, subtle transitions (200-300ms) | Precise spacing, restrained palette |
| Calm / Minimal | Very slow, barely-there motion | High whitespace, muted palette |
| Editorial / Magazine | Staggered text reveals | Strong type hierarchy, pull-quote treatment |
| None / Minimal | No motion beyond instant state changes | Let typography and color carry all the weight |

"None" is a legitimate, deliberate choice — not a fallback for lack of a better idea. Some of the strongest technical/editorial styles use zero animation on purpose.

---

## Icon Style Reference

| Style | When it fits | Risk to avoid |
|---|---|---|
| None | Technical, editorial, minimal, or typography-led styles | — (this is often the *strongest* choice, not an absence of one) |
| Line icons | Technical/precise, professional/corporate | Don't default to a generic open-source icon set with no weight/style match to the chosen fonts |
| Filled/solid | Bold/confident, playful | Keep corner radius consistent with the rest of the system |
| Duotone | Futuristic/techy, editorial | Use exactly two tones from the established palette, not arbitrary extra colors |
| Hand-drawn | Playful/friendly, personal brands | Only if the rest of the system is informal — clashes badly with anything technical/corporate |
| Pixel art | Technical/retro, developer-facing | Very high commitment, narrow fit — confirm explicitly before going here |

---

## Logo / Wordmark Reference

This skill produces **simple, type-based marks** — not illustrated or vector-art logo design. Set that expectation with the user up front if they ask for "a logo." Three lockup styles, adapted from `slide-design-system`'s Wordmark Patterns:

1. **Mark + wordmark** — a small abstract shape (circle, square, simple geometric form colored with the primary accent) next to the brand name in the display font.
2. **Split-weight lockup** — `PART1PART2` where one half is heavy weight and the other is light. Fits umbrella/group names (e.g. a school with multiple course tracks).
3. **Accent lockup** — `PART1PART2` where one half is colored with the primary accent. Fits sub-brands or internal tracks.
4. **Wordmark only, no mark** — sometimes the strongest choice for calm/minimal or editorial directions. Don't force a shape into the system if the typography alone is already doing the job.

If the user wants a real illustrated logo (a custom icon, mascot, or detailed mark), say so plainly and suggest a dedicated design tool or designer — this skill's mark generation is intentionally lightweight (inline SVG geometry, not illustration).

---

## Color Palette Construction

Once a direction is chosen, build the actual palette as:

- `--bg-primary` — the dominant surface color
- `--bg-secondary` — one step lighter/darker than primary, for cards/panels
- `--text-primary` — high-contrast against `--bg-primary`
- `--text-secondary` — muted variant of `--text-primary`
- `--accent` — exactly **one** color carrying all emphasis (links, CTAs, highlights). Resist the urge to add a second or third "just in case" — a single committed accent is what makes a generated palette read as intentional rather than a default theme with swapped variables.
- `--accent-glow` — a low-opacity rgba() of `--accent`, for glow/shadow effects

Pick real, specific hex values — not round numbers like `#ff0000` or `#0000ff`, which read as placeholder values rather than considered choices.