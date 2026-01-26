import pandas as pd
import matplotlib.pyplot as plt
import os

# === FILEPATHS ===
FOLDER = "."  # Set to your working directory
MSG_FILE = os.path.join(FOLDER, "Subj533_msgs_only.csv")
LEXICON_FILE = os.path.join(FOLDER, "NRC-Emotion-Lexicon-Wordlevel-v0.92.txt")
EARLY_FILE = os.path.join(FOLDER, "Subj533_therapeutic_early_175.csv")
LATE_FILE = os.path.join(FOLDER, "Subj533_therapeutic_late_175.csv")

# === LOAD MESSAGES ===
df = pd.read_csv(MSG_FILE)
df = df.dropna(subset=["text"])  # drop empty messages

# Split first and last 175
early_df = df.head(175)
late_df = df.tail(175)

early_df.to_csv(EARLY_FILE, index=False)
late_df.to_csv(LATE_FILE, index=False)

# === LOAD NRC LEXICON ===
nrc = pd.read_csv(
    LEXICON_FILE,
    sep="\t",
    names=["word", "emotion", "association"],
    encoding="utf-8"
)
nrc = nrc[nrc['association'] == 1]
pos_words = set(nrc[nrc["emotion"] == "positive"]["word"])
neg_words = set(nrc[nrc["emotion"] == "negative"]["word"])

def compute_scores(text_series):
    pos, neg = 0, 0
    for text in text_series.dropna():
        tokens = str(text).lower().split()
        pos += sum(1 for t in tokens if t in pos_words)
        neg += sum(1 for t in tokens if t in neg_words)
    return pos, neg

# === COMPUTE SCORES ===
early_pos, early_neg = compute_scores(early_df["text"])
late_pos, late_neg = compute_scores(late_df["text"])

# Normalize by number of messages
early_n, late_n = len(early_df), len(late_df)
data = {
    "Positive": [early_pos / early_n, late_pos / late_n],
    "Negative": [early_neg / early_n, late_neg / late_n]
}
result_df = pd.DataFrame(data, index=["Early", "Late"])
print(result_df)

# === PLOT ===
ax = result_df.plot(kind="bar", rot=0, figsize=(6, 4), ylabel="Avg. emotion words per message")
plt.title("NRC Emotion Comparison: Early vs Late Therapeutic Chat")
plt.tight_layout()
plt.savefig(os.path.join(FOLDER, "Figure_NRC_PosNeg_Therapeutic_175s.png"))
plt.show()
