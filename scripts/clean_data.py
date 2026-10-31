"""Clean the Kaggle Video Game Sales CSV and save a reproducible cleaned file."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "dataset" / "vgsales.csv"
OUTPUT = ROOT / "dataset" / "vgsales_clean.csv"

EXPECTED = [
    "Name", "Platform", "Year", "Genre", "Publisher",
    "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales",
]
SALES = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]

def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"File tidak ditemukan: {INPUT}\n"
            "Unduh dataset dari Kaggle dan simpan sebagai dataset/vgsales.csv."
        )

    df = pd.read_csv(INPUT)
    df.columns = [str(c).strip() for c in df.columns]

    missing = set(EXPECTED) - set(df.columns)
    if missing:
        raise ValueError(
            "Kolom wajib tidak ditemukan: " + ", ".join(sorted(missing))
            + ". Pastikan CSV berasal dari dataset Video Game Sales yang benar."
        )

    before = len(df)
    df = df.drop_duplicates().copy()

    for col in ["Name", "Platform", "Genre", "Publisher"]:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace({"": pd.NA, "N/A": pd.NA, "nan": pd.NA})

    for col in ["Year", *SALES]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Core identity and outcome fields are required for this dashboard.
    df = df.dropna(subset=["Name", "Platform", "Genre", "Global_Sales"])
    # Negative sales are invalid for this dataset; missing regional sales are kept missing.
    df = df[df["Global_Sales"] >= 0]
    for col in SALES:
        df = df[df[col].isna() | (df[col] >= 0)]

    df["Year"] = df["Year"].round().astype("Int64")
    df = df[EXPECTED + (["Rank"] if "Rank" in df.columns else [])]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print("Pembersihan selesai.")
    print(f"Baris awal: {before:,}")
    print(f"Baris setelah pembersihan: {len(df):,}")
    print(f"Baris dihapus: {before - len(df):,}")
    print(f"File output: {OUTPUT}")
    print("\nMissing values per kolom:")
    print(df.isna().sum().to_string())

if __name__ == "__main__":
    main()
