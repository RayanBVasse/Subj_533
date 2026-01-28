""" 
Emotional Word Frequency Analysis (LIWC-Style) 
Tracks 5 emotion categories across temporal phases 
""" 
 
import re 
from collections import defaultdict 
 
# ============================================================================ 
# CONFIGURATION 
# ============================================================================ 
 
TRANSCRIPT_PATH = 'Combined_Subject_533_threads.txt' 
 
# Emotion lexicons (LIWC-inspired) 
EMOTION_CATEGORIES = { 
    'Positive Emotion': [ 
        'happy', 'happiness', 'joy', 'joyful', 'pleased', 'delighted',  
        'excited', 'enthusiasm', 'love', 'loving', 'wonderful', 'excellent',  
        'great', 'good', 'nice', 'pleasant', 'enjoy', 'enjoyed', 'fun',  
        'laugh', 'smile' 
    ], 
    'Negative Emotion': [ 
        'sad', 'sadness', 'unhappy', 'miserable', 'depressed', 'depression',  
        'hurt', 'pain', 'painful', 'suffering', 'ache', 'terrible', 'awful',  
        'horrible', 'bad', 'worse', 'worst', 'unfortunate' 
    ], 
    'Anxiety': [ 
        'worried', 'worry', 'anxious', 'anxiety', 'nervous', 'tense',  
        'stressed', 'stress', 'fear', 'fearful', 'scared', 'afraid',  
        'panic', 'dread' 
    ], 
    'Anger': [ 
        'angry', 'anger', 'mad', 'furious', 'rage', 'annoyed', 'irritated',  
        'frustrated', 'frustration', 'hate', 'hatred', 'resent',  
        'resentment', 'bitter' 
    ], 
    'Acceptance': [ 
        'accept', 'accepted', 'accepting', 'acceptance', 'peace', 'peaceful',  
        'content', 'contentment', 'okay', 'fine', 'comfortable', 'settled',  
        'calm', 'tranquil', 'serene' 
    ] 
} 
 
# ============================================================================ 
# ANALYSIS FUNCTIONS 
# ============================================================================ 
 
def count_emotion_words(messages, word_list): 
    """Count messages containing any word from emotion category""" 
    count = 0 
    for msg in messages: 
        msg_lower = msg.lower() 
        if any(word in msg_lower for word in word_list): 
            count += 1 
    return count 
 
def analyze_emotions(messages, phase_name): 
    """Analyze all emotion categories for a message set""" 
    results = {} 
    total_msgs = len(messages) 
     
    print(f"\n{phase_name}:") 
    print("-" * 70) 
     
    for category, words in EMOTION_CATEGORIES.items(): 
        count = count_emotion_words(messages, words) 
        percentage = (count / total_msgs) * 100 
        results[category] = (count, percentage) 
        print(f"  {category:<20} {count:3d} messages ({percentage:4.1f}%)") 
     
    return results 
 
# ============================================================================ 
# MAIN ANALYSIS 
# ============================================================================ 
 
def main(): 
    print("="*80) 
    print("EMOTIONAL WORD FREQUENCY ANALYSIS (LIWC-STYLE)") 
    print("="*80) 
     
    # Load transcript (same function as Script 1) 
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
    all_results = {} 
    for phase_name, msgs in phases.items(): 
        all_results[phase_name] = analyze_emotions(msgs, phase_name) 
     
    # Summary comparison 
    print("\n" + "="*80) 
    print("KEY FINDINGS") 
    print("="*80) 
     
    # Track acceptance growth 
    phase_names = list(phases.keys()) 
    acceptance_start = all_results[phase_names[0]]['Acceptance'][1] 
    acceptance_end = all_results[phase_names[-1]]['Acceptance'][1] 
    acceptance_growth = ((acceptance_end - acceptance_start) / acceptance_start) * 100 
     
    print(f"\nAcceptance language growth: {acceptance_start:.1f}% → {acceptance_end:.1f}% " 
          f"({acceptance_growth:+.0f}% change)") 
     
    # Check if acceptance exceeds negative emotion in final phase 
    final_acceptance = all_results[phase_names[-1]]['Acceptance'][0] 
    final_negative = all_results[phase_names[-1]]['Negative Emotion'][0] 
     
    print(f"\nFinal phase (Phase 4):") 
    print(f"  Acceptance messages: {final_acceptance}") 
    print(f"  Negative emotion messages: {final_negative}") 
     
    if final_acceptance > final_negative: 
        print("  ✓ Acceptance EXCEEDS negative emotion (therapeutic success indicator)") 
    else: 
        print("  ✗ Negative emotion exceeds acceptance") 
 
if __name__ == "__main__": 
    main()