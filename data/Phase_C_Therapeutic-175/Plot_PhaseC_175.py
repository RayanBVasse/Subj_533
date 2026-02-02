import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

# Load the early and late Phase C outputs
early_FILE = Path(__file__).resolve().parent / "Subj533_phaseC_early175.csv"
late_FILE = Path(__file__).resolve().parent / "Subj533_phaseC_late175.csv" 
early_df = pd.read_csv(early_FILE)
late_df = pd.read_csv(late_FILE)

# FIX: Remove any trailing spaces or BOM issues in column names
early_df.columns = early_df.columns.str.strip()
late_df.columns = late_df.columns.str.strip()

# Compute mean scores for positive and negative emotion fields
early_means = early_df[["positive_affect_llm", "negative_affect_llm"]].mean()
late_means = late_df[["positive_affect_llm", "negative_affect_llm"]].mean()

# Plot setup
labels = ["Positive Emotion", "Negative Emotion"]
early_vals = [early_means["positive_affect_llm"], early_means["negative_affect_llm"]]
late_vals = [late_means["positive_affect_llm"], late_means["negative_affect_llm"]]


x = range(len(labels))
width = 0.35

fig, ax = plt.subplots()
ax.bar([p - width/2 for p in x], early_vals, width, label='Early Comm.')
ax.bar([p + width/2 for p in x], late_vals, width, label='Late Comm.')

ax.set_ylabel('Mean Score')
ax.set_title('Phase C LLM Scores for Early vs Late Therapeutic Chat (n=175 each)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.tight_layout()
plt.savefig("Figure_PhaseC_LLM_Early_Late_Therapy_175.png")
plt.show()
