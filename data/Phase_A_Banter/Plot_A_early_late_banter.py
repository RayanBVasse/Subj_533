import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the NRC scores CSVs
early_df = pd.read_csv("Subj533_earlybanter_nrc_scores.csv")
late_df = pd.read_csv("Subj533_latebanter_nrc_scores.csv")

# List of emotion columns to analyze
emotion_cols = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 
                'sadness', 'surprise', 'trust', 'positive', 'negative']

# Compute average scores
early_means = early_df[emotion_cols].mean()
late_means = late_df[emotion_cols].mean()

# Combine into a single DataFrame for plotting
emotion_df = pd.DataFrame({
    'Emotion': emotion_cols,
    'Early Comm.': early_means.values,
    'Late Comm.': late_means.values
}).set_index('Emotion')

# Plot
plt.figure(figsize=(10, 6))
emotion_df.plot(kind='bar', colormap='Set2', width=0.8)
plt.title('Mean NRC Emotion Scores\nEarly vs Late Casual Communication')
plt.ylabel('Average Emotion Word Count per Message')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.legend(title='Period')
plt.show()
