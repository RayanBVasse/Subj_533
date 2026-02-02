from pathlib import Path
import re

FILE_PATH = "Thread_34_Daily_Banter_with_Henry.txt"

text = Path(FILE_PATH).read_text(encoding="utf-8", errors="ignore")

count_user = len(re.findall(r"\buser\b", text, flags=re.IGNORECASE))
count_chatgpt = len(re.findall(r"\bchatgpt\b", text, flags=re.IGNORECASE))

print(f"Occurrences of 'user': {count_user}")
print(f"Occurrences of 'chatGPT': {count_chatgpt}")
