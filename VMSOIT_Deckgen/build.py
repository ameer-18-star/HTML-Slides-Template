"""
build.py
=========
CLI entrypoint. Wires loader.py -> renderer.py -> a .html file on disk.

Usage:
    python build.py notes/objective-1.1.yaml
    python build.py notes/objective-1.1.yaml -o output/objective-1.1.html
    python build.py notes/objective-1.1.yaml --strict          # warnings fail the build
    python build.py notes/ --batch -o output/                  # every notes file in a dir
    python build.py notes/objective-1.1.yaml --watch            # rebuild + live-reload on save

Exit codes:
    0  success (or success with warnings, unless --strict)
    1  a slide/deck could not be built (SlideRenderError / NotesFileError)
    2  --strict was set and validate.py raised warnings
"""

from __future__ import annotations
import sys
import shutil
from pathlib import Path

import click

from engine.loader import load_notes, load_notes_dir, NotesFileError
from engine.renderer import DeckRenderer, SlideRenderError

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_ASSETS_DIR = PROJECT_ROOT / "assets"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


# ============================================================
# Core build logic (no CLI concerns) -- reusable by --watch too
# ============================================================

def build_one(notes_path: Path, output_path: Path, assets_dir: Path | None) -> list[str]:
    """Build a single notes file to a single output HTML file.
    Returns the list of warnings (empty if none). Raises NotesFileError /
    SlideRenderError on hard failures."""
    meta, raw_slides = load_notes(notes_path)

    renderer = DeckRenderer()
    html, warnings = renderer.render_deck(meta, raw_slides)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    if assets_dir and assets_dir.exists():
        _copy_assets(assets_dir, output_path.parent)

    return warnings


def _copy_assets(assets_dir: Path, dest_dir: Path) -> None:
    """Copy static assets (logo, images) next to the output HTML so the
    deck's relative <img src="..."> paths resolve when opened directly."""
    for item in assets_dir.iterdir():
        dest = dest_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)


def _report_warnings(warnings: list[str], notes_label: str) -> None:
    if not warnings:
        click.secho(f"  {notes_label}: no warnings", fg="green")
        return
    click.secho(f"  {notes_label}: {len(warnings)} warning(s)", fg="yellow")
    for w in warnings:
        click.echo(f"    - {w}")


def _default_output_path(notes_path: Path, output_dir: Path) -> Path:
    return output_dir / f"{notes_path.stem}.html"


# ============================================================
# CLI
# ============================================================

@click.command()
@click.argument("notes_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o", "--output", "output_arg", type=click.Path(path_type=Path), default=None,
    help="Output .html file (single mode) or output directory (--batch mode). "
         "Defaults to ./output/<name>.html",
)
@click.option(
    "--assets-dir", type=click.Path(path_type=Path), default=DEFAULT_ASSETS_DIR,
    help="Directory of static assets (logo, images) copied next to the output file(s).",
)
@click.option(
    "--batch", is_flag=True,
    help="Treat NOTES_PATH as a directory and build every .yaml/.yml/.json file in it.",
)
@click.option(
    "--strict", is_flag=True,
    help="Treat validate.py warnings as build failures (exit code 2).",
)
@click.option(
    "--watch", is_flag=True,
    help="Watch the notes file (and templates/) for changes and rebuild automatically, "
         "serving the output with live-reload in the browser.",
)
@click.option(
    "--port", default=5500, show_default=True, help="Port for --watch's local preview server.",
)
def main(
    notes_path: Path,
    output_arg: Path | None,
    assets_dir: Path,
    batch: bool,
    strict: bool,
    watch: bool,
    port: int,
) -> None:
    """Build a VMSOIT slide deck from a notes YAML/JSON file."""

    if watch and batch:
        raise click.UsageError("--watch and --batch cannot be combined.")

    if batch:
        _run_batch(notes_path, output_arg or DEFAULT_OUTPUT_DIR, assets_dir, strict)
        return

    output_path = output_arg or _default_output_path(notes_path, DEFAULT_OUTPUT_DIR)

    if watch:
        _run_watch(notes_path, output_path, assets_dir, strict, port)
        return

    _run_single(notes_path, output_path, assets_dir, strict)


