import os
import json
import extract_msg

ROOT_FOLDER = r"D:\mail\data"
OUTPUT_JSON = "parsed_messages2.json"

results = []

for root, _, files in os.walk(ROOT_FOLDER):
    for file in files:
        if file.lower().endswith(".msg"):
            msg_path = os.path.join(root, file)
            try:
                msg = extract_msg.Message(msg_path)
                msg_sender = msg.sender or ""
                msg_subject = msg.subject or ""
                attachments = [
                    att.longFilename or att.shortFilename or f"attachment_{i+1}"
                    for i, att in enumerate(msg.attachments)
                ]
                results.append({
                    "subject": msg_subject,
                    "sender": msg_sender,
                    "attachments": attachments,
                    "path_to_folder": root
                })
            except Exception as e:
                print(f"Failed to process {msg_path}: {e}")

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Saved {len(results)} entries to {OUTPUT_JSON}")
