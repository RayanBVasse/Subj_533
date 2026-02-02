import re
import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.stats import spearmanr

# -----------------------------
# CONFIG
# -----------------------------
TEXT_FILE = "Combined_Patient_533_threads.txt"
MODEL_NAME = "SamLowe/roberta-base-go_emotions"
ROLLING_WINDOW = 20
OUTPUT_CSV = "phaseB_goemotions_scores.csv"

# -----------------------------
# LOAD AND PREPARE DATA
# -----------------------------
with open(TEXT_FILE, "r", encoding="utf-8") as f:
    raw_text = f.read()

entries = re.split(r"\[user\]: ", raw_text)[1:]

data = pd.DataFrame({
    "entry_index": range(1, len(entries) + 1),
    "text": entries
})

print(f"Loaded {len(data)} patient entries")

# -----------------------------
# LOAD MODEL
# -----------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

emotion_labels = model.config.id2label

# -----------------------------
# PHASE B COLLAPSE MAP
# -----------------------------
PHASE_B_MAP = {
    "sadness": ["sadness", "grief"],
    "anxiety": ["fear", "nervousness"],
    "anger": ["anger", "annoyance"],
    "joy": ["joy", "excitement"],
    "calm": ["relief", "contentment"]
}

# -----------------------------
# INFERENCE
# -----------------------------
results = []

for _, row in tqdm(data.iterrows(), total=len(data)):
    inputs = tokenizer(
        row["text"],
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.sigmoid(outputs.logits).numpy()[0]

    scores = {}
    for dim, labels in PHASE_B_MAP.items():
        scores[dim] = np.mean([
            probs[list(emotion_labels.values()).index(lbl)]
            for lbl in labels
            if lbl in emotion_labels.values()
        ])

    scores["entry_index"] = row["entry_index"]
    results.append(scores)

df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved Phase B scores to {OUTPUT_CSV}")

# -----------------------------
# ROLLING VARIANCE
# -----------------------------
df["negative_sum"] = df[["sadness", "anxiety", "anger"]].sum(axis=1)
df["positive_sum"] = df[["joy", "calm"]].sum(axis=1)

df["neg_var"] = df["negative_sum"].rolling(ROLLING_WINDOW).var()
df["pos_var"] = df["positive_sum"].rolling(ROLLING_WINDOW).var()

# -----------------------------
# PLOTS
# -----------------------------
plt.figure(figsize=(14,6))
plt.plot(df["entry_index"], df["neg_var"], label="Negative Variance")
plt.plot(df["entry_index"], df["pos_var"], label="Positive Variance")
plt.xlabel("Entry Index")
plt.ylabel("Rolling Variance")
plt.title("Phase B1: Emotional Volatility (GoEmotions)")
plt.legend()
plt.tight_layout()
plt.show()