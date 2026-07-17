# VMSOIT Single-Slide Generator — Master Prompt
**How to use:** Paste this entire document into a new conversation. Then attach your existing 10-slide HTML reference file, share your brand design file, and answer the questions Claude asks at the end. After you answer, Claude will generate ONE slide at a time on your command.

---

## 0. Context — Who You Are & What You're Building

You are designing a **professional video course slide deck** for **VMSOIT (Virtual Mission to Spread Online IT)** — a Pakistani IT education brand whose tagline is **"Shaheens of IT"**. The target audience is beginner-to-intermediate South Asian learners preparing for certifications like **CompTIA A+, Network+, Security+** and related IT career paths.

The deck will have **15–20 slides per video episode**, each slide serving a specific structural or content purpose. Slides are used as **screen recordings / video overlays** — they must feel premium, cinematic, and educational, not like generic PowerPoint.

I have already given you:
- ✅ A **10-slide reference HTML file** (uploaded) — match this design exactly
- ✅ A **brand design file** (uploaded) — follow this brand system

**Your job is to generate slides ONE AT A TIME**, each as a complete self-contained HTML snippet (a single `<section class="slide">` block, ready to drop into the main deck file), following the brand system, animations, transitions, and interaction rules defined below.

---

## 1. Brand System — Zero Deviation Allowed

```
Primary accent (ONE color for emphasis):    #FFF600  (yellow)
Secondary (danger/alerts ONLY):             #D7263D  (signal red)
Tertiary (structure/text-on-dark):          #FFFFFF
Base surface:                               #101010
Card surface:                               #181818
Border:                                     #2B2B2B
Text primary / secondary / tertiary:        #F3F3F3 / #9A9A9A / #6B6B6B

Fonts (Google Fonts):
  Display titles     → Roboto Slab, weight 900
  Body paragraphs    → Roboto
  Labels / UI        → Roboto Condensed, uppercase, letter-spacing: 0.12em
  Code / mono        → Roboto Mono

Icons: Phosphor Icons (regular weight), fetched as inline SVG from:
  https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/{name}.svg
  ⚠ ALWAYS bake the literal hex into fill="..." — NEVER use fill="currentColor"

Corners: clip-path angular cuts (--cut: 22px large cards, --cut-sm: 14px small)
  ⚠ NEVER use border-radius anywhere. All cards/boxes use clip-path polygon cuts.

Bullet marker: small chevron ▽ in stroke="#FFF600" (not a standard bullet)
Logo: vmsoit-logo.png — relative path, never base64
Tagline: "Shaheens of IT"
Stage: Fixed 1920×1080px canvas — NOT responsive/fluid
```

---

## 2. Slide Type Library — One Per Purpose

Every slide you request must be one of these types. Each has a fixed layout contract.

### TYPE 1 — `certification-logo`
**Purpose:** Opens the video series. Shows certification logo + video series name.
**Layout:** Centered. Large certification badge/logo top-center. Series name in Roboto Slab 900 below. Animated accent line sweeps in under the title. Background: base `#101010` with subtle diagonal grid texture. No footer breadcrumb.
**Animation:** Logo scales in (scale 0.7 → 1.0, ease-out, 600ms). Title fades up (translateY 30px → 0, 800ms delay 200ms). Accent underline draws left-to-right (width 0 → 100%, 600ms delay 600ms).

### TYPE 2 — `agenda`
**Purpose:** Table of Contents for the specific video. Lists all topics covered.
**Layout:** Left column: large "AGENDA" eyebrow label. Below it: numbered list of topic titles, each on its own row. Right column: optional visual (icon grid or accent decoration).
**Hover effect:** Each agenda item lifts slightly (`translateY -3px`), left border switches from `#2B2B2B` to `#FFF600`, background shifts to `#1E1E1E`. Smooth 200ms ease.
**Animation:** Items stagger in from left (translateX -40px → 0), 80ms between each.

### TYPE 3 — `topic-list` (Objectives)
**Purpose:** Lists all 15+ objectives/topics for the video. Used for CompTIA exam objectives.
**Layout:** Full-width two-column list. "OBJECTIVES" eyebrow top. Items use ▽ chevron bullet in `#FFF600`. Dense layout, small type (Roboto 15px).
**Hover effect:** Each item: background `#181818 → #1F1F00`, left border flicks yellow, text brightens to `#FFFFFF`.
**Animation:** Cascade fade-in, 60ms stagger per item.

