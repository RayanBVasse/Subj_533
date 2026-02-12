# Blind Spots in AI-Based Longitudinal Psychological Inference

Methodological Insights from Deterministic, Supervised, and LLM-Based Approaches
This repository contains method-validation scripts for a longitudinal psychological text analysis study based on the personal conversational log of an anonymized subject ("Subject 533").

The study is associated with a submitted manuscript exploring retrospective emotional and psychological trajectory using a 3‑phase pipeline:

🔍 Phases of Analysis

Phase A: Deterministic Lexicon-Based (NRC Emotion Lexicon)
Applies word-level emotion tagging (e.g. sadness, anger, joy)
Outputs: Subj533_nrc_scores.csv + volatility plot

Phase B: Supervised Model-Based (GoEmotions)
Uses fine-tuned BERT classifier to infer probabilistic emotions
Outputs: phaseB_goemotions_scores.csv + sentiment trajectory plot

Phase C: Prompted LLM-Based Inference (Experimental)
Uses GPT-style inference with schema-constrained prompting
Status: now functional, coverage-verified JSONL logs included

Outputs: Subj533_phaseC_LLM_scores.csv, phaseC_row_log.jsonl, phaseC_execution_log.json

Getting Started:
git clone https://github.com/RayanBVasse/Subj_533.git
cd Subj_533

Dependencies:
pip install -r requirements.txt

