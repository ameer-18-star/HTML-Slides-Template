#!/usr/bin/env python3
"""
render_pdf.py — Render the VMSOIT HTML slide deck to a multi-page PDF.

Strategy (tries each in order, stops on first success):
  1. Playwright + Chromium — best CSS/animation fidelity for the 1920×1080
                             fixed-stage layout. Screenshots every slide,
                             assembles into a PDF. No system browser needed.
  2. System browser on PATH (Chrome / Chromium / Edge) — good fidelity when
                             a desktop browser is already installed.
  3. WeasyPrint — pure Python fallback. Works without any browser but has
                  limited CSS Grid / transform support; layout may differ.

Usage:
    python render_pdf.py <input.html> <output.pdf>

The script auto-installs missing Python packages (Playwright, WeasyPrint).
"""

import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path


# ─── helpers ──────────────────────────────────────────────────────────────────

def _pip_install(package: str) -> bool:
    """Install a pip package. Returns True on success."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install",
             "--break-system-packages", "-q", package],
            check=True, timeout=180,
        )
        return True
    except Exception as e:
        print(f"  pip install {package} failed: {e}")
        return False


def _html_uri(path: str) -> str:
    """Convert an absolute file path to a file:// URI correctly on all OS."""
    return Path(os.path.abspath(path)).as_uri()


# ─── Strategy 1: Playwright (best for VMSOIT 1920×1080 fixed-stage) ──────────

def try_playwright(html_path: str, pdf_path: str) -> bool:
    # BUG-FIX 3/4: import AFTER install so the module is actually available.
    try:
        from playwright.sync_api import sync_playwright as _sw
    except ImportError:
        print("  Installing Playwright...")
        if not _pip_install("playwright"):
            return False
        try:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True, timeout=300,
            )
        except Exception as e:
            print(f"  Chromium install failed: {e}")
            return False
        # Re-import after install
        try:
            from playwright.sync_api import sync_playwright as _sw
        except Exception as e:
            print(f"  Playwright still unavailable after install: {e}")
            return False

    try:
        abs_html = os.path.abspath(html_path)
        abs_pdf  = os.path.abspath(pdf_path)

        with _sw() as p:
            browser = p.chromium.launch()

            # ── Pass 1: screenshot every slide at 1920×1080 ──────────────
            page = browser.new_page(viewport={"width": 1920, "height": 1080})

            # BUG-FIX 1: use Path.as_uri() for correct file:// URI on all OS
            page.goto(_html_uri(abs_html), wait_until="networkidle")
            page.evaluate("() => document.fonts.ready")
            page.wait_for_timeout(1500)   # let first-slide animation settle

            slide_count = page.evaluate(
                "() => document.querySelectorAll('.slide').length"
            )
            if slide_count == 0:
                print("  ERROR: no .slide elements found.")
                browser.close()
                return False

            print(f"  Found {slide_count} slides")
            import tempfile, base64
            tmp_dir = tempfile.mkdtemp()
            shot_paths = []

            for i in range(slide_count):
                # BUG-FIX 10+11: VMSOIT uses position:absolute on slides.
                # Do NOT set position:relative (collapses height to 0).
                # Add .visible (required for reveal animations) alongside .active.
                page.evaluate("""(index) => {
                    const slides = document.querySelectorAll('.slide');
                    slides.forEach((slide, idx) => {
                        if (idx === index) {
                            slide.style.opacity      = '1';
                            slide.style.visibility   = 'visible';
                            // Do NOT override position — keep absolute
                            slide.classList.add('active', 'visible');
                        } else {
                            slide.style.opacity      = '0';
                            slide.style.visibility   = 'hidden';
                            slide.classList.remove('active', 'visible');
                        }
                    });

                    // Also call goToSlide if the presentation JS exposes it
                    if (window.deck && typeof window.deck.goTo === 'function') {
                        window.deck.goTo(index);
                    }
                }""", i)

                page.wait_for_timeout(400)   # transitions

                # Force all .reveal elements visible (CSS transitions need .visible)
                page.evaluate("""(index) => {
                    const slide = document.querySelectorAll('.slide')[index];
                    if (!slide) return;
                    slide.querySelectorAll('.reveal, .agenda-item, .topic-item, ' +
                        '.bullet-item, .step-row, .unord-item, .cmp-card, ' +
                        '.flip-card-wrap, .narr-img-placeholder').forEach(el => {
                        el.style.opacity    = '1';
                        el.style.transform  = 'none';
                        el.style.visibility = 'visible';
                    });
                    // Force clip-path wipe elements open
                    slide.querySelectorAll('.mnh-title, .sh-title, .data-table thead tr')
                        .forEach(el => {
                        el.style.clipPath = 'polygon(0 0, 100% 0, 100% 100%, 0 100%)';
                    });
                    // Force animated bar to a neutral state
                    slide.querySelectorAll('.mh-bar').forEach(el => {
                        el.style.animation = 'none';
                        el.style.transform = 'scaleX(0)';
                    });
                    // Force scale-in cards
                    slide.querySelectorAll('.note-card').forEach(el => {
                        el.style.transform = 'scale(1)';
                    });
                }""", i)

                page.wait_for_timeout(100)

                shot = os.path.join(tmp_dir, f"slide-{i+1:03d}.png")
                page.screenshot(path=shot, full_page=False)
                shot_paths.append(shot)
                print(f"  Captured slide {i+1}/{slide_count}")

            browser.close()

            # ── Pass 2: assemble screenshots into a single PDF ────────────
            print("  Assembling PDF...")
            browser2 = p.chromium.launch()
            pdf_page = browser2.new_page()

            pages_html = "\n".join(
                f'<div class="p"><img src="data:image/png;base64,'
                f'{base64.b64encode(open(s,"rb").read()).decode()}" /></div>'
                for s in shot_paths
            )
            assembly = f"""<!DOCTYPE html><html><head><style>
                *{{margin:0;padding:0}}
                @page{{size:1920px 1080px;margin:0}}
                .p{{width:1920px;height:1080px;page-break-after:always;overflow:hidden}}
                .p:last-child{{page-break-after:auto}}
                img{{width:1920px;height:1080px;display:block;object-fit:cover}}
            </style></head><body>{pages_html}</body></html>"""

            pdf_page.set_content(assembly, wait_until="load")
            # BUG-FIX 2: explicitly set 1920×1080 page size so slides are
            # not cropped to A4.
            pdf_page.pdf(
                path=abs_pdf,
                width="1920px",
                height="1080px",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            browser2.close()

        # Clean up temp screenshots
        import shutil as _sh
        _sh.rmtree(tmp_dir, ignore_errors=True)

        print(f"  Rendered with Playwright -> {pdf_path}")
        return True

    except Exception as e:
        print(f"  Playwright render failed: {e}")
        return False


# ─── Strategy 2: system browser binary ───────────────────────────────────────

def try_system_browser(html_path: str, pdf_path: str) -> bool:
    candidates = [
        "google-chrome", "google-chrome-stable",
        "chromium", "chromium-browser",
        "msedge", "microsoft-edge", "microsoft-edge-stable",
    ]
    fixed = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        "/c/Program Files/Google/Chrome/Application/chrome.exe",
    ]

    binary = next((shutil.which(c) for c in candidates if shutil.which(c)), None)
    if not binary:
        binary = next((p for p in fixed if os.path.exists(p)), None)
    if not binary:
        print("  No system browser found; skipping.")
        return False

    abs_html = os.path.abspath(html_path)
    abs_pdf  = os.path.abspath(pdf_path)
    try:
        subprocess.run(
            [binary, "--headless", "--disable-gpu",
             "--no-pdf-header-footer",
             f"--print-to-pdf={abs_pdf}",
             # BUG-FIX 1: use Path.as_uri() for correct file:// URI
             _html_uri(abs_html)],
            check=True, timeout=60,
        )
        print(f"  Rendered with system browser ({binary}) -> {pdf_path}")
        return True
    except Exception as e:
        print(f"  System browser render failed: {e}")
        return False