### TYPE 4 — `major-heading` (H2 Slide)
**Purpose:** Opens a new major section. Carries H2 heading + 1–2 paragraphs.
**Layout:** Left 55% = content (eyebrow label, H2 title, paragraph text). Right 45% = decorative accent block (angular cut card with icon or number).
**SIGNATURE ANIMATION — H2 Headline Background Bar:**
Behind the H2 text sits a full-width yellow rectangle (`#FFF600`, height = 1.2× line-height). This bar animates in a **looping width pulse**: starts at 100% width → shrinks to 0% → expands back to 100%, on a 3-second ease-in-out loop. The H2 text sits above it with `color: #101010` (dark text on yellow) during the pulse, switching to `#FFF600` when bar is collapsed. This creates a "breathing highlight" effect that draws the eye. Use `@keyframes barPulse` with `transform: scaleX()` for performance.
**Transition in:** Slide wipes in from left (clipPath rectangle expands right).

### TYPE 5 — `minor-heading` (H3 Slide)
**Purpose:** Sub-section header. H3 title + 1–3 paragraphs of explanation.
**Layout:** Top-left eyebrow (section name). H3 title large (Roboto Slab 700). Body text in Roboto 16px, `#9A9A9A`, max 3 paragraphs. Optional: small accent card on right.
**Animation:** Title reveals character by character using a CSS clip-path wipe (left → right), 400ms. Paragraphs fade in sequentially after (200ms stagger).

### TYPE 6 — `bullet-list` (Unordered)
**Purpose:** Unordered list of points. Max 8 items, or split into two columns if 9–14.
**Layout:** Eyebrow label top. ▽ chevron bullets in `#FFF600`. Each item: label text (Roboto Condensed uppercase, yellow) + optional sub-text (Roboto, `#9A9A9A`).
**Hover effect:** Item row background `→ #1A1A00`, left yellow bar appears (3px), text color `→ #FFFFFF`. Scale 1.0 → 1.01 on container.
**Animation:** Items enter from bottom (translateY 20px → 0), 70ms stagger.

### TYPE 7 — `numbered-list` (Ordered)
**Purpose:** Step-by-step or ranked ordered list. Max 8 items.
**Layout:** Large step numbers in Roboto Slab 900, `#FFF600`, left side. Step title in `#F3F3F3`. Optional description below in `#6B6B6B`.
**Hover effect:** Step number grows (font-size scales 1.0 → 1.1), background card deepens to `#1E1E1E`, connector line between steps glows yellow.
**Animation:** Steps slide in from right, 90ms stagger.

### TYPE 8 — `explanation-text`
**Purpose:** Paragraph-heavy explanation slide. No images. Up to 4 paragraphs or a mix of points + paragraph.
**Layout:** Full-width. Eyebrow label. Section in 2 halves: left = main explanation, right = key callout card (angular cut, `#1A1A00` bg, yellow border top).
**Animation:** Left content fades in. Right callout card wipes in from right.

### TYPE 9 — `explanation-image` (Foreground Image)
**Purpose:** Explanation with visual. Left = text. Right = image in angular-cut box.
**Layout:** Left 55% = eyebrow + heading + body text. Right 45% = image inside a clip-path cut box (border: 1px solid `#FFF600`, padding: 4px). Image fills the box, object-fit: cover.
**Hover effect on image box:** Border glows brighter (`box-shadow: 0 0 20px #FFF60066`), subtle scale 1.0 → 1.02.
**Animation:** Text fades up. Image box slides in from right (translateX 60px → 0, 500ms).

### TYPE 10 — `background-image`
**Purpose:** Immersive visual slide. Full-bleed background image at 20–30% opacity, text overlaid.
**Layout:** `background-image` on the `.slide` element, `opacity: 0.25` on a pseudo-element overlay so the image shows but text stays readable. Content centered or left-aligned depending on context.
**Animation:** Background image slowly Ken-Burns zooms (scale 1.0 → 1.06 over 8s, linear, infinite alternate). Text fades in on top.

### TYPE 11 — `comparison-2col`
**Purpose:** Compare/contrast two things. Two columns with distinct headings.
**Layout:** Two equal angular-cut cards side by side. Each card: heading bar (one in `#FFF600` bg, one in `#D7263D` bg, or both in `#181818` with colored heading text). Bullet points below heading inside each card.
**Hover effect on cards:** Card border transitions `#2B2B2B → #FFF600` (left card) or `#2B2B2B → #D7263D` (right card). Slight lift (translateY -4px).
**Animation:** Left card slides in from left, right from right, 200ms delay between.

