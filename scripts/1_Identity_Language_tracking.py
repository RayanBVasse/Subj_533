""" 
Identity Language Analysis for Subject 533 ChatGPT Transcript 
Calculates Identity Score across temporal phases 
Author: Rayan B. Vasse (pseudonym) 
Date: December 2024 
""" 
 
import re 
from collections import defaultdict 
import statistics 
from pathlib import Path
 
# ============================================================================ 
# CONFIGURATION 
# ============================================================================ 
 
# File path (update to your transcript location)
BASE_DIR = Path(__file__).resolve().parents[1]

TRANSCRIPT_PATH = Path(__file__).resolve().parent / "Combined_Subject_533_threads.txt" 
 
# Lexicons 
DEFICIT_WORDS = [ 
    'broken', 'failed', 'failure', 'outlier', 'alone', 'lonely',  
    'isolated', 'misfit', 'outcast', 'unwanted', 'rejected',  
    'worthless', 'deficient', 'inadequate', 'lacking', 'missing out',  
    'left behind', 'invisible', 'unseen', 'unheard', 'forgotten',  
    'abandoned', 'lost', 'damaged', 'wrong' 
] 
 
ASSET_WORDS = [ 
    'independent', 'skilled', 'multifaceted', 'elevated', 'capable',  
    'strong', 'resilient', 'intelligent', 'creative', 'resourceful',  
    'accomplished', 'competent', 'talented', 'valuable', 'worthy',  
    'significant', 'meaningful', 'productive', 'effective', 'successful',  
    'thriving', 'growing', 'developing', 'mature', 'wise' 
] 
 
# ============================================================================ 
# DATA LOADING 
# ============================================================================ 
 
def load_transcript(filepath): 
    """Load transcript and extract user messages only""" 
    with open(filepath, 'r', encoding='utf-8') as f: 
        content = f.read() 
     
    # Extract user messages using regex 
    # Assumes format: [user]: message text [ChatGPT]: response 
    user_pattern = r'\[user\]: (.*?)(?=\[ChatGPT\]:|$)' 
    user_messages = re.findall(user_pattern, content, re.DOTALL) 
     
    return user_messages 
 
# ============================================================================ 
# ANALYSIS FUNCTIONS 
# ============================================================================ 
 
def count_identity_words(messages, word_list): 
    """ 
    Count how many messages contain at least one word from word_list 
     
    Parameters: 
    ----------- 
    messages : list of str 
        List of message texts to analyze 
    word_list : list of str 
        List of words to search for 
         
    Returns: 
    -------- 
    int : Number of messages containing ≥1 word from list 
    """ 
    count = 0 
    for msg in messages: 
        msg_lower = msg.lower() 
        # Check if ANY word from list appears in message 
        if any(word in msg_lower for word in word_list): 
            count += 1 
    return count 
 
def calculate_identity_score(deficit_count, asset_count): 
    """ 
    Calculate identity score: (asset - deficit) / (asset + deficit) 
     
    Returns: 
    -------- 
    float : Score from -1.0 to +1.0 
            -1.0 = purely deficit language 
             0.0 = balanced 
            +1.0 = purely asset language 
    """ 
    total = deficit_count + asset_count 
    if total == 0: 
        return 0.0  # No identity language detected 
    return (asset_count - deficit_count) / total 
 
# ============================================================================ 
# MAIN ANALYSIS 
# ============================================================================ 
 
def main(): 
    print("="*80) 
    print("IDENTITY LANGUAGE ANALYSIS") 
    print("="*80) 
     
    # Load data 
    print("\nLoading transcript...") 
    messages = load_transcript(TRANSCRIPT_PATH) 
    print(f"Total user messages: {len(messages)}") 
     
    # Divide into 4 temporal phases 
    phase_size = len(messages) // 4 
    phases = { 
        'Phase 1 (Early)': messages[0:phase_size], 
        'Phase 2 (Active)': messages[phase_size:phase_size*2], 
        'Phase 3 (Integration)': messages[phase_size*2:phase_size*3], 
        'Phase 4 (Recent)': messages[phase_size*3:], 
    } 
     
    print(f"\nPhase breakdown:") 
    for phase_name, msgs in phases.items(): 
        print(f"  {phase_name}: {len(msgs)} messages") 
     
    # Analyze each phase 
    print("\n" + "="*80) 
    print("RESULTS BY PHASE") 
    print("="*80) 
    print(f"\n{'Phase':<20} {'Deficit':<12} {'Asset':<12} {'Score':<10} {'Change':<15}") 
    print("-"*80) 
     
    baseline_score = None 
     
    for phase_name, msgs in phases.items(): 
        deficit_count = count_identity_words(msgs, DEFICIT_WORDS) 
        asset_count = count_identity_words(msgs, ASSET_WORDS) 
        identity_score = calculate_identity_score(deficit_count, asset_count) 
         
        # Calculate percentage of messages containing identity language 
        deficit_pct = (deficit_count / len(msgs)) * 100 
        asset_pct = (asset_count / len(msgs)) * 100 
         
        # Track change from baseline 
        if baseline_score is None: 
            baseline_score = identity_score 
            change = "Baseline" 
        else: 
            if baseline_score != 0: 
                change_pct = ((identity_score - baseline_score) / abs(baseline_score)) * 100 
                change = f"+{change_pct:.0f}%" if change_pct > 0 else f"{change_pct:.0f}%" 
            else: 
                change = "N/A" 
         
        print(f"{phase_name:<20} " 
              f"{deficit_count:3d} ({deficit_pct:4.1f}%)  " 
              f"{asset_count:3d} ({asset_pct:4.1f}%)  " 
              f"{identity_score:+.3f}     " 
              f"{change:<15}") 
     
    print("\n" + "="*80) 
    print("INTERPRETATION") 
    print("="*80) 
    print("\nIdentity Score Meaning:") 
    print("  -1.00 = Purely deficit-based self-concept (ego-dystonic)") 
    print("   0.00 = Balanced self-concept") 
    print("  +1.00 = Purely asset-based self-concept (ego-syntonic)") 
    print("\nNote: Final score near 0 with high frequencies of BOTH deficit") 
    print("and asset language indicates realistic, integrated self-concept,") 
    print("not lack of ego-syntonic shift.") 
 
if __name__ == "__main__": 
    main()
         