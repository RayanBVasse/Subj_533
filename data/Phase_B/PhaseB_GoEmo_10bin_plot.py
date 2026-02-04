from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "Subj533_goemotions_scores.csv"

N_BINS = 10

def cohens_d_independent(x1, x2):
    """Cohen's d (pooled SD), independent groups: (mean_last - mean_first)/pooled."""
    x1 = np.asarray(x1, dtype=float)
    x2 = np.asarray(x2, dtype=float)
    x1 = x1[~np.isnan(x1)]
    x2 = x2[~np.isnan(x2)]
    n1, n2 = len(x1), len(x2)
    if n1 < 2 or n2 < 2:
        return np.nan
    s1 = np.var(x1, ddof=1)
    s2 = np.var(x2, ddof=1)
    pooled = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if pooled == 0:
        return np.nan
    return (np.mean(x2) - np.mean(x1)) / pooled

def main():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)

    # Expected columns (case-insensitive friendly)
    colmap = {c.lower(): c for c in df.columns}
    required = ["sadness", "anxiety", "anger", "joy", "calm", "entry_index"]
    missing = [c for c in required if c not in colmap]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found: {list(df.columns)}")

    # Sort chronologically
    df = df.sort_values(colmap["entry_index"]).reset_index(drop=True)

    # Ensure numeric
    for k in ["sadness", "anxiety", "anger", "joy", "calm"]:
        df[colmap[k]] = pd.to_numeric(df[colmap[k]], errors="coerce")

    # Aggregate super-scores
    df["neg_score"] = df[colmap["sadness"]] + df[colmap["anxiety"]] + df[colmap["anger"]]
    df["pos_score"] = df[colmap["joy"]] + df[colmap["calm"]]

    n = len(df)
    df["bin"] = (np.floor(np.arange(n) * N_BINS / n)).astype(int)
    df.loc[df["bin"] == N_BINS, "bin"] = N_BINS - 1

    summary = df.groupby("bin").agg(
        pos_mean=("pos_score", "mean"),
        pos_sd=("pos_score", "std"),
        neg_mean=("neg_score", "mean"),
        neg_sd=("neg_score", "std"),
        n_msgs=("bin", "count"),
    ).reset_index()

    d_pos = cohens_d_independent(df[df["bin"] == 0]["pos_score"], df[df["bin"] == (N_BINS - 1)]["pos_score"])
    d_neg = cohens_d_independent(df[df["bin"] == 0]["neg_score"], df[df["bin"] == (N_BINS - 1)]["neg_score"])

    print("---- Phase B (5-dim emotions), 10 bins ----")
    print("Positive = joy + calm; Negative = sadness + anxiety + anger")
    print(summary)
    print(f"\nCohen's d (bin0 vs bin{N_BINS-1})")
    print(f"  Positive: {d_pos:.3f}")
    print(f"  Negative: {d_neg:.3f}")

    out_csv = BASE_DIR / "PhaseB_5dim_10bin_summary.csv"
    summary.to_csv(out_csv, index=False)
    print(f"\nSaved summary: {out_csv}")

    # Plot
    x = summary["bin"].to_numpy()
    plt.figure(figsize=(8, 5))
    plt.errorbar(x, summary["pos_mean"], yerr=summary["pos_sd"], capsize=3, label="Positive (joy+calm)")
    plt.errorbar(x, summary["neg_mean"], yerr=summary["neg_sd"], capsize=3, label="Negative (sadness+anxiety+anger)")
    plt.title("Exploratory coarse temporal binning (10 bins, Phase B classifier)")
    plt.xlabel("Chronological bin (earliest → latest)")
    plt.ylabel("Mean emotion score (aggregated)")
    plt.legend()
    plt.tight_layout()

    out_png = BASE_DIR / "Figure_PhaseB_10bin.png"
    plt.savefig(out_png, dpi=300)
    print(f"Saved plot: {out_png}")

if __name__ == "__main__":
    main()
