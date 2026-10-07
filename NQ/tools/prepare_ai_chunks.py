#!/usr/bin/env python3
"""
One-command VPS job for preparing AI-readable CSV chunks in AlgoStrategy.

Run:
    cd /root/trading/AlgoStrategy
    python3 NQ/tools/prepare_ai_chunks.py

What it does:
1. Pulls latest origin/main.
2. Downloads known oversized external CSVs into a Git-ignored staging folder.
3. Recursively scans NQ/data and Backtesting for CSV files.
4. Reads every qualifying CSV gradually/streaming.
5. Splits files into fixed-size row chunks so AI/tools can read them easily.
6. Preserves the source folder structure under AI_Chunks.
7. Writes manifest.json for each source file.
8. Git-adds only generated chunks + scripts.
9. Commits and pushes the generated small files to origin/main.

Original source CSVs are never modified or deleted.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
TOOLS_DIR = THIS_FILE.parent
REPO_ROOT = TOOLS_DIR.parents[1]

NQ_DATA = REPO_ROOT / "NQ" / "data"
BACKTESTING_ROOT = REPO_ROOT / "Backtesting"

RAW_DIR = NQ_DATA / "_raw_large"
AI_ROOT = REPO_ROOT / "AI_Chunks"

# Process even moderately large files so examples like INTC 5m are included.
MIN_SIZE_MB = 1.0
ROWS_PER_CHUNK = 10_000

sys.path.insert(0, str(TOOLS_DIR))
from chunk_market_csv import (  # noqa: E402
    download_stream,
    chunk_by_rows,
    write_manifest,
    print_summary,
)

REMOTE_SOURCES = [
    {
        "name": "NQ/data/external/Dataset_NQ_1min_2022_2025",
        "url": "https://github.com/s-k-28/nq-es-trader-5k-payout/blob/main/data/Dataset_NQ_1min_2022_2025.csv",
        "filename": "Dataset_NQ_1min_2022_2025.csv",
    },
]

SCAN_ROOTS = [
    NQ_DATA,
    BACKTESTING_ROOT,
]

COMMIT_MESSAGE = "Add AI-readable chunks for large market CSV files"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("RUN | " + " ".join(cmd))
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, check=check)


def ensure_repo() -> None:
    if not (REPO_ROOT / ".git").exists():
        raise RuntimeError(f"Not a Git repository: {REPO_ROOT}")


def rel_dataset_path(source: Path) -> Path:
    """Mirror the source path below AI_Chunks, without the .csv suffix."""
    try:
        rel = source.resolve().relative_to(REPO_ROOT.resolve())
        return rel.with_suffix("")
    except ValueError:
        return Path("external") / source.stem


def process_csv(source: Path, output_rel: Path | None = None) -> None:
    if not source.exists() or not source.is_file():
        print(f"SKIP | missing source | {source}")
        return

    if output_rel is None:
        output_rel = rel_dataset_path(source)

    out_dir = AI_ROOT / output_rel
    out_dir.mkdir(parents=True, exist_ok=True)

    print("")
    print("#" * 100)
    print(f"PROCESS | {source.relative_to(REPO_ROOT) if source.is_relative_to(REPO_ROOT) else source}")
    print(f"SIZE    | {source.stat().st_size / (1024 * 1024):.2f} MB")
    print(f"OUTPUT  | {out_dir.relative_to(REPO_ROOT)}")
    print("#" * 100)

    result = chunk_by_rows(
        source=source,
        output_dir=out_dir,
        rows_per_chunk=ROWS_PER_CHUNK,
        encoding="utf-8-sig",
    )
    manifest = write_manifest(source, out_dir, result)
    print_summary(source, out_dir, result, manifest)


def download_remote_sources() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for item in REMOTE_SOURCES:
        destination = RAW_DIR / item["filename"]

        if destination.exists() and destination.stat().st_size > 0:
            print(f"DOWNLOAD | reuse existing | {destination}")
        else:
            download_stream(item["url"], destination)

        process_csv(destination, Path(item["name"]))


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return (
        "AI_Chunks" in parts
        or "_raw_large" in parts
        or "_tmp" in parts
        or ".git" in parts
    )


def discover_local_csvs() -> list[Path]:
    found: list[Path] = []
    minimum_bytes = int(MIN_SIZE_MB * 1024 * 1024)

    for root in SCAN_ROOTS:
        if not root.exists():
            print(f"SCAN | folder not present | {root}")
            continue

        print(f"SCAN | {root.relative_to(REPO_ROOT)}")
        for path in root.rglob("*.csv"):
            if should_skip(path):
                continue
            try:
                size = path.stat().st_size
            except OSError as exc:
                print(f"SKIP | cannot stat {path} | {exc}")
                continue

            if size >= minimum_bytes:
                found.append(path)
                print(
                    f"FOUND | {path.relative_to(REPO_ROOT)} | "
                    f"{size / (1024 * 1024):.2f} MB"
                )

    return sorted(set(found))


def process_local_sources() -> None:
    files = discover_local_csvs()

    if not files:
        print("SCAN | no local CSV files met the size threshold")
        return

    print(f"SCAN | {len(files)} CSV file(s) will be chunked")

    for source in files:
        try:
            process_csv(source)
        except Exception as exc:
            # One unusual/bad CSV must not stop all the other datasets.
            print(f"ERROR | {source} | {type(exc).__name__}: {exc}", file=sys.stderr)


def git_publish() -> None:
    # Only generated output and these helper files are staged.
    paths = [
        ".gitignore",
        "NQ/tools/chunk_market_csv.py",
        "NQ/tools/prepare_ai_chunks.py",
        "AI_Chunks",
    ]

    run(["git", "add", "--"] + paths)

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=REPO_ROOT,
    )

    if diff.returncode == 0:
        print("GIT | no new chunk changes to commit")
        return

    run(["git", "status", "--short"])
    run(["git", "commit", "-m", COMMIT_MESSAGE])
    run(["git", "push", "origin", "main"])
    print("GIT | push complete")


def main() -> int:
    print("=" * 100)
    print("ALGO STRATEGY | ALL LARGE CSV -> AI CHUNKS")
    print("=" * 100)
    print(f"Repo root      : {REPO_ROOT}")
    print(f"Scan roots     : NQ/data, Backtesting")
    print(f"Minimum size   : {MIN_SIZE_MB:.1f} MB")
    print(f"Rows per chunk : {ROWS_PER_CHUNK:,}")
    print(f"Raw staging    : {RAW_DIR.relative_to(REPO_ROOT)}")
    print(f"AI output      : {AI_ROOT.relative_to(REPO_ROOT)}")
    print("")

    ensure_repo()
    run(["git", "pull", "--ff-only", "origin", "main"])

    download_remote_sources()
    process_local_sources()
    git_publish()

    print("")
    print("=" * 100)
    print("DONE")
    print("Original CSV files were not changed.")
    print(f"Temporary external originals remain in: {RAW_DIR.relative_to(REPO_ROOT)}")
    print("You can manually remove that temporary folder later.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
