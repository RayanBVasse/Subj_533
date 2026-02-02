import pandas as pd
import matplotlib.pyplot as plt

# Load NRC scores
early = pd.read_csv("Subj533_earlybanter_nrc_scores.csv")
late = pd.read_csv("Subj533_latebanter_nrc_scores.csv")

# Calculate mean of 'positive' and 'negative' columns
means = {
    'Early Comm.': [early['positive'].mean(), early['negative'].mean()],
    'Late Comm.': [late['positive'].mean(), late['negative'].mean()]
}

# Convert to DataFrame for plotting
df = pd.DataFrame(means, index=['Positive', 'Negative'])

# Plot
ax = df.plot(kind='bar', figsize=(7, 5), rot=0)
ax.set_ylabel("Mean NRC Score")
ax.set_title("Figure 2a. NRC Positive and Negative Emotion Scores\nEarly vs Late Casual Communication")
plt.tight_layout()
plt.savefig("Figure_2a_Pos_Neg_Early_Late.png")
plt.show()
