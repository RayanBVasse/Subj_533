import re
import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

MESSAGES_CSV = BASE_DIR / "Subj533_msgs_only.csv"

# NRC lexicon format options:
# (A) Common: "NRC-Emotion-Lexicon-Wordlevel-v0.92.txt" with columns: word \t emotion \t association(0/1)
# (B) Or a CSV you created. If so, adjust loader below.
NRC_LEXICON = BASE_DIR / "NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"

TEXT_COL_CANDIDATES = ["text", "message", "content", "msg", "body"]  # adjust if needed

N_BINS = 10  # 10 bins -> ~53 each for 531 msgs

# -----------------------------
# Helpers
# -----------------------------
TOKEN_RE = re.compile(r"[A-Za-z']+")

def pick_text_column(df: pd.DataFrame) -> str:
    for c in TEXT_COL_CANDIDATES:
        if c in df.columns:
            return c
    raise ValueError(f"Could not find a text column. Available columns: {list(df.columns)}")

def tokenize(text: str):
    if not isinstance(text, str):
        return []
    return TOKEN_RE.findall(text.lower())

def load_nrc_word_sets(path: Path):
    """
    Loads NRC v0.92 word-level lexicon (tab-separated).
    Returns sets for 'positive' and 'negative' categories (NRC sentiment).
    """
    if not path.exists():
        raise FileNotFoundError(f"NRC lexicon not found: {path}")

    # NRC file is usually tab-separated with no header:
    # word \t emotion \t association
    lex = pd.read_csv(path, sep="\t", header=None, names=["word", "category", "assoc"])
    lex = lex[lex["assoc"] == 1]

    pos_words = set(lex.loc[lex["category"] == "positive", "word"])
    neg_words = set(lex.loc[lex["category"] == "negative", "word"])

    if len(pos_words) == 0 or len(neg_words) == 0:
        raise ValueError("Loaded NRC lexicon but got empty positive/negative sets. Check file format.")

    return pos_words, neg_words

def cohens_d_independent(x1, x2):
    """Cohen's d (pooled SD), independent groups."""
    x1 = np.asarray(x1, dtype=float)
    x2 = np.asarray(x2, dtype=float)
    x1 = x1[~np.isnan(x1)]
    x2 = x2[~np.isnan(x2)]

    n1, n2 = len(x1), len(x2)
    if n1 < 2 or n2 < 2:
        return np.nan

    s1 = np.var(x1, ddof=1)
    s2 = np.var(x2, ddof=1)
    pooled = np.sqrt(((n1 - 1)*s1 + (n2 - 1)*s2) / (n1 + n2 - 2))
    if pooled == 0:
        return np.nan
    return (np.mean(x2) - np.mean(x1)) / pooled

# -----------------------------
# Main
# -----------------------------
def main():
    # Load messages
    df = pd.read_csv(MESSAGES_CSV)
    text_col = pick_text_column(df)
    df = df[[text_col]].copy()
    df.rename(columns={text_col: "text"}, inplace=True)

    # Tokenize + token counts
    df["tokens"] = df["text"].apply(tokenize)
    df["token_count"] = df["tokens"].apply(len)

    # Guard: remove empty-token messages (or keep them but they will yield NaN rates)
    # I recommend keeping them but setting rates = NaN when token_count == 0.
    # That matches "short messages retained" without dividing by zero.
    pos_words, neg_words = load_nrc_word_sets(NRC_LEXICON)

    def count_matches(tok_list, wordset):
        return sum(1 for t in tok_list if t in wordset)

    df["pos_count"] = df["tokens"].apply(lambda t: count_matches(t, pos_words))
    df["neg_count"] = df["tokens"].apply(lambda t: count_matches(t, neg_words))

    # Rate per 100 words
    df["pos_rate_100w"] = np.where(df["token_count"] > 0, (df["pos_count"] / df["token_count"]) * 100, np.nan)
    df["neg_rate_100w"] = np.where(df["token_count"] > 0, (df["neg_count"] / df["token_count"]) * 100, np.nan)

    # Bin into 10 chronological bins by row order
    n = len(df)
    if n < N_BINS:
        raise ValueError(f"Not enough rows ({n}) for {N_BINS} bins.")

    # Equal-size bins as close as possible: use integer bin index based on position
    df["bin"] = (np.floor(np.arange(n) * N_BINS / n)).astype(int)
    df.loc[df["bin"] == N_BINS, "bin"] = N_BINS - 1  # safety

    # Summaries: mean and SD within each bin
    summary = df.groupby("bin").agg(
        pos_mean=("pos_rate_100w", "mean"),
        pos_sd=("pos_rate_100w", "std"),
        neg_mean=("neg_rate_100w", "mean"),
        neg_sd=("neg_rate_100w", "std"),
        n_msgs=("text", "count")
    ).reset_index()

    # Cohen's d between first and last bin (bin 0 vs bin 9)
    bin0_pos = df[df["bin"] == 0]["pos_rate_100w"]
    bin9_pos = df[df["bin"] == (N_BINS - 1)]["pos_rate_100w"]
    d_pos = cohens_d_independent(bin0_pos, bin9_pos)

    bin0_neg = df[df["bin"] == 0]["neg_rate_100w"]
    bin9_neg = df[df["bin"] == (N_BINS - 1)]["neg_rate_100w"]
    d_neg = cohens_d_independent(bin0_neg, bin9_neg)

    print("---- Phase A NRC (per 100 words), 10 bins ----")
    print(summary)
    print(f"\nCohen's d (bin0 vs bin{N_BINS-1})")
    print(f"  Positive: {d_pos:.3f}")
    print(f"  Negative: {d_neg:.3f}")

    # Plot with error bars
    x = summary["bin"].to_numpy()
    plt.figure(figsize=(8, 5))
    plt.errorbar(x, summary["pos_mean"], yerr=summary["pos_sd"], capsize=3, label="Positive (NRC)")
    plt.errorbar(x, summary["neg_mean"], yerr=summary["neg_sd"], capsize=3, label="Negative (NRC)")
    plt.title("Exploratory coarse temporal binning (10 bins, NRC)")
    plt.xlabel("Chronological bin (earliest → latest)")
    plt.ylabel("Mean NRC term rate (per 100 words)")
    plt.legend()
    plt.tight_layout()

    outpath = BASE_DIR / "Figure_NRC_10bin_per100w.png"
    plt.savefig(outpath, dpi=300)
    print(f"\nSaved plot: {outpath}")

if __name__ == "__main__":
    main()
