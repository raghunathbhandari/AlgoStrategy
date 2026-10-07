#!/usr/bin/env python3
"""
Create small, AI-friendly CSV chunks from large market-data CSV files.

Designed for VPS use:
- download a large CSV directly to a temporary VPS folder (outside Git repo)
- stream the file without loading it all into RAM
- split by month (recommended for market data) or by row count
- write only small chunk files into the Git repository
- create a manifest so AI/tools can quickly see coverage

Examples
--------
# Download a large GitHub CSV to VPS temp storage, then split monthly:
python NQ/tools/chunk_market_csv.py \
  --url "https://github.com/s-k-28/nq-es-trader-5k-payout/blob/main/data/Dataset_NQ_1min_2022_2025.csv" \
  --download-dir /root/marketdata_raw \
  --output-dir NQ/data/AI_Chunks/NQ_1min_2022_2025 \
  --split month

# Chunk an existing local CSV:
python NQ/tools/chunk_market_csv.py \
  --input NQ/data/NQ_1min_20260401_20260902.csv \
  --output-dir NQ/data/AI_Chunks/NQ_1min_20260401_20260902 \
  --split month

# Fixed-size row chunks:
python NQ/tools/chunk_market_csv.py \
  --input /root/marketdata_raw/big.csv \
  --output-dir NQ/data/AI_Chunks/big \
  --split rows \
  --rows-per-chunk 25000
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


DATE_CANDIDATES = (
    "datetime",
    "date",
    "timestamp",
    "time",
    "Datetime",
    "Date",
    "Timestamp",
    "Time",
)


def github_blob_to_raw(url: str) -> str:
    """Convert a normal github.com/.../blob/... URL to raw.githubusercontent.com."""
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return url

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) >= 5 and parts[2] == "blob":
        owner, repo, _, branch = parts[:4]
        file_path = "/".join(parts[4:])
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
    return url


def filename_from_url(url: str) -> str:
    name = Path(urllib.parse.urlparse(url).path).name
    return name or "download.csv"


def download_stream(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    raw_url = github_blob_to_raw(url)

    print(f"DOWNLOAD | source={raw_url}")
    print(f"DOWNLOAD | target={destination}")

    req = urllib.request.Request(
        raw_url,
        headers={"User-Agent": "ASJR-CSV-Chunker/1.0"},
    )

    total = 0
    with urllib.request.urlopen(req, timeout=120) as response, destination.open("wb") as out:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            out.write(block)
            total += len(block)
            if total % (25 * 1024 * 1024) < len(block):
                print(f"DOWNLOAD | {total / (1024 * 1024):.1f} MB")

    print(f"DOWNLOAD | complete | {total / (1024 * 1024):.2f} MB")
    return destination


def parse_dt(value: str) -> Optional[datetime]:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    # Common ISO formats, including trailing Z.
    iso_text = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(iso_text)
    except ValueError:
        pass

    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    )
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    # Unix epoch seconds / milliseconds.
    try:
        n = float(text)
        if n > 10_000_000_000:
            n /= 1000.0
        if n > 1_000_000_000:
            return datetime.utcfromtimestamp(n)
    except (ValueError, OverflowError, OSError):
        pass

    return None


def detect_date_column(fieldnames: List[str], requested: Optional[str]) -> str:
    if requested:
        if requested not in fieldnames:
            raise ValueError(
                f"Requested date column '{requested}' not found. Columns: {fieldnames}"
            )
        return requested

    for candidate in DATE_CANDIDATES:
        if candidate in fieldnames:
            return candidate

    lower_map = {name.lower(): name for name in fieldnames}
    for candidate in DATE_CANDIDATES:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]

    raise ValueError(
        "Could not detect datetime column. "
        "Use --date-column. Columns: " + ", ".join(fieldnames)
    )


def safe_stem(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", path.stem).strip("_")
    return stem or "data"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def human_mb(nbytes: int) -> float:
    return round(nbytes / (1024 * 1024), 3)


def chunk_by_month(
    source: Path,
    output_dir: Path,
    date_column: Optional[str],
    encoding: str,
) -> Dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    writers: Dict[str, csv.DictWriter] = {}
    handles: Dict[str, object] = {}
    counts = defaultdict(int)
    first_dt: Dict[str, str] = {}
    last_dt: Dict[str, str] = {}
    skipped = 0

    try:
        with source.open("r", newline="", encoding=encoding) as src:
            reader = csv.DictReader(src)
            if not reader.fieldnames:
                raise ValueError("CSV has no header")

            fieldnames = list(reader.fieldnames)
            dt_col = detect_date_column(fieldnames, date_column)
            stem = safe_stem(source)

            print(f"CHUNK | mode=month | datetime_column={dt_col}")

            for row_num, row in enumerate(reader, start=2):
                dt = parse_dt(row.get(dt_col, ""))
                if dt is None:
                    skipped += 1
                    if skipped <= 5:
                        print(
                            f"WARNING | row={row_num} | cannot parse {dt_col}={row.get(dt_col)!r}",
                            file=sys.stderr,
                        )
                    continue

                key = dt.strftime("%Y-%m")
                if key not in writers:
                    out_path = output_dir / f"{stem}_{key}.csv"
                    handle = out_path.open("w", newline="", encoding="utf-8")
                    writer = csv.DictWriter(handle, fieldnames=fieldnames)
                    writer.writeheader()
                    handles[key] = handle
                    writers[key] = writer

                writers[key].writerow(row)
                counts[key] += 1
                dt_text = dt.isoformat()
                first_dt.setdefault(key, dt_text)
                last_dt[key] = dt_text

                if sum(counts.values()) % 100_000 == 0:
                    print(f"CHUNK | rows={sum(counts.values()):,}")
    finally:
        for handle in handles.values():
            handle.close()

    files = []
    total_rows = 0
    for key in sorted(counts):
        out_path = output_dir / f"{safe_stem(source)}_{key}.csv"
        rows = counts[key]
        total_rows += rows
        files.append(
            {
                "file": out_path.name,
                "period": key,
                "rows": rows,
                "first_datetime": first_dt.get(key),
                "last_datetime": last_dt.get(key),
                "size_mb": human_mb(out_path.stat().st_size),
            }
        )

    return {
        "split_mode": "month",
        "date_column": dt_col,
        "total_rows": total_rows,
        "skipped_rows": skipped,
        "files": files,
    }


def chunk_by_rows(
    source: Path,
    output_dir: Path,
    rows_per_chunk: int,
    encoding: str,
) -> Dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = safe_stem(source)
    total_rows = 0
    files = []
    chunk_number = 0
    chunk_rows = 0
    handle = None
    writer = None
    current_path = None

    try:
        with source.open("r", newline="", encoding=encoding) as src:
            reader = csv.reader(src)
            try:
                header = next(reader)
            except StopIteration:
                raise ValueError("CSV is empty")

            for row in reader:
                if writer is None or chunk_rows >= rows_per_chunk:
                    if handle is not None:
                        handle.close()
                        files.append(
                            {
                                "file": current_path.name,
                                "rows": chunk_rows,
                                "size_mb": human_mb(current_path.stat().st_size),
                            }
                        )

                    chunk_number += 1
                    chunk_rows = 0
                    current_path = output_dir / f"{stem}_part_{chunk_number:04d}.csv"
                    handle = current_path.open("w", newline="", encoding="utf-8")
                    writer = csv.writer(handle)
                    writer.writerow(header)

                writer.writerow(row)
                chunk_rows += 1
                total_rows += 1

                if total_rows % 100_000 == 0:
                    print(f"CHUNK | rows={total_rows:,}")

        if handle is not None:
            handle.close()
            files.append(
                {
                    "file": current_path.name,
                    "rows": chunk_rows,
                    "size_mb": human_mb(current_path.stat().st_size),
                }
            )
            handle = None
    finally:
        if handle is not None:
            handle.close()

    return {
        "split_mode": "rows",
        "rows_per_chunk": rows_per_chunk,
        "total_rows": total_rows,
        "skipped_rows": 0,
        "files": files,
    }


def write_manifest(source: Path, output_dir: Path, result: Dict) -> Path:
    manifest = {
        "source_file": str(source),
        "source_size_mb": human_mb(source.stat().st_size),
        "source_sha256": sha256_file(source),
        **result,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def print_summary(source: Path, output_dir: Path, result: Dict, manifest: Path) -> None:
    print("")
    print("=" * 90)
    print("AI CSV CHUNK SUMMARY")
    print("=" * 90)
    print(f"Source       : {source}")
    print(f"Source size  : {human_mb(source.stat().st_size):.3f} MB")
    print(f"Output dir   : {output_dir}")
    print(f"Split mode   : {result['split_mode']}")
    print(f"Rows written : {result['total_rows']:,}")
    print(f"Rows skipped : {result.get('skipped_rows', 0):,}")
    print(f"Chunk files  : {len(result['files'])}")
    print(f"Manifest     : {manifest}")
    print("-" * 90)
    for item in result["files"]:
        period = f" | {item.get('period')}" if item.get("period") else ""
        print(
            f"{item['file']} | rows={item['rows']:,} | "
            f"{item['size_mb']:.3f} MB{period}"
        )
    print("=" * 90)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stream large market CSVs into smaller AI-friendly Git files."
    )

    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="Existing CSV path on VPS")
    src.add_argument("--url", help="CSV URL to download first")

    parser.add_argument(
        "--download-dir",
        default="/root/marketdata_raw",
        help="VPS-only folder for large downloaded originals",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory for small CSV chunks (normally inside Git repo)",
    )
    parser.add_argument(
        "--split",
        choices=("month", "rows"),
        default="month",
        help="Split by calendar month or fixed row count",
    )
    parser.add_argument(
        "--rows-per-chunk",
        type=int,
        default=25000,
        help="Rows per file when --split rows is used",
    )
    parser.add_argument(
        "--date-column",
        help="Datetime column name for monthly splitting; auto-detected if omitted",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="Input CSV encoding (default utf-8-sig)",
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve()

    if args.url:
        download_dir = Path(args.download_dir).expanduser().resolve()
        source = download_dir / filename_from_url(args.url)
        if source.exists() and source.stat().st_size > 0:
            print(f"DOWNLOAD | reuse existing VPS file | {source}")
        else:
            download_stream(args.url, source)
    else:
        source = Path(args.input).expanduser().resolve()

    if not source.exists():
        print(f"ERROR | source does not exist: {source}", file=sys.stderr)
        return 2

    if source.resolve() == output_dir.resolve():
        print("ERROR | output directory cannot be the source file", file=sys.stderr)
        return 2

    if args.split == "month":
        result = chunk_by_month(
            source=source,
            output_dir=output_dir,
            date_column=args.date_column,
            encoding=args.encoding,
        )
    else:
        if args.rows_per_chunk <= 0:
            print("ERROR | --rows-per-chunk must be > 0", file=sys.stderr)
            return 2
        result = chunk_by_rows(
            source=source,
            output_dir=output_dir,
            rows_per_chunk=args.rows_per_chunk,
            encoding=args.encoding,
        )

    manifest = write_manifest(source, output_dir, result)
    print_summary(source, output_dir, result, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
