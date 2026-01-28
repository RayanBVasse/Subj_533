""" 
Simple Sentiment Analysis 
Calculates positive-negative polarity per message and phase 
""" 
 
import re 
import statistics 
 
# ============================================================================ 
# CONFIGURATION 
# ============================================================================ 
 
TRANSCRIPT_PATH = 'Combined_Subject_533_threads.txt' 
 
POSITIVE_WORDS = [ 
    'good', 'great', 'excellent', 'wonderful', 'amazing', 'happy', 'joy',  
    'love', 'peace', 'content', 'clear', 'clarity', 'better', 'improved',  
    'progress', 'successful', 'thriving', 'delighted', 'pleased', 'enjoy', 
    'positive', 'growth', 'breakthrough', 'pleasant', 'nice' 
] 
 
NEGATIVE_WORDS = [ 
    'bad', 'terrible', 'awful', 'horrible', 'sad', 'pain', 'hurt',  
    'difficult', 'struggle', 'problem', 'worse', 'failing', 'disappointed', 
    'frustrated', 'depressed', 'suffering', 'issue', 'obstacle', 'decline', 
    'setback', 'painful', 'miserable', 'unfortunate', 'hard' 
] 
 
# ============================================================================ 
# ANALYSIS FUNCTIONS 
# ============================================================================ 
 
def calculate_message_sentiment(message): 
    """ 
    Calculate sentiment for single message 
     
    Returns: 
    -------- 
    float : Sentiment score from -1.0 to +1.0 
            -1.0 = purely negative 
             0.0 = neutral or balanced 
            +1.0 = purely positive 
    """ 
    msg_lower = message.lower() 
     
    # Count positive and negative words 
    pos_count = sum(1 for word in POSITIVE_WORDS if word in msg_lower) 
    neg_count = sum(1 for word in NEGATIVE_WORDS if word in msg_lower) 
     
    total = pos_count + neg_count 
    if total == 0: 
        return 0.0  # Neutral (no emotional words detected) 
     
    return (pos_count - neg_count) / total 
 
def categorize_message(sentiment_score, threshold=0.1): 
    """ 
    Categorize message as positive, negative, or neutral/mixed 
     
    Parameters: 
    ----------- 
    sentiment_score : float 
        Sentiment score from calculate_message_sentiment() 
    threshold : float 
        Absolute value below which considered neutral (default 0.1) 
         
    Returns: 
    -------- 
    str : 'positive', 'negative', or 'neutral' 
    """ 
    if sentiment_score > threshold: 
        return 'positive' 
    elif sentiment_score < -threshold: 
        return 'negative' 
    else: 
        return 'neutral' 
 
# ============================================================================ 
# MAIN ANALYSIS 
# ============================================================================ 
 
def main(): 
    print("="*80) 
    print("SENTIMENT ANALYSIS") 
    print("="*80) 
     
    # Load transcript 
    with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f: 
        content = f.read() 
    user_pattern = r'\[user\]: (.*?)(?=\[ChatGPT\]:|$)' 
    messages = re.findall(user_pattern, content, re.DOTALL) 
     
    print(f"\nTotal messages: {len(messages)}") 
     
    # Divide into phases 
    phase_size = len(messages) // 4 
    phases = { 
        'Phase 1 (Early)': messages[0:phase_size], 
        'Phase 2 (Active)': messages[phase_size:phase_size*2], 
        'Phase 3 (Integration)': messages[phase_size*2:phase_size*3], 
        'Phase 4 (Recent)': messages[phase_size*3:], 
    } 
     
    # Analyze each phase 
    print("\n" + "="*80) 
    print("SENTIMENT SCORES BY PHASE") 
    print("="*80) 
    print(f"\n{'Phase':<20} {'Avg Sentiment':<15} {'Pos Msgs':<15} {'Neg Msgs':<15} {'Neutral':<15}") 
    print("-"*90) 
     
    trajectory = [] 
     
    for phase_name, msgs in phases.items(): 
        # Calculate sentiment for each message 
        scores = [calculate_message_sentiment(msg) for msg in msgs] 
         
        # Calculate phase average 
        avg_sentiment = statistics.mean(scores) 
        trajectory.append(avg_sentiment) 
         
        # Categorize messages 
        categories = [categorize_message(s) for s in scores] 
        pos_count = categories.count('positive') 
        neg_count = categories.count('negative') 
        neu_count = categories.count('neutral') 
         
        # Calculate percentages 
        pos_pct = (pos_count / len(msgs)) * 100 
        neg_pct = (neg_count / len(msgs)) * 100 
        neu_pct = (neu_count / len(msgs)) * 100 
         
        print(f"{phase_name:<20} " 
              f"{avg_sentiment:+.3f}           " 
              f"{pos_count:3d} ({pos_pct:4.1f}%)    " 
              f"{neg_count:3d} ({neg_pct:4.1f}%)    " 
              f"{neu_count:3d} ({neu_pct:4.1f}%)") 
     
    # Trajectory analysis 
    print("\n" + "="*80) 
    print("TRAJECTORY ANALYSIS") 
    print("="*80) 
     
    print(f"\nSentiment progression: {trajectory[0]:+.3f} → {trajectory[-1]:+.3f}") 
     
    change = trajectory[-1] - trajectory[0] 
    if trajectory[0] != 0: 
        change_pct = (change / abs(trajectory[0])) * 100 
        print(f"Change: {change:+.3f} ({change_pct:+.1f}%)") 
     
    print("\nInterpretation:") 
    if change < 0: 
        print("  Note: Sentiment DECREASE is not necessarily treatment failure.") 
        print("  May indicate increased emotional honesty (processing painful content)") 
        print("  rather than defensive positivity. Check acceptance language and") 
        print("  qualitative themes for complete picture.") 
    else: 
        print("  Sentiment increased, suggesting improved emotional state.") 
 
if __name__ == "__main__": 
    main() 
