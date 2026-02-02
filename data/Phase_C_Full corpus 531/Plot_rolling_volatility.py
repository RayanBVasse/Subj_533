
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Subj533_phaseC_LLM_scores.csv")
df = df.sort_values("entry_index")

plt.figure(figsize=(10,4))
plt.plot(df["entry_index"], df["positive_affect_llm"], label="Positive affect", alpha=0.7)
plt.plot(df["entry_index"], df["negative_affect_llm"], label="Negative affect", alpha=0.7)

plt.xlabel("Conversational entry (temporal order)")
plt.ylabel("LLM-inferred affect")
plt.title("Phase C: LLM-Inferred Positive and Negative Affect Over Time")
plt.legend()
plt.tight_layout()
plt.show()


window = 25

plt.figure(figsize=(10,4))
plt.plot(
    df["entry_index"],
    df["positive_affect_llm"].rolling(window).mean(),
    label="Positive affect (rolling mean)"
)
plt.plot(
    df["entry_index"],
    df["negative_affect_llm"].rolling(window).mean(),
    label="Negative affect (rolling mean)"
)

plt.xlabel("Conversational entry (temporal order)")
plt.ylabel("LLM-inferred affect")
plt.title("Phase C: Rolling Mean Affect Over Time")
plt.legend()
plt.tight_layout()
plt.show()
