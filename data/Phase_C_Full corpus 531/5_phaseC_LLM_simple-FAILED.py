import csv
import json
from openai import OpenAI

MODEL_NAME = "gpt-4.1-mini"
INPUT_FILE = "Subj533_msgs_only.csv"
OUTPUT_FILE = "Subj533_phaseC_llm_scores.csv"

client = OpenAI()

PROMPT_TEMPLATE = """You are performing a structured emotional labeling task.

Given the text below, return a JSON object with exactly two fields:
- "positive_affect": a float between 0 and 1
- "negative_affect": a float between 0 and 1

Definitions:
- positive_affect reflects expressions of joy, calm, trust, hope, or satisfaction.
- negative_affect reflects expressions of sadness, anxiety, anger, fear, or distress.

Text:
\"\"\"{text}\"\"\"

Return JSON only. Do not include explanations, commentary, or additional fields.
"""

rows = []
with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

results = []

for row in rows:
    prompt = PROMPT_TEMPLATE.format(text=row["text"])

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content
        
        data = json.loads(content)

        
        results.append({
            "entry_index": row["entry_index"],
            "positive_affect_llm": float(data["positive_affect"]),
            "negative_affect_llm": float(data["negative_affect"])
        })

    except Exception as e:
        raise RuntimeError(f"Phase C failed at entry {row['entry_index']}: {e}")

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["entry_index", "positive_affect_llm", "negative_affect_llm"]
    )
    writer.writeheader()
    writer.writerows(results)

print(f"Phase C complete: {len(results)} rows")
