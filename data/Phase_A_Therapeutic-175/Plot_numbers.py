import matplotlib.pyplot as plt
import numpy as np

# Data
conditions = [
    "Early banter",
    "Late banter",
    "Early therapeutic",
    "Late therapeutic"
]

positive = [1.70, 4.86, 2.96, 6.95]
negative = [0.63, 1.66, 1.10, 2.39]

x = np.arange(len(conditions))
width = 0.35

# Plot
plt.figure(figsize=(8, 5))
plt.bar(x - width/2, positive, width, label="Positive (NRC)")
plt.bar(x + width/2, negative, width, label="Negative (NRC)")

plt.xticks(x, conditions, rotation=20)
plt.ylabel("Mean NRC count per message")
plt.title("Positive and Negative NRC Scores Across Corpora and Time")
plt.legend()

plt.tight_layout()
plt.show()
