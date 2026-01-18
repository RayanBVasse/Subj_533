import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
df = pd.read_csv("Subj533_phaseC_LLM_scores.csv")
df = df.sort_values("entry_index").reset_index(drop=True)

# Split into thirds
n = len(df)
df["segment"] = pd.cut(
    df.index,
    bins=[-1, n//3, 2*n//3, n],
    labels=["First third", "Middle third", "Final third"]
)

# Aggregate means
summary = df.groupby("segment", observed=True)[
    ["positive_affect_llm", "negative_affect_llm"]
].mean()

# Plot
x = np.arange(len(summary))
width = 0.35

plt.figure(figsize=(7,4))
plt.bar(x - width/2, summary["positive_affect_llm"], width, label="Positive affect")
plt.bar(x + width/2, summary["negative_affect_llm"], width, label="Negative affect")

plt.xticks(x, summary.index)
plt.ylabel("Mean affect (LLM inferred)")
plt.title("Phase C: Mean Positive and Negative Affect Across Corpus Segments")
plt.legend()
plt.tight_layout()

plt.show()
plt.savefig("PhaseC_affect_pos_neg_by_segment.png", dpi=300)


