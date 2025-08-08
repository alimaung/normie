import os
import json
import extract_msg
import re
from typing import List, Dict, Tuple
import time

# ========== ATS SCORER ==========
class ATSEmailScorer:
    def __init__(self):
        self.high_keywords = [
            'antrag', 'ats', 'afts', 'aft&s', 'aftus', 
            'antrag teile und stoffe', 'antrag für teile und stoffe',
            'teile und stoffe', 'application materials'
        ]
        self.medium_keywords = [
            'freigabe', 'approval', 'genehmigung', 'zulassung',
            'material', 'substance', 'chemical', 'produkt'
        ]
        self.ats_patterns = [r'.*ats.*', r'.*afts.*', r'.*aft&s.*', r'.*antrag.*',
                             r'.*teile.*stoffe.*', r'.*application.*']
        self.sds_patterns = [r'.*sdb.*', r'.*msds.*', r'.*sds.*', r'.*safety.*data.*sheet.*']
        self.tds_patterns = [r'.*pdb.*', r'.*tdb.*', r'.*tds.*', r'.*pds.*',
                             r'.*technical.*data.*sheet.*', r'.*product.*data.*sheet.*']
        self.ignore_senders = ['irm-standartization-office@rolls-royce.com']
        self.ignore_subjects = ['qctp', 'pbr', 'din', 'rqsc', 'ballot', 'la', 'edns']

    def score_email(self, subject: str, sender: str, attachments: List[str]) -> Dict:
        subj_l = subject.lower()
        sender_l = sender.lower()
        attachments_l = [a.lower() for a in attachments]
        scores = {
            "subject_score": 0.0,
            "body_score": 0.0,  # We don't have body in .msg-only parsing
            "attachment_score": 0.0,
            "sender_penalty": 0.0,
            "ignore_penalty": 0.0
        }
        reasoning = []

        # Ignore rules
        if any(ignore in sender_l for ignore in self.ignore_senders) or \
           any(ignore in subj_l for ignore in self.ignore_subjects):
            scores["ignore_penalty"] = -100.0
            reasoning.append("Email ignored due to sender or subject.")
            return self._format_result(scores, reasoning, subject, sender)

        # Subject scoring
        for kw in self.high_keywords:
            if kw in subj_l:
                scores["subject_score"] += 10.0
        for kw in self.medium_keywords:
            if kw in subj_l:
                scores["subject_score"] += 3.0
        if scores["subject_score"]:
            reasoning.append(f"Subject contains ATS-related keywords (score: {scores['subject_score']})")

        # Attachment scoring
        ats, sds, tds = False, False, False
        for fname in attachments_l:
            if any(re.match(pat, fname) for pat in self.ats_patterns):
                scores["attachment_score"] += 15.0
                ats = True
            elif any(re.match(pat, fname) for pat in self.sds_patterns):
                scores["attachment_score"] += 8.0
                sds = True
            elif any(re.match(pat, fname) for pat in self.tds_patterns):
                scores["attachment_score"] += 5.0
                tds = True
        if attachments:
            scores["attachment_score"] += 2.0  # Base bonus for having attachments
        if ats and (sds or tds):
            scores["attachment_score"] += 10.0  # Bonus
        if scores["attachment_score"]:
            reasoning.append(f"Attachments suggest ATS content (score: {scores['attachment_score']})")

        return self._format_result(scores, reasoning, subject, sender)

    def _format_result(self, scores: Dict, reasoning: List[str], subject: str, sender: str) -> Dict:
        total = sum(scores.values())
        if scores["ignore_penalty"] < 0:
            prob, is_ats = "NONE", False
        elif total >= 20.0:
            prob, is_ats = "HIGH", True
        elif total >= 10.0:
            prob, is_ats = "MEDIUM", False
        elif total >= 3.0:
            prob, is_ats = "LOW", False
        else:
            prob, is_ats = "NONE", False

        return {
            "total_score": total,
            "probability": prob,
            "is_ats_application": is_ats,
            "reasoning": reasoning if reasoning else ["No strong ATS indicators."],
            "details": scores
        }

# ========== MAIN PARSER ==========
def parse_and_score_emails(root_dir: str, output_json_path: str):
    scorer = ATSEmailScorer()
    results = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".msg"):
                msg_path = os.path.join(root, file)
                try:
                    msg = extract_msg.Message(msg_path)
                    subject = msg.subject or ""
                    sender = msg.sender or ""
                    attachments = [att.longFilename or att.shortFilename or f"attachment_{i+1}"
                                   for i, att in enumerate(msg.attachments)]
                    
                    score_data = scorer.score_email(subject, sender, attachments)
                    
                    results.append({
                        "subject": subject,
                        "sender": sender,
                        "attachments": attachments,
                        "path_to_folder": root,
                        "ats_score": score_data
                    })
                except Exception as e:
                    print(f"Error parsing {msg_path}: {e}")

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(results)} emails with ATS scoring to {output_json_path}")

    time.sleep(5)

# ========== RUN ==========
if __name__ == "__main__":
    ROOT_DIR = r"V:\normie stuff\mail\data"
    OUTPUT_JSON = "ats-scores.json"
    parse_and_score_emails(ROOT_DIR, OUTPUT_JSON)
