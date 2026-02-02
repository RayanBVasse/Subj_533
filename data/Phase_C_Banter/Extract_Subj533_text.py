from pathlib import Path
import csv
import sys

INPUT_FILE = "Thread 03_04 merged_late.txt"
OUTPUT_FILE = "Subj533_late_banter_only.csv"

text = Path(INPUT_FILE).read_text(encoding="utf-8", errors="ignore")

# Split into message blocks (same rule as coverage manifest)
entries = [e.strip() for e in text.split("\n\n") if e.strip()]

user_rows = []

for idx, entry in enumerate(entries, start=1):
    if entry.lower().startswith("[user]"):
        # remove leading [user] or [user]:
        cleaned = entry.split("]", 1)[-1].lstrip(":").strip()
        if cleaned:
            user_rows.append((idx, cleaned))

# HARD CHECK — do not proceed silently
EXPECTED_USER_COUNT = 403

if len(user_rows) != EXPECTED_USER_COUNT:
    print(f"ERROR: Expected {EXPECTED_USER_COUNT} USER messages, found {len(user_rows)}")
    sys.exit(1)

# Write CSV
with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["entry_index", "text"])
    for row in user_rows:
        writer.writerow(row)

print("SUCCESS")
print(f"USER messages exported: {len(user_rows)}")
print(f"Output file: {OUTPUT_FILE}")
