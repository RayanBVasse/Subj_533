from pathlib import Path
import re

FILE_PATH = "Combined Subject 533 threads.txt"

text = Path(FILE_PATH).read_text(encoding="utf-8", errors="ignore")

count_user = len(re.findall(r"\buser\b", text, flags=re.IGNORECASE))
count_chatgpt = len(re.findall(r"\bchatgpt\b", text, flags=re.IGNORECASE))

print(f"Occurrences of 'user': {count_user}")
print(f"Occurrences of 'chatGPT': {count_chatgpt}")
