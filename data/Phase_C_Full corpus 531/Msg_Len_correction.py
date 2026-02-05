"""
NRC Emotion Analysis with Message Length Correction
Demonstrates the message length confound in longitudinal text analysis

Input files needed:
1. Subj_533_msg_only.txt - One message per line
2. NRC-Emotion-Lexicon-Wordlevel-v0.92.txt - NRC lexicon file

Output:
- CSV with corrected metrics
- Multi-panel visualization showing the confound
"""

import re
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================================
# CONFIGURATION
# ============================================================================

TRANSCRIPT_PATH = 'Subj533_msgs_only.csv'  # One message per line
NRC_LEXICON_PATH = 'NRC-Emotion-Lexicon-Wordlevel-v0.92.txt'
OUTPUT_CSV = 'NRC_corrected_analysis.csv'
OUTPUT_FIGURE = 'message_length_confound_figure.png'

N_BINS = 10  # Number of temporal bins

# ============================================================================
# LOAD NRC LEXICON
# ============================================================================

def load_nrc_lexicon(filepath):
    """
    Load NRC lexicon and extract positive/negative emotion words.
    
    NRC format: word	emotion	association
    e.g., "abandon	anger	1"
    
    Returns two sets: positive_words, negative_words
    """
    positive_words = set()
    negative_words = set()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split('\t')
            if len(parts) != 3:
                continue
                
            word, emotion, association = parts
            
            if association == '1':
                if emotion == 'positive':
                    positive_words.add(word.lower())
                elif emotion == 'negative':
                    negative_words.add(word.lower())
    
    print(f"Loaded NRC lexicon: {len(positive_words)} positive, {len(negative_words)} negative words")
    return positive_words, negative_words

# ============================================================================
# LOAD MESSAGES
# ============================================================================