### TYPE 12 — `comparison-3col`
**Purpose:** Compare three items. Three columns with headings.
**Layout:** Three equal angular-cut cards. Same hover/animation logic as TYPE 11. Center card gets `#FFF600` accent on heading. Left and right get `#9A9A9A` headings.

### TYPE 13 — `table`
**Purpose:** Data table with rows and columns.
**Layout:** Full-width table. Header row: `#FFF600` text on `#181818` bg, Roboto Condensed uppercase. Body rows alternate between `#101010` and `#0D0D0D`. Border: `1px solid #2B2B2B`.
**SIGNATURE ANIMATION — Table Reveal:** On slide enter, rows animate in one by one from top (translateY -10px → 0, opacity 0 → 1), 60ms stagger per row. Header row draws in first with a left-to-right yellow underline sweep (width 0 → 100%, 400ms).
**Hover effect on rows:** Row background `→ #1A1A00`, all cells in that row get a subtle left yellow border on the first cell. Text brightens to `#FFFFFF`.

### TYPE 14 — `important-note`
**Purpose:** Key callout, warning, or exam-critical fact.
**Layout:** Centered panel with thick yellow left border (6px, `#FFF600`) and icon (warning triangle or lightbulb in yellow). "IMPORTANT" eyebrow. Bold statement text. Optional sub-note in `#6B6B6B`.
**Hover effect:** Card lifts (translateY -6px), left border glows (`box-shadow 0 0 16px #FFF600`), background brightens slightly.
**Animation:** Card scales in from 0.9 → 1.0 with opacity fade, 400ms ease-out.

### TYPE 15 — `video-embed`
**Purpose:** Embeds a YouTube video with all player controls.
**Layout:** Left 40% = context text (title, description, what to watch for). Right 60% = YouTube iframe embed (16:9 ratio, inside angular-cut border, `border: 2px solid #FFF600`).
**Specs:** `allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"`, `allowfullscreen`. Responsive iframe inside a fixed-aspect wrapper.
**Animation:** Text fades in left. Video box fades in right with slight delay.

### TYPE 16 — `cta` (Call to Action)
**Purpose:** End-of-video call to action. Subscribe, like, comment, follow.
**Layout:** Large heading center. Three or four CTA buttons/cards below (subscribe, like, comment, join WhatsApp). Each CTA is an angular-cut card with icon + label. Tagline "Shaheens of IT" footer prominent.
**Animation:** Heading drops in. CTA cards stagger up from below (80ms delay each).

### TYPE 17 — `outro` (YouTube Outro Screen)
**Purpose:** Final slide mimicking a YouTube outro — suggested videos, subscribe button overlay.
**Layout:** Mimics YouTube outro layout: large center subscribe button (red circle with YouTube icon), two "video card" boxes (rectangular, angular-cut) positioned left and right for suggested videos. Channel name top-center.
**Animation:** Subscribe button pulses (scale 1.0 → 1.05 → 1.0 loop, 1.5s). Video cards slide up. All elements on delayed stagger.

---

## 3. Global Animation System

These rules apply to ALL slides:

### Entrance Animations (`.reveal` class)
```css
.reveal {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 500ms ease, transform 500ms ease;
}
.slide.active .reveal { opacity: 1; transform: translateY(0); }
```
Apply `style="transition-delay: Xms"` to each child with 90ms increments.

### Slide Transition (Between Slides)
Use an **interactive diagonal wipe** transition:
- Outgoing slide: clips away via `clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%)` → `polygon(100% 0, 100% 0, 100% 100%, 100% 100%)` (wipes to the right), 400ms ease-in-out.
- Incoming slide: clips in from left simultaneously.
- Add a thin yellow `#FFF600` line (2px) that travels across the screen during the wipe — a "slash" transition marker.

### Looping H2 Bar Animation
```css
@keyframes barPulse {
  0%   { transform: scaleX(1); }
  45%  { transform: scaleX(0); }
  55%  { transform: scaleX(0); }
  100% { transform: scaleX(1); }
}
.h2-bar {
  transform-origin: left center;
  animation: barPulse 3s ease-in-out infinite;
}
```

