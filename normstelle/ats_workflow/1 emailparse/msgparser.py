import sys
import os
import re
import shutil
import extract_msg

OUTPUT_DIR = "output"
ATTACH_DIR = os.path.join(OUTPUT_DIR, "attachments")

def split_messages_and_attachments(file_path):
    # Prepare output folders
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(ATTACH_DIR, exist_ok=True)

    msg = extract_msg.Message(file_path)

    # Extract HTML body
    html_body = msg.htmlBody
    if isinstance(html_body, bytes):
        html_body = html_body.decode("utf-8", errors="replace")

    # Split HTML into parts
    parts = re.split(r'(?=<div style="border:none;border-top:)', html_body)
    for i, part in enumerate(parts, 1):
        out_file = os.path.join(OUTPUT_DIR, f"message_part_{i}.html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(part)
        print(f"Saved HTML part {i}: {out_file}")

    # Save attachments (if any)
    if msg.attachments:
        print(f"\nFound {len(msg.attachments)} attachment(s):")
        for i, att in enumerate(msg.attachments, 1):
            filename = att.longFilename or att.shortFilename or f"attachment_{i}"
            att.save(customPath=ATTACH_DIR)  # save to folder, not full file path
            print(f" - Saved: {os.path.join(ATTACH_DIR, filename)}")
    else:
        print("\nNo attachments found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_and_split_msg.py <path_to_msg_file>")
    else:
        split_messages_and_attachments(sys.argv[1])
