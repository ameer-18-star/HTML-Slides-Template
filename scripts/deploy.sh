#!/usr/bin/env bash
# deploy.sh — Deploy the VMSOIT slide deck to Vercel for instant sharing.
#
# Usage:
#   bash scripts/deploy.sh <path-to-html-file-or-folder>
#
# Examples:
#   bash scripts/deploy.sh ./vmsoit-slides.html
#   bash scripts/deploy.sh ./my-deck/
#
# Requirements: Node.js (https://nodejs.org). Vercel CLI auto-installed.
set -euo pipefail

# ─── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'
info() { echo -e "${CYAN}ℹ${NC} $*"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
err()  { echo -e "${RED}✗${NC} $*" >&2; }

# ─── Input ────────────────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
    err "Usage: bash scripts/deploy.sh <path-to-html-or-folder>"
    exit 1
fi

INPUT="$1"
CLEANUP_TEMP=false

if [[ -f "$INPUT" && "$INPUT" == *.html ]]; then
    DEPLOY_DIR=$(mktemp -d)
    PARENT_DIR=$(dirname "$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")")
    cp "$INPUT" "$DEPLOY_DIR/index.html"

    # Copy local assets referenced in the HTML
    # BUG-FIX 14: run in a process substitution instead of a pipe so failures
    # are visible and the parent shell detects them properly.
    while IFS= read -r ref; do
        [[ -z "$ref" ]] && continue
        SOURCE_FILE="$PARENT_DIR/$ref"
        if [[ -e "$SOURCE_FILE" ]]; then
            TARGET_SUBDIR="$DEPLOY_DIR/$(dirname "$ref")"
            mkdir -p "$TARGET_SUBDIR"
            cp -r "$SOURCE_FILE" "$TARGET_SUBDIR/" || \
                warn "Could not copy asset: $SOURCE_FILE"
        fi
    done < <(
        grep -oE '(src|href|url\()["'"'"']?[^"'"'"'>)]+' "$INPUT" 2>/dev/null \
        | sed "s/^src=//; s/^href=//; s/^url(//; s/[\"']//g" \
        | grep -v '^http' | grep -v '^data:' | grep -v '^#' | grep -v '^/' \
        | sort -u
    )

    # Also copy an assets/ folder if it exists (common convention)
    [[ -d "$PARENT_DIR/assets" ]] && \
        cp -r "$PARENT_DIR/assets" "$DEPLOY_DIR/assets" 2>/dev/null || true

    CLEANUP_TEMP=true
    info "Single HTML file detected — prepared temp deploy directory."

elif [[ -d "$INPUT" ]]; then
    if [[ ! -f "$INPUT/index.html" ]]; then
        err "Folder '$INPUT' has no index.html."
        exit 1
    fi
    DEPLOY_DIR="$(cd "$INPUT" && pwd)"
    CLEANUP_TEMP=false

else
    err "'$INPUT' is not a valid HTML file or directory."
    exit 1
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   Deploy VMSOIT Slides to Vercel      ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"
echo ""

# ─── Node.js check ────────────────────────────────────────────────────────────
if ! command -v npx &>/dev/null; then
    err "Node.js required. Install from https://nodejs.org"
    [[ "$CLEANUP_TEMP" == "true" ]] && rm -rf "$DEPLOY_DIR"
    exit 1
fi

# ─── Vercel CLI ───────────────────────────────────────────────────────────────
info "Checking Vercel CLI..."

# BUG-FIX 12: use an array for VERCEL_CMD so word-splitting is never an issue
if command -v vercel &>/dev/null; then
    VERCEL_CMD=(vercel)
    ok "Vercel CLI found ($(vercel --version 2>/dev/null | head -1))"
elif npx --yes vercel --version &>/dev/null 2>&1; then
    VERCEL_CMD=(npx --yes vercel)
    ok "Vercel CLI available via npx"
else
    info "Installing Vercel CLI globally..."
    npm install -g vercel
    VERCEL_CMD=(vercel)
    ok "Vercel CLI installed"
fi

# ─── Login check ──────────────────────────────────────────────────────────────
echo ""
info "Checking Vercel login..."

if ! "${VERCEL_CMD[@]}" whoami &>/dev/null 2>&1; then
    warn "Not logged in to Vercel."
    echo ""
    echo "  Run: vercel login"
    echo "  Or visit https://vercel.com/signup to create a free account first."
    echo ""
    echo -e "${YELLOW}Attempting interactive login now...${NC}"
    "${VERCEL_CMD[@]}" login || {
        err "Login failed. Run 'vercel login' manually then re-run this script."
        [[ "$CLEANUP_TEMP" == "true" ]] && rm -rf "$DEPLOY_DIR"
        exit 1
    }
    ok "Logged in!"
fi

VERCEL_USER=$("${VERCEL_CMD[@]}" whoami 2>/dev/null || echo "unknown")
ok "Logged in as: $VERCEL_USER"

# ─── Project name ─────────────────────────────────────────────────────────────
if [[ "$CLEANUP_TEMP" == "true" ]]; then
    DECK_NAME=$(basename "$INPUT" .html)
else
    DECK_NAME=$(basename "$DEPLOY_DIR")
fi

# Sanitise for Vercel (lowercase, hyphens only, max 100 chars)
DECK_NAME=$(
    echo "$DECK_NAME" \
    | tr '[:upper:]' '[:lower:]' \
    | sed 's/[^a-z0-9._-]/-/g; s/--*/-/g; s/^-//; s/-$//' \
    | cut -c1-100
)

# Rename temp dir to sanitised name so Vercel picks it up as the project name
if [[ "$CLEANUP_TEMP" == "true" ]]; then
    RENAMED="$(dirname "$DEPLOY_DIR")/$DECK_NAME"
    mv "$DEPLOY_DIR" "$RENAMED"
    DEPLOY_DIR="$RENAMED"
fi

# ─── Deploy ───────────────────────────────────────────────────────────────────
echo ""
info "Deploying '$DECK_NAME' to Vercel..."
echo ""

DEPLOY_OUTPUT=$("${VERCEL_CMD[@]}" deploy "$DEPLOY_DIR" --yes --prod 2>&1) || {
    err "Deployment failed:"
    echo "$DEPLOY_OUTPUT"
    [[ "$CLEANUP_TEMP" == "true" ]] && rm -rf "$DEPLOY_DIR"
    exit 1
}

# BUG-FIX 13: stricter URL extraction — match only well-formed https URLs
# (no trailing punctuation, no newlines)
DEPLOY_URL=$(echo "$DEPLOY_OUTPUT" \
    | grep -o 'https://[a-zA-Z0-9._/-]*' \
    | grep '\.vercel\.app\|\.now\.sh' \
    | tail -1)

if [[ -z "$DEPLOY_URL" ]]; then
    # Fallback: grab any https URL from the output
    DEPLOY_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^ ]*' | tail -1)
fi

# ─── Success ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}════════════════════════════════════════${NC}"
ok "Deployed successfully!"
echo ""
echo -e "  ${BOLD}Live URL:${NC}  ${DEPLOY_URL:-'(see output above)'}"
echo ""
echo "  Works on any device — phone, tablet, laptop."
echo "  Share via Slack, email, WhatsApp, or anywhere."
echo ""
echo -e "  ${CYAN}To remove later:${NC} vercel rm $DECK_NAME --yes"
echo -e "${BOLD}════════════════════════════════════════${NC}"
echo ""

# ─── Cleanup ──────────────────────────────────────────────────────────────────
[[ "$CLEANUP_TEMP" == "true" ]] && rm -rf "$DEPLOY_DIR"