# ─── Strategy 3: WeasyPrint (pure Python, limited CSS support) ───────────────

def try_weasyprint(html_path: str, pdf_path: str) -> bool:
    # BUG-FIX 3: import AFTER install, not inside except block
    try:
        from weasyprint import HTML as _WP_HTML
    except ImportError:
        print("  Installing WeasyPrint...")
        if not _pip_install("weasyprint"):
            return False
        try:
            from weasyprint import HTML as _WP_HTML
        except Exception as e:
            print(f"  WeasyPrint still unavailable: {e}")
            return False

    try:
        _WP_HTML(filename=os.path.abspath(html_path)).write_pdf(pdf_path)
        print(f"  Rendered with WeasyPrint -> {pdf_path}")
        print("  Note: WeasyPrint has limited CSS transform/Grid support.")
        print("  Some VMSOIT slide layouts may differ from the browser view.")
        return True
    except Exception as e:
        print(f"  WeasyPrint render failed: {e}")
        return False


# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python render_pdf.py <input.html> <output.pdf>")
        sys.exit(1)

    html_path, pdf_path = sys.argv[1], sys.argv[2]

    if not os.path.exists(html_path):
        print(f"Input file not found: {html_path}")
        sys.exit(1)

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(pdf_path))
    os.makedirs(out_dir, exist_ok=True)

    print(f"\nRendering {html_path} -> {pdf_path}\n")

    print("1/3 Trying Playwright + Chromium (best for VMSOIT 1920×1080 layout)...")
    if try_playwright(html_path, pdf_path):
        sys.exit(0)

    print("\n2/3 Trying system browser binary...")
    if try_system_browser(html_path, pdf_path):
        sys.exit(0)

    print("\n3/3 Trying WeasyPrint (pure Python fallback)...")
    if try_weasyprint(html_path, pdf_path):
        sys.exit(0)

    print()
    print("Could not render automatically.")
    print(f"Manual fallback: open {os.path.abspath(html_path)} in Chrome,")
    print("press Ctrl/Cmd+P -> Save as PDF -> set paper size to 1920×1080 px.")
    sys.exit(1)


if __name__ == "__main__":
    main()
