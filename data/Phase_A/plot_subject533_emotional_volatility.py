import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Configuration
# =========================

INPUT_CSV = "phaseB_goemotions_scores.csv"
ROLLING_WINDOW = 20
OUTPUT_FIG = "Figure_1_Patient533_Emotional_Volatility.png"

NEGATIVE_COLS = ["sadness", "anxiety", "anger"]
POSITIVE_COLS = ["joy", "calm"]

# =========================
# Load data
# =========================

df = pd.read_csv(INPUT_CSV)

# Ensure correct temporal order
df = df.sort_values("entry_index").reset_index(drop=True)

# =========================
# Compute affect scores
# =========================

df["negative_affect"] = df[NEGATIVE_COLS].mean(axis=1)
df["positive_affect"] = df[POSITIVE_COLS].mean(axis=1)

# =========================
# Compute rolling volatility
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
# Plot
# =========================

plt.figure(figsize=(10, 5))

plt.plot(
    df["entry_index"],
    df["positive_volatility"],
    label="Positive emotional volatility",
    linewidth=2
)

plt.plot(
    df["entry_index"],
    df["negative_volatility"],
    label="Negative emotional volatility",
    linewidth=2
)

plt.xlabel("Conversational entry (temporal order)")
plt.ylabel("Rolling emotional volatility")
plt.title("Longitudinal Emotional Volatility in a Single-Author ChatGPT Conversation")

plt.legend()
plt.tight_layout()

plt.savefig(OUTPUT_FIG, dpi=300)
plt.show()

print(f"Figure saved as: {OUTPUT_FIG}")
