import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# =========================
# CONFIG
# =========================

INPUT_FILE = "Subj533_msgs_only.csv"
OUTPUT_FILE = "Subj533_phaseC_LLM_scores.csv"
EXEC_LOG = "phaseC_execution_log.txt"

EXPECTED_ROWS = 531
MODEL_NAME = "gpt-4.1-mini"
TEMPERATURE = 0

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

client = OpenAI()

# =========================
# LOAD INPUT
# =========================

rows = []
with open(INPUT_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

if len(rows) != EXPECTED_ROWS:
    print(f"ERROR: Expected {EXPECTED_ROWS} rows, found {len(rows)}")
    sys.exit(1)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "emit_affect_scores",
            "description": "Return affect scores for a message",
            "parameters": {
                "type": "object",
                "properties": {
                    "positive_affect": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "negative_affect": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                    }
                },
                "required": ["positive_affect", "negative_affect"],
                "additionalProperties": False
            }
        }
    }
]

# =========================
# LLM INFERENCE
# =========================

results = []
failures = 0

MAX_RETRIES = 3

for i, row in enumerate(rows, start=1):
    prompt = PROMPT_TEMPLATE.format(text=row["text"])

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=TEMPERATURE,
                input=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    tools=TOOLS,
                    tool_choice={
                        "type": "function",
                        "function": {"name": "emit_affect_scores"}
                    }
                )

            tool_call = response.choices[0].message.tool_calls[0]
            args = tool_call.function.arguments

            results.append({
                "entry_index": row["entry_index"],
                "positive_affect_llm": float(args["positive_affect"]),
                "negative_affect_llm": float(args["negative_affect"]),
                "model": MODEL_NAME
            })

        except Exception as e:
            raise RuntimeError(
                f"Phase C failed at entry {row['entry_index']}: {e}"
            )
        


# =========================
# HARD CHECK
# =========================

if len(results) != EXPECTED_ROWS:
    print("ERROR: Row count mismatch after LLM inference")
    sys.exit(1)

# =========================
# WRITE OUTPUT
# =========================

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "entry_index",
            "positive_affect_llm",
            "negative_affect_llm",
            "model"
        ]
    )
    writer.writeheader()
    for r in results:
        writer.writerow(r)

# =========================
# EXECUTION LOG
# =========================

with open(EXEC_LOG, "w", encoding="utf-8") as f:
    f.write("=== PHASE C LLM EXECUTION LOG ===\n")
    f.write(f"Timestamp: {datetime.now()}\n")
    f.write(f"Input file: {INPUT_FILE}\n")
    f.write(f"Expected rows: {EXPECTED_ROWS}\n")
    f.write(f"Rows processed: {len(results)}\n")
    f.write(f"Failures: {failures}\n")
    f.write(f"Model: {MODEL_NAME}\n")
    f.write(f"Temperature: {TEMPERATURE}\n")
    f.write("Prompt: FIXED\n")
    f.write("Status: COMPLETE\n")

print("SUCCESS")
print(f"Rows processed: {len(results)}")
print(f"Output written: {OUTPUT_FILE}")
print(f"Execution log written: {EXEC_LOG}")
