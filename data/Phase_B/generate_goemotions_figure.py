import pandas as pd
import matplotlib.pyplot as plt

# ---- CONFIG ----
INPUT_FILE = "Subj533_goemotions_scores.csv"
WINDOW = 20

EMOTIONS = ["sadness", "anxiety", "anger", "joy", "calm"]

# ---- LOAD ----
df = pd.read_csv(INPUT_FILE)
df = df.sort_values("entry_index")

# ---- COMPUTE ROLLING VARIANCE ----
vol_df = pd.DataFrame()
vol_df["entry_index"] = df["entry_index"]

for emo in EMOTIONS:
    vol_df[emo] = df[emo].rolling(WINDOW, min_periods=WINDOW).var()

# ---- PLOT ----
plt.figure(figsize=(10, 5))

for emo in EMOTIONS:
    plt.plot(vol_df["entry_index"], vol_df[emo], label=emo)

plt.xlabel("Conversation Entry Index")
plt.ylabel("Rolling Variance (Volatility)")
plt.title("Phase B: Emotional Volatility Over Time (GoEmotions)")
plt.legend()
plt.tight_layout()

plt.savefig("Figure_PhaseB_GoEmotions_Volatility.png", dpi=300)
plt.show()
