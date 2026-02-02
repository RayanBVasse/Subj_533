from pathlib import Path
import csv
import sys
from collections import defaultdict
from datetime import datetime

# =========================
# CONFIG
# =========================

INPUT_FILE = "Subj533_therapeutic_late_175_msgs.txt"
NRC_LEXICON = "NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"
OUTPUT_FILE = "Subj533_late175therua_nrc_scores.csv"
EXEC_LOG = "nrc_late175therua_execution_log.txt"

#EXPECTED_ROWS = 531

EMOTIONS = [
    "anger", "anticipation", "disgust", "fear",
    "joy", "sadness", "surprise", "trust",
    "positive", "negative"
]

# =========================
# LOAD NRC LEXICON
# =========================

nrc = defaultdict(set)

with open(NRC_LEXICON, encoding="utf-8") as f:
    for line in f:
        word, emotion, flag = line.strip().split("\t")
        if flag == "1":
            nrc[word].add(emotion)

# =========================
# READ INPUT
# =========================

rows = []
with open(INPUT_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

#if len(rows) != EXPECTED_ROWS:
#    print(f"ERROR: Expected {EXPECTED_ROWS} rows, found {len(rows)}")
#    sys.exit(1)

# =========================
# ANALYSIS
# =========================

results = []

for row in rows:
    text = row["text"].lower()
    tokens = text.split()
    counts = dict.fromkeys(EMOTIONS, 0)

    for token in tokens:
        if token in nrc:
            for emo in nrc[token]:
                counts[emo] += 1

    counts["entry_index"] = row["entry_index"]
    counts["word_count"] = len(tokens)

    results.append(counts)

# =========================
# WRITE OUTPUT
# =========================

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["entry_index", "word_count"] + EMOTIONS
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow(r)

# =========================
# EXECUTION LOG
# =========================

with open(EXEC_LOG, "w", encoding="utf-8") as f:
    f.write("=== NRC EXECUTION LOG ===\n")
    f.write(f"Timestamp: {datetime.now()}\n")
    f.write(f"Input file: {INPUT_FILE}\n")
    #f.write(f"Expected rows: {EXPECTED_ROWS}\n")
    f.write(f"Rows processed: {len(results)}\n")
    f.write("Method: NRC Emotion Lexicon\n")
    f.write("Status: COMPLETE\n")

print("SUCCESS")
print(f"Rows processed: {len(results)}")
print(f"Output written: {OUTPUT_FILE}")
print(f"Execution log written: {EXEC_LOG}")