def _run_single(notes_path: Path, output_path: Path, assets_dir: Path, strict: bool) -> None:
    click.echo(f"Building {notes_path} -> {output_path}")
    try:
        warnings = build_one(notes_path, output_path, assets_dir)
    except (NotesFileError, SlideRenderError) as e:
        click.secho(f"BUILD FAILED: {e}", fg="red", err=True)
        sys.exit(1)

    _report_warnings(warnings, notes_path.name)

    if strict and warnings:
        click.secho("Exiting non-zero due to --strict.", fg="red", err=True)
        sys.exit(2)

    click.secho(f"Done: {output_path}", fg="green")


def _run_batch(notes_dir: Path, output_dir: Path, assets_dir: Path, strict: bool) -> None:
    if not notes_dir.is_dir():
        raise click.UsageError(f"--batch requires NOTES_PATH to be a directory, got: {notes_dir}")

    try:
        all_notes = load_notes_dir(notes_dir)
    except NotesFileError as e:
        click.secho(f"BUILD FAILED: {e}", fg="red", err=True)
        sys.exit(1)

    if not all_notes:
        click.secho(f"No .yaml/.yml/.json files found in {notes_dir}", fg="yellow")
        return

    any_warnings = False
    for stem, (meta, raw_slides) in all_notes.items():
        output_path = output_dir / f"{stem}.html"
        click.echo(f"Building {stem} -> {output_path}")
        try:
            renderer = DeckRenderer()
            html, warnings = renderer.render_deck(meta, raw_slides)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")
            if assets_dir.exists():
                _copy_assets(assets_dir, output_path.parent)
        except SlideRenderError as e:
            click.secho(f"BUILD FAILED ({stem}): {e}", fg="red", err=True)
            sys.exit(1)

        _report_warnings(warnings, stem)
        any_warnings = any_warnings or bool(warnings)

    if strict and any_warnings:
        click.secho("Exiting non-zero due to --strict.", fg="red", err=True)
        sys.exit(2)

    click.secho(f"Done: {len(all_notes)} deck(s) built to {output_dir}", fg="green")


def _run_watch(notes_path: Path, output_path: Path, assets_dir: Path, strict: bool, port: int) -> None:
    """Rebuild on every save to the notes file or any template, and serve the
    output directory with browser live-reload via the `livereload` package."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        from livereload import Server
    except ImportError:
        click.secho(
            "watchdog and livereload are required for --watch "
            "(pip install watchdog livereload).",
            fg="red", err=True,
        )
        sys.exit(1)

    templates_dir = PROJECT_ROOT / "templates"

    def rebuild(_event=None) -> None:
        click.echo(f"\nRebuilding {notes_path} -> {output_path} ...")
        try:
            warnings = build_one(notes_path, output_path, assets_dir)
            _report_warnings(warnings, notes_path.name)
            if strict and warnings:
                click.secho("(warnings present -- would fail with --strict outside watch mode)", fg="yellow")
        except (NotesFileError, SlideRenderError) as e:
            click.secho(f"BUILD FAILED: {e}", fg="red", err=True)

    class RebuildHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory:
                rebuild()

    rebuild()  # initial build before watching starts

    observer = Observer()
    observer.schedule(RebuildHandler(), str(notes_path.parent), recursive=False)
    if templates_dir.exists():
        observer.schedule(RebuildHandler(), str(templates_dir), recursive=True)
    observer.start()

    click.secho(f"Watching for changes... serving {output_path.parent} at http://localhost:{port}", fg="cyan")
    server = Server()
    server.watch(str(output_path))
    try:
        server.serve(root=str(output_path.parent), port=port, open_url_delay=1)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()