#!/usr/bin/env bash
# export-pdf.sh — Export the VMSOIT HTML slide deck to a pixel-perfect PDF.
#
# Usage:
#   bash scripts/export-pdf.sh <path-to-html> [output.pdf] [--compact]
#
# Examples:
#   bash scripts/export-pdf.sh ./vmsoit-slides.html
#   bash scripts/export-pdf.sh ./vmsoit-slides.html ./deck.pdf
#   bash scripts/export-pdf.sh ./vmsoit-slides.html --compact   # 1280×720, smaller file
#
# Requirements: Node.js (https://nodejs.org)
# Playwright + Chromium are installed automatically on first run.
set -euo pipefail

# ─── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'
info() { echo -e "${CYAN}ℹ${NC} $*"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
err()  { echo -e "${RED}✗${NC} $*" >&2; }

# ─── Parse flags ──────────────────────────────────────────────────────────────
VIEWPORT_W=1920
VIEWPORT_H=1080
COMPACT=false

# BUG-FIX 5: guard POSITIONAL array so set -u does not crash on empty array
POSITIONAL=()
for arg in "$@"; do
    case $arg in
        --compact)
            COMPACT=true
            VIEWPORT_W=1280
            VIEWPORT_H=720
            ;;
        *)
            POSITIONAL+=("$arg")
            ;;
    esac
done
# BUG-FIX 5: use "${POSITIONAL[@]+"${POSITIONAL[@]}"}" to safely expand empty array
set -- ${POSITIONAL[@]+"${POSITIONAL[@]}"}

# ─── Input validation ─────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
    err "Usage: bash scripts/export-pdf.sh <path-to-html> [output.pdf] [--compact]"
    exit 1
fi

INPUT_HTML="$1"
if [[ ! -f "$INPUT_HTML" ]]; then
    err "File not found: $INPUT_HTML"
    exit 1
fi

# Resolve to absolute path
INPUT_HTML=$(cd "$(dirname "$INPUT_HTML")" && pwd)/$(basename "$INPUT_HTML")

