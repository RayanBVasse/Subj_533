from pathlib import Path
import pandas as pd
import sys
from datetime import datetime

# =========================
# CONFIG
# =========================

INPUT_FILE = "Subj533_nrc_scores.csv"
OUTPUT_FILE = "Subj533_nrc_volatility.csv"
EXEC_LOG = "nrc_volatility_execution_log.txt"

EXPECTED_ROWS = 531
ROLLING_WINDOW = 20   # fixed, documented

NEGATIVE_EMOTIONS = [
    "anger", "fear", "sadness", "disgust", "negative"
]

POSITIVE_EMOTIONS = [
    "joy", "trust", "positive"
]

# =========================
# LOAD DATA
# =========================

df = pd.read_csv(INPUT_FILE)

if len(df) != EXPECTED_ROWS:
    print(f"ERROR: Expected {EXPECTED_ROWS} rows, found {len(df)}")
    sys.exit(1)

# =========================
# NORMALIZE (counts → rates)
# =========================

for col in NEGATIVE_EMOTIONS + POSITIVE_EMOTIONS:
    df[col] = df[col] / df["word_count"]

# =========================
# COMPOSITE AFFECT
# =========================

df["negative_affect"] = df[NEGATIVE_EMOTIONS].mean(axis=1)
df["positive_affect"] = df[POSITIVE_EMOTIONS].mean(axis=1)

# =========================
# ROLLING VOLATILITY
# =========================

df["negative_volatility"] = (
    df["negative_affect"]
    .rolling(window=ROLLING_WINDOW, min_periods=5)
    .var()
)

df["positive_volatility"] = (
    df["positive_affect"]
    .rolling(window=ROLLING_WINDOW, min_periods=5)
    .var()
)

# =========================
# OUTPUT
# =========================

out = df[
    [
        "entry_index",
        "negative_affect",
        "positive_affect",
        "negative_volatility",
        "positive_volatility"
    ]
]

out.to_csv(OUTPUT_FILE, index=False)

# =========================
# EXECUTION LOG
# =========================

with open(EXEC_LOG, "w", encoding="utf-8") as f:
    f.write("=== NRC VOLATILITY EXECUTION LOG ===\n")
    f.write(f"Timestamp: {datetime.now()}\n")
    f.write(f"Input file: {INPUT_FILE}\n")
    f.write(f"Rows processed: {len(df)}\n")
    f.write(f"Rolling window: {ROLLING_WINDOW}\n")
    f.write("Method: NRC normalization + composite affect + rolling variance\n")
    f.write("Status: COMPLETE\n")

print("SUCCESS")
print(f"Rows processed: {len(df)}")
print(f"Output written: {OUTPUT_FILE}")
print(f"Execution log written: {EXEC_LOG}")