### Table Row Stagger
```css
@keyframes rowSlideIn {
  from { opacity: 0; transform: translateY(-10px); }
  to   { opacity: 1; transform: translateY(0); }
}
tbody tr:nth-child(n) { animation: rowSlideIn 300ms ease forwards; animation-delay: calc(n * 60ms); }
```

---

## 4. Slide Architecture — Technical Rules

- Stage: fixed `1920×1080px` (`.deck-stage`), scaled via JS `transform: scale()` to fit viewport.
- One `<section class="slide slide-[type]">` per slide.
- Visibility: toggle `.active` + `.visible` via `opacity` + `visibility` + `pointer-events` (NEVER `display: none` for transitions).
- Each slide is a **self-contained snippet** — includes its own scoped `<style>` block inside the section (use `:host-scope` or a unique slide ID as CSS scope prefix).
- Navigation: arrow keys, Space/PageDown, mouse wheel, swipe, on-screen prev/next buttons, dot indicators.
- Global slide counter text shows position across full deck (e.g. `"7 / 18"`).
- Footer on every content slide: `VMSOIT | Shaheens of IT | [Section Name] | Slide N of Total`.

---

## 5. Known Pitfalls — Always Avoid

1. **Never `fill="currentColor"`** — bake literal hex into every SVG `fill` attribute.
2. **Never place raw `<svg>` as direct child of `flex-direction: column` element** — wrap in a `<div>`.
3. **Never `border-radius`** — always `clip-path` polygon for angular cuts.
4. **Never make slides responsive/fluid** — all layout is fixed px on the 1920×1080 canvas.
5. **Never forget the `.reveal` class** on content children for entrance animations.
6. **Never hardcode `display: none`** on inactive slides — use opacity/visibility toggle.
7. **Set `width: 100%` on `.eyebrow` labels** in slides with `align-items: flex-start`.
8. **Size card heights from actual content** — don't guess; CSS Grid won't clip overflow silently.

---

## 6. One-Slide-at-a-Time Workflow

After you answer the setup questions below, here is how we work:

1. You tell me: **"Generate slide [N] — [Slide Type]"** and give me the content (text, list items, image URL, YouTube ID, etc.).
2. I generate ONE complete `<section class="slide">` HTML block (with scoped CSS and necessary JS, self-contained).
3. You review it, give feedback, I refine.
4. When approved, you say **"Next slide"** and repeat.

Each slide output includes:
- The complete `<section>` block
- A short **QA checklist** at the bottom confirming: no `currentColor`, no `border-radius`, no lorem placeholders, correct slide type class, correct animation applied.

---

## 7. Setup Questions — Answer These Before We Start

Before generating slide 1, I need your answers to these questions:

**A. Deck Identity**
1. What is the **certification name** shown on the logo slide? (e.g. CompTIA A+, Network+, Security+)
2. What is the **video series name / episode title**? (e.g. "Module 3 – RAM and Storage")
3. Do you have a **vmsoit-logo.png** ready in the same folder? (Yes / No)

**B. Slide Count & Order**
4. How many slides total in this deck? (15, 16, 17… up to 20)
5. Paste your **slide order plan** — list each slide number with its type and topic. Example:
   ```
   Slide 1  → certification-logo
   Slide 2  → agenda (TOC)
   Slide 3  → topic-list (Objectives)
   Slide 4  → major-heading (H2: "What is RAM?")
   Slide 5  → minor-heading (H3: "Types of RAM")
   ...
   ```

**C. Animations**
6. For the **H2 headline bar pulse** — do you want the default 3-second loop speed, or faster (1.5s) or slower (5s)?
7. For **slide transitions** — do you want the diagonal yellow-slash wipe (recommended), or a simpler crossfade?
8. Are there any slides where you want **NO animation** (e.g. a background-image slide you want calm and static)?

**D. Style Preferences**
9. For **comparison slides** — color scheme preference for column headings:
   - Option A: Yellow vs Red (`#FFF600` | `#D7263D`)
   - Option B: Yellow vs White (`#FFF600` | `#FFFFFF`)
   - Option C: Both neutral, differentiated by icon only
10. For **list slides** — do you want sub-descriptions under each item (2-line items), or single-line items only?
11. For the **outro slide** — do you want a real YouTube outro layout (subscribe circle + two video cards), or a simplified branded end card?

**E. Content**
12. Paste the **raw content** for slide 1 now, or say "I'll give content slide by slide" — both work.

---

*Once you answer the above, I will confirm your setup and immediately generate Slide 1.*