def load_messages(filepath):
    """Load messages from file (one per line)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        messages = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(messages)} messages")
    return messages

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def count_words(text):
    """Count total words in text"""
    words = re.findall(r'\b\w+\b', text.lower())
    return len(words)

def count_emotion_words(text, emotion_set):
    """Count how many words from emotion_set appear in text"""
    words = re.findall(r'\b\w+\b', text.lower())
    return sum(1 for word in words if word in emotion_set)

def analyze_message(message, positive_words, negative_words):
    """
    Analyze single message.
    
    Returns dict with:
    - total_words: int
    - pos_count: int (raw count)
    - neg_count: int (raw count)
    - pos_pct: float (percentage of total words)
    - neg_pct: float (percentage of total words)
    """
    total_words = count_words(message)
    pos_count = count_emotion_words(message, positive_words)
    neg_count = count_emotion_words(message, negative_words)
    
    # Avoid division by zero
    pos_pct = (pos_count / total_words * 100) if total_words > 0 else 0
    neg_pct = (neg_count / total_words * 100) if total_words > 0 else 0
    
    return {
        'total_words': total_words,
        'pos_count': pos_count,
        'neg_count': neg_count,
        'pos_pct': pos_pct,
        'neg_pct': neg_pct
    }

# ============================================================================
# BIN ANALYSIS
# ============================================================================

def analyze_by_bins(messages, positive_words, negative_words, n_bins=10):
    """
    Divide messages into temporal bins and analyze each.
    
    Returns DataFrame with bin-level statistics.
    """
    bin_size = len(messages) // n_bins
    results = []
    
    for bin_idx in range(n_bins):
        start = bin_idx * bin_size
        end = start + bin_size if bin_idx < n_bins - 1 else len(messages)
        bin_messages = messages[start:end]
        
        # Analyze each message in bin
        bin_stats = [analyze_message(msg, positive_words, negative_words) 
                     for msg in bin_messages]
        
        # Aggregate bin statistics
        n_msgs = len(bin_messages)
        total_words = sum(s['total_words'] for s in bin_stats)
        total_pos = sum(s['pos_count'] for s in bin_stats)
        total_neg = sum(s['neg_count'] for s in bin_stats)
        
        # Calculate averages
        avg_msg_length = total_words / n_msgs if n_msgs > 0 else 0
        avg_pos_count = total_pos / n_msgs if n_msgs > 0 else 0
        avg_neg_count = total_neg / n_msgs if n_msgs > 0 else 0
        
        # Percentage of total words that are emotional
        pos_pct = (total_pos / total_words * 100) if total_words > 0 else 0
        neg_pct = (total_neg / total_words * 100) if total_words > 0 else 0
        
        results.append({
            'bin': bin_idx,
            'n_msgs': n_msgs,
            'avg_msg_length': avg_msg_length,
            'avg_pos_count': avg_pos_count,  # Raw count per message
            'avg_neg_count': avg_neg_count,  # Raw count per message
            'pos_pct': pos_pct,  # % of all words
            'neg_pct': neg_pct   # % of all words
        })
    
    return pd.DataFrame(results)

# ============================================================================
# VISUALIZATION
# ============================================================================

def create_confound_figure(df, output_path):
    """
    Create 4-panel figure showing the message length confound.
    
    Panel A: Raw emotion counts (naive analysis)
    Panel B: Average message length over time
    Panel C: Proportional emotion content (corrected)
    Panel D: [Reserved for identity/acceptance scores if you add them]
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('The Message Length Confound in Longitudinal Text Analysis', 
                 fontsize=16, fontweight='bold')
    
    # Panel A: Raw Counts (Misleading)
    ax1 = axes[0, 0]
    ax1.plot(df['bin'], df['avg_pos_count'], 'o-', color='green', 
             linewidth=2, markersize=8, label='Positive')
    ax1.plot(df['bin'], df['avg_neg_count'], 'o-', color='red', 
             linewidth=2, markersize=8, label='Negative')
    ax1.set_xlabel('Temporal Bin (0=Early, 9=Late)', fontsize=11)
    ax1.set_ylabel('Avg Emotion Words per Message', fontsize=11)
    ax1.set_title('A: Raw Emotion Word Counts\n(Naive Analysis - Appears to Increase)', 
                  fontsize=12, fontweight='bold')
    ax1.legend(frameon=True, loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Panel B: Message Length (The Confound)
    ax2 = axes[0, 1]
    ax2.plot(df['bin'], df['avg_msg_length'], 'o-', color='purple', 
             linewidth=2, markersize=8)
    ax2.set_xlabel('Temporal Bin (0=Early, 9=Late)', fontsize=11)
    ax2.set_ylabel('Average Message Length (words)', fontsize=11)
    ax2.set_title('B: Message Length Over Time\n(The Confound Revealed)', 
                  fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Panel C: Proportional Content (Corrected)
    ax3 = axes[1, 0]
    ax3.plot(df['bin'], df['pos_pct'], 'o-', color='green', 
             linewidth=2, markersize=8, label='Positive %')
    ax3.plot(df['bin'], df['neg_pct'], 'o-', color='red', 
             linewidth=2, markersize=8, label='Negative %')
    ax3.set_xlabel('Temporal Bin (0=Early, 9=Late)', fontsize=11)
    ax3.set_ylabel('% of Total Words', fontsize=11)
    ax3.set_title('C: Proportional Emotional Content\n(Corrected - Remains Stable)', 
                  fontsize=12, fontweight='bold')
    ax3.legend(frameon=True, loc='best')
    ax3.grid(True, alpha=0.3)
    
    # Panel D: Reserved for construct-specific measures
    ax4 = axes[1, 1]
    ax4.text(0.5, 0.5, 
             'Panel D Reserved:\n\n'
             'Add identity score trajectory\n'
             'or acceptance language %\n\n'
             '(construct-specific measures\n'
             'that DID detect change)',
             ha='center', va='center', fontsize=11,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    ax4.set_title('D: Construct-Specific Measures\n(Detected Real Change)', 
                  fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved: {output_path}")
    plt.close()

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("="*80)
    print("NRC EMOTION ANALYSIS WITH MESSAGE LENGTH CORRECTION")
    print("="*80)
    
    # Load data
    print("\n1. Loading NRC lexicon...")
    positive_words, negative_words = load_nrc_lexicon(NRC_LEXICON_PATH)
    
    print("\n2. Loading messages...")
    messages = load_messages(TRANSCRIPT_PATH)
    
    print("\n3. Analyzing by temporal bins...")
    df = analyze_by_bins(messages, positive_words, negative_words, N_BINS)
    
    # Save results
    print("\n4. Saving results...")
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Results saved: {OUTPUT_CSV}")
    
    # Display summary
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    print(df.to_string(index=False))
    
    # Key findings
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)
    
    msg_length_change = ((df['avg_msg_length'].iloc[-1] - df['avg_msg_length'].iloc[0]) 
                         / df['avg_msg_length'].iloc[0] * 100)
    raw_pos_change = ((df['avg_pos_count'].iloc[-1] - df['avg_pos_count'].iloc[0]) 
                      / df['avg_pos_count'].iloc[0] * 100) if df['avg_pos_count'].iloc[0] > 0 else 0
    pct_pos_change = df['pos_pct'].iloc[-1] - df['pos_pct'].iloc[0]
    
    print(f"Message length change: {msg_length_change:+.1f}%")
    print(f"Raw positive count change: {raw_pos_change:+.1f}%")
    print(f"Proportional positive content change: {pct_pos_change:+.2f} percentage points")
    
    if msg_length_change > 20 and abs(pct_pos_change) < 0.5:
        print("\n⚠️  CONFOUND DETECTED:")
        print("   Messages got longer, but proportional emotional content remained stable.")
        print("   Raw counts are MISLEADING - use proportional measures instead.")
    
    # Create visualization
    print("\n5. Creating visualization...")
    create_confound_figure(df, OUTPUT_FIGURE)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nOutputs:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {OUTPUT_FIGURE}")

if __name__ == "__main__":
    main()