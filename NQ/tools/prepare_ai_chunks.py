#!/usr/bin/env python3
"""
One-command VPS job for preparing AI-readable market-data chunks.

Run from anywhere inside the cloned AlgoStrategy repository:
    python NQ/tools/prepare_ai_chunks.py

What it does:
1. Finds the AlgoStrategy repository root automatically.
2. Downloads the known oversized NQ CSV into a Git-ignored staging folder.
3. Chunks the oversized file into smaller monthly CSVs.
4. Chunks large CSVs already stored in NQ/data.
5. Writes manifests for AI/tools.
6. Git-adds only the AI chunk outputs and scripts.
7. Commits and pushes to origin/main when there are changes.

The oversized staging copy is NEVER added to Git.
You can manually remove NQ/data/_raw_large next week.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
TOOLS_DIR = THIS_FILE.parent
REPO_ROOT = TOOLS_DIR.parents[1]
NQ_DATA = REPO_ROOT / "NQ" / "data"
RAW_DIR = NQ_DATA / "_raw_large"
AI_ROOT = NQ_DATA / "AI_Chunks"

sys.path.insert(0, str(TOOLS_DIR))
from chunk_market_csv import download_stream, chunk_by_month, write_manifest, print_summary  # noqa: E402


# Known oversized source that GitHub cannot accept normally.
REMOTE_SOURCES = [
    {
        "name": "Dataset_NQ_1min_2022_2025",
        "url": "https://github.com/s-k-28/nq-es-trader-5k-payout/blob/main/data/Dataset_NQ_1min_2022_2025.csv",
        "filename": "Dataset_NQ_1min_2022_2025.csv",
        "date_column": None,
    },
]

# Large CSVs already kept in AlgoStrategy/NQ/data that should also be
# converted into AI-friendly monthly chunks when present on the VPS.
LOCAL_SOURCES = [
    {
        "path": NQ_DATA / "NQ_1min_20260401_20260902.csv",
        "name": "NQ_1min_20260401_20260902",
        "date_column": None,
    },
    {
        "path": NQ_DATA / "NQ_5min_20260120_20260415.csv",
        "name": "NQ_5min_20260120_20260415",
        "date_column": None,
    },
]

COMMIT_MESSAGE = "Add AI-readable chunks for large NQ market data"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("RUN | " + " ".join(cmd))
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        check=check,
    )


def ensure_repo() -> None:
    git_dir = REPO_ROOT / ".git"
    if not git_dir.exists():
        raise RuntimeError(f"Not a Git repository: {REPO_ROOT}")


def process_csv(source: Path, dataset_name: str, date_column: str | None = None) -> None:
    if not source.exists():
        print(f"SKIP | missing source | {source}")
        return

    out_dir = AI_ROOT / dataset_name
    out_dir.mkdir(parents=True, exist_ok=True)

    print("")
    print("#" * 100)
    print(f"PROCESS | {dataset_name}")
    print(f"SOURCE  | {source}")
    print(f"OUTPUT  | {out_dir}")
    print("#" * 100)

    result = chunk_by_month(
        source=source,
        output_dir=out_dir,
        date_column=date_column,
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

        process_csv(
            source=destination,
            dataset_name=item["name"],
            date_column=item.get("date_column"),
        )


def process_local_sources() -> None:
    for item in LOCAL_SOURCES:
        process_csv(
            source=item["path"],
            dataset_name=item["name"],
            date_column=item.get("date_column"),
        )


def git_publish() -> None:
    # Safety: only stage the scripts, .gitignore and AI_Chunks.
    paths = [
        ".gitignore",
        "NQ/tools/chunk_market_csv.py",
        "NQ/tools/prepare_ai_chunks.py",
        "NQ/data/AI_Chunks",
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
    print("ALGO STRATEGY | LARGE CSV -> AI CHUNKS")
    print("=" * 100)
    print(f"Repo root : {REPO_ROOT}")
    print(f"Raw stage : {RAW_DIR}")
    print(f"AI chunks : {AI_ROOT}")
    print("")

    ensure_repo()

    # Pull first so the VPS works from the latest main branch.
    run(["git", "pull", "--ff-only", "origin", "main"])

    download_remote_sources()
    process_local_sources()
    git_publish()

    print("")
    print("=" * 100)
    print("DONE")
    print(f"Large temporary originals remain only in: {RAW_DIR}")
    print("They are Git-ignored and can be manually deleted later.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
