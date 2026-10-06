from pathlib import Path
from urllib.request import urlretrieve

RAW_URL = "https://raw.githubusercontent.com/s-k-28/nq-es-trader-5k-payout/main/data/Dataset_NQ_1min_2022_2025.csv"
DEST = Path(__file__).resolve().parents[1] / "data" / "NQ" / "Dataset_NQ_1min_2022_2025.csv"

def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists() and DEST.stat().st_size > 1_000_000:
        print(f"Already exists: {DEST} ({DEST.stat().st_size/1024/1024:.1f} MB)")
        return
    print(f"Downloading NQ dataset to {DEST}")
    urlretrieve(RAW_URL, DEST)
    print(f"Done: {DEST} ({DEST.stat().st_size/1024/1024:.1f} MB)")

if __name__ == "__main__":
    main()
