import csv
import json
import time
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI

# =========================
# CONFIG
# =========================

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "Subj533_msgs_only.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "Subj533_phaseC_LLM_scores.csv"
EXEC_LOG = OUTPUT_DIR / "phaseC_execution_log.json"
ROW_LOG = OUTPUT_DIR / "phaseC_row_log.jsonl"

EXPECTED_ROWS = 531
MODEL_NAME = "gpt-4.1-mini"
TEMPERATURE = 0
MAX_RETRIES = 3
RETRY_SLEEP_SECONDS = 2

PROMPT_TEMPLATE = (
    "You are performing a structured emotional labeling task.\n\n"
    "Given the text below, return a JSON object with exactly two fields:\n"
    '- "positive_affect": a float between 0 and 1\n'
    '- "negative_affect": a float between 0 and 1\n\n'
    "Definitions:\n"
    "- positive_affect reflects expressions of joy, calm, trust, hope, or satisfaction.\n"
    "- negative_affect reflects expressions of sadness, anxiety, anger, fear, or distress.\n\n"
    "Text:\n"
    "{text}\n\n"
    "Return JSON only. Do not include explanations, commentary, or additional fields."
)


@dataclass
class AffectResult:
    positive_affect: Optional[float]
    negative_affect: Optional[float]
    status: str
    error: Optional[str]


client = OpenAI()


def file_sha256(path: Path) -> str:
    hasher = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_json_payload(text: str) -> Dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in response")
    payload = text[start : end + 1]
    return json.loads(payload)


def parse_affect(payload: Dict[str, Any]) -> Dict[str, float]:
    if "positive_affect" not in payload or "negative_affect" not in payload:
        raise ValueError("Missing required keys in response")
    positive = float(payload["positive_affect"])
    negative = float(payload["negative_affect"])
    for value, name in ((positive, "positive_affect"), (negative, "negative_affect")):
        if not 0 <= value <= 1:
            raise ValueError(f"{name} out of range: {value}")
    return {"positive_affect": positive, "negative_affect": negative}


def score_row(text: str, row_log_handle) -> AffectResult:
    prompt = PROMPT_TEMPLATE.format(text=text)
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            message = response.choices[0].message
            content = message.content or ""
            payload = extract_json_payload(content)
            scores = parse_affect(payload)
            row_log_handle.write(
                json.dumps(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "attempt": attempt,
                        "status": "success",
                        "payload": payload,
                    }
                )
                + "\n"
            )
            return AffectResult(
                positive_affect=scores["positive_affect"],
                negative_affect=scores["negative_affect"],
                status="success",
                error=None,
            )
        except Exception as exc:
            last_error = str(exc)
            row_log_handle.write(
                json.dumps(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "attempt": attempt,
                        "status": "failure",
                        "error": last_error,
                    }
                )
                + "\n"
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_SLEEP_SECONDS * attempt)
    return AffectResult(
        positive_affect=None,
        negative_affect=None,
        status="failed",
        error=last_error,
    )


# =========================
# LOAD INPUT
# =========================

rows = []
with INPUT_FILE.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)


# =========================
# LLM INFERENCE
# =========================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

results = []
failures = 0

with ROW_LOG.open("w", encoding="utf-8") as row_log_handle:
    for row in rows:
        result = score_row(row["text"], row_log_handle)
        if result.status != "success":
            failures += 1
        results.append(
            {
                "entry_index": row["entry_index"],
                "positive_affect_llm": result.positive_affect,
                "negative_affect_llm": result.negative_affect,
                "model": MODEL_NAME,
                "status": result.status,
                "error": result.error,
            }
        )


# =========================
# WRITE OUTPUT
# =========================

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "entry_index",
            "positive_affect_llm",
            "negative_affect_llm",
            "model",
            "status",
            "error",
        ],
    )
    writer.writeheader()
    for r in results:
        writer.writerow(r)

# =========================
# EXECUTION LOG
# =========================

rows_processed = len(results)
coverage = (rows_processed - failures) / rows_processed * 100 if rows_processed else 0

execution_log = {
    "timestamp": datetime.utcnow().isoformat(),
    "input_file": str(INPUT_FILE),
    "input_sha256": file_sha256(INPUT_FILE),
    "expected_rows": EXPECTED_ROWS,
    "rows_in_file": len(rows),
    "rows_processed": rows_processed,
    "successes": rows_processed - failures,
    "failures": failures,
    "coverage_percent": round(coverage, 2),
    "output_file": str(OUTPUT_FILE),
    "row_log": str(ROW_LOG),
    "model": MODEL_NAME,
    "temperature": TEMPERATURE,
    "max_retries": MAX_RETRIES,
    "retry_sleep_seconds": RETRY_SLEEP_SECONDS,
    "prompt_template": PROMPT_TEMPLATE,
}

with EXEC_LOG.open("w", encoding="utf-8") as f:
    json.dump(execution_log, f, indent=2)

print("SUCCESS")
print(f"Rows processed: {rows_processed}")
print(f"Coverage: {execution_log['coverage_percent']}%")
print(f"Output written: {OUTPUT_FILE}")
print(f"Execution log written: {EXEC_LOG}")