if [[ $# -ge 2 ]]; then
    OUTPUT_PDF="$2"
else
    OUTPUT_PDF="$(dirname "$INPUT_HTML")/$(basename "$INPUT_HTML" .html).pdf"
fi

OUTPUT_DIR=$(dirname "$OUTPUT_PDF")
mkdir -p "$OUTPUT_DIR"
OUTPUT_PDF="$(cd "$OUTPUT_DIR" && pwd)/$(basename "$OUTPUT_PDF")"   # absolute

# BUG-FIX 6: save original working dir so we can restore after cd "$TEMP_DIR"
ORIG_DIR="$(pwd)"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   Export VMSOIT Slides to PDF         ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"
echo ""
[[ "$COMPACT" == "true" ]] && info "Compact mode: 1280×720 (smaller file size)"

# ─── Step 1: Check Node.js ────────────────────────────────────────────────────
info "Checking dependencies..."
if ! command -v node &>/dev/null; then
    err "Node.js is required but not installed."
    err "  macOS:   brew install node"
    err "  Ubuntu:  sudo apt install nodejs npm"
    err "  Windows: https://nodejs.org"
    exit 1
fi
ok "Node.js $(node --version) found"

# ─── Step 2: Create temp dir + Node script ────────────────────────────────────
TEMP_DIR=$(mktemp -d)
SERVE_DIR=$(dirname "$INPUT_HTML")
HTML_FILENAME=$(basename "$INPUT_HTML")

# Write the embedded Node/Playwright script
cat > "$TEMP_DIR/export-slides.mjs" << 'NODESCRIPT'
// export-slides.mjs — Screenshots every VMSOIT slide, assembles into PDF.

import { chromium } from 'playwright';
import { createServer }   from 'http';
// BUG-FIX 7+8: removed unused writeFileSync and execSync imports
import { readFileSync, mkdirSync, unlinkSync } from 'fs';
import { join, extname } from 'path';

const SERVE_DIR      = process.argv[2];
const HTML_FILE      = process.argv[3];
const OUTPUT_PDF     = process.argv[4];
const SCREENSHOT_DIR = process.argv[5];
const VP_W           = parseInt(process.argv[6]) || 1920;
const VP_H           = parseInt(process.argv[7]) || 1080;

// ── Local HTTP server (fonts + assets need HTTP, not file://) ────────────────
const MIME = {
  '.html':'text/html', '.css':'text/css', '.js':'application/javascript',
  '.json':'application/json', '.png':'image/png', '.jpg':'image/jpeg',
  '.jpeg':'image/jpeg', '.gif':'image/gif', '.svg':'image/svg+xml',
  '.webp':'image/webp', '.woff':'font/woff', '.woff2':'font/woff2',
  '.ttf':'font/ttf', '.eot':'application/vnd.ms-fontobject',
};

const server = createServer((req, res) => {
  const url      = decodeURIComponent(req.url);
  const filePath = join(SERVE_DIR, url === '/' ? HTML_FILE : url);
  try {
    const content = readFileSync(filePath);
    const ext     = extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(content);
  } catch {
    res.writeHead(404); res.end('Not found');
  }
});

const port = await new Promise(resolve =>
  server.listen(0, () => resolve(server.address().port))
);
console.log(`  Local server on port ${port}`);

// ── Screenshot each slide ─────────────────────────────────────────────────────
const browser = await chromium.launch();
const page    = await browser.newPage({ viewport: { width: VP_W, height: VP_H } });

await page.goto(`http://localhost:${port}/`, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(1500);

const slideCount = await page.evaluate(
  () => document.querySelectorAll('.slide').length
);
if (slideCount === 0) {
  console.error('  ERROR: no .slide elements found.');
  await browser.close(); server.close(); process.exit(1);
}
console.log(`  Found ${slideCount} slides`);

mkdirSync(SCREENSHOT_DIR, { recursive: true });
const shotPaths = [];

for (let i = 0; i < slideCount; i++) {

  // BUG-FIX 10+11: show/hide slides without overriding position:absolute.
  // Add .visible (VMSOIT's animation trigger class) alongside .active.
  await page.evaluate((idx) => {
    document.querySelectorAll('.slide').forEach((slide, j) => {
      if (j === idx) {
        slide.style.opacity    = '1';
        slide.style.visibility = 'visible';
        slide.style.zIndex     = '1';
        // Do NOT touch slide.style.position — keep it absolute
        slide.classList.add('active', 'visible');
      } else {
        slide.style.opacity    = '0';
        slide.style.visibility = 'hidden';
        slide.style.zIndex     = '0';
        slide.classList.remove('active', 'visible');
      }
    });
    // Honour any deck JS API
    if (window.deck?.goTo) window.deck.goTo(idx);
  }, i);

  await page.waitForTimeout(400);   // CSS transitions

  // Force all animated/reveal elements to their final visible state
  await page.evaluate((idx) => {
    const slide = document.querySelectorAll('.slide')[idx];
    if (!slide) return;

    // Generic reveal elements
    const revealSels = [
      '.reveal', '.agenda-item', '.topic-item', '.bullet-item',
      '.step-row', '.unord-item', '.cmp-card', '.cmp-card',
      '.flip-card-wrap', '.outro-video-card', '.cta-card',
      '.expl-right-card', '.img-box', '.video-box', '.note-card',
      '.narr-img-placeholder', '.narr-item-tag', '.narr-item-title',
      '.narr-item-body', '.narr-accent-line', '.sh-desc', '.sh-meta',
      '.sh-bracket', '.sh-line', '.sh-stripe',
    ];
    slide.querySelectorAll(revealSels.join(',')).forEach(el => {
      el.style.opacity    = '1';
      el.style.transform  = 'none';
      el.style.visibility = 'visible';
      el.style.maxHeight  = '2000px';
      el.style.width      = el.style.width || '';  // keep sh-line width
    });

    // Clip-path wipe elements — open them fully
    slide.querySelectorAll('.mnh-title, .sh-title').forEach(el => {
      el.style.clipPath = 'polygon(0 0, 100% 0, 100% 100%, 0 100%)';
    });
    slide.querySelectorAll('.data-table thead tr').forEach(el => {
      el.style.clipPath = 'polygon(0 0, 100% 0, 100% 100%, 0 100%)';
    });
    slide.querySelectorAll('td').forEach(el => {
      el.style.opacity   = '1';
      el.style.transform = 'none';
    });

    // barPulse: freeze bar at retracted state so text is readable
    slide.querySelectorAll('.mh-bar').forEach(el => {
      el.style.animation = 'none';
      el.style.transform = 'scaleX(0)';
    });
    slide.querySelectorAll('h2.mh-title').forEach(el => {
      el.style.animation = 'none';
      el.style.color     = 'var(--accent)';
    });

    // sh-line: force to full width
    slide.querySelectorAll('.sh-line').forEach(el => {
      el.style.width = '110px';
    });
    slide.querySelectorAll('.narr-accent-line').forEach(el => {
      el.style.width = '80px';
    });
    slide.querySelectorAll('.tab-accent-line').forEach(el => {
      el.style.width = '56px';
    });
  }, i);

  await page.waitForTimeout(100);

  const shot = join(SCREENSHOT_DIR, `slide-${String(i + 1).padStart(3, '0')}.png`);
  await page.screenshot({ path: shot, fullPage: false });
  shotPaths.push(shot);
  console.log(`  Captured slide ${i + 1}/${slideCount}`);
}

await browser.close();
server.close();

// ── Assemble screenshots into PDF ─────────────────────────────────────────────
console.log('  Assembling PDF...');

const browser2 = await chromium.launch();
const pdfPage  = await browser2.newPage();

const pagesHtml = shotPaths.map(p => {
  const b64 = readFileSync(p).toString('base64');
  return `<div class="pg"><img src="data:image/png;base64,${b64}"/></div>`;
}).join('');

await pdfPage.setContent(`<!DOCTYPE html><html><head><style>
  *{margin:0;padding:0}
  @page{size:${VP_W}px ${VP_H}px;margin:0}
  .pg{width:${VP_W}px;height:${VP_H}px;page-break-after:always;overflow:hidden}
  .pg:last-child{page-break-after:auto}
  img{width:${VP_W}px;height:${VP_H}px;display:block;object-fit:cover}
</style></head><body>${pagesHtml}</body></html>`, { waitUntil: 'load' });

// BUG-FIX 2: explicit 1920×1080 page size — not A4
await pdfPage.pdf({
  path:            OUTPUT_PDF,
  width:           `${VP_W}px`,
  height:          `${VP_H}px`,
  printBackground: true,
  margin:          { top: '0', right: '0', bottom: '0', left: '0' },
});

await browser2.close();

// Clean up screenshots
shotPaths.forEach(p => unlinkSync(p));

console.log(`  ✓ PDF saved: ${OUTPUT_PDF}`);
NODESCRIPT

# ─── Step 3: Install Playwright in temp dir ───────────────────────────────────
info "Setting up Playwright (first run downloads ~120 MB Chromium)..."
echo ""

cd "$TEMP_DIR"
# BUG-FIX 6: now that we have saved ORIG_DIR we can safely cd here

cat > "$TEMP_DIR/package.json" << 'PKG'
{ "name": "vmsoit-pdf-export", "private": true, "type": "module" }
PKG

npm install playwright --save-exact &>/dev/null || {
    err "npm install playwright failed."
    cd "$ORIG_DIR"; rm -rf "$TEMP_DIR"; exit 1
}

npx playwright install chromium 2>/dev/null || {
    err "Playwright Chromium install failed."
    cd "$ORIG_DIR"; rm -rf "$TEMP_DIR"; exit 1
}
ok "Playwright ready"
echo ""

# ─── Step 4: Run the export ───────────────────────────────────────────────────
SCREENSHOT_DIR="$TEMP_DIR/screenshots"
info "Exporting slides..."
echo ""

node "$TEMP_DIR/export-slides.mjs" \
    "$SERVE_DIR" "$HTML_FILENAME" "$OUTPUT_PDF" \
    "$SCREENSHOT_DIR" "$VIEWPORT_W" "$VIEWPORT_H" || {
    err "Export failed."
    # BUG-FIX 6: always restore working dir before exit
    cd "$ORIG_DIR"; rm -rf "$TEMP_DIR"; exit 1
}

# ─── Step 5: Cleanup + success ────────────────────────────────────────────────
# BUG-FIX 6: restore working directory before cleanup
cd "$ORIG_DIR"
rm -rf "$TEMP_DIR"

echo ""
echo -e "${BOLD}════════════════════════════════════════${NC}"
ok "PDF exported successfully!"
echo -e "  ${BOLD}File:${NC}  $OUTPUT_PDF"
FILE_SIZE=$(du -h "$OUTPUT_PDF" | cut -f1 | xargs)
echo "  Size:  $FILE_SIZE"
echo "  Slides are 1920×1080 px (16:9 landscape)."
echo "  Animations are not preserved — this is a static export."
echo -e "${BOLD}════════════════════════════════════════${NC}"
echo ""

# Auto-open on macOS / Linux
command -v open    &>/dev/null && open    "$OUTPUT_PDF" || true
command -v xdg-open &>/dev/null && xdg-open "$OUTPUT_PDF" || true
