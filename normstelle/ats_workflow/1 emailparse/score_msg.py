"""
Single .msg file ATS probability scorer.

This module provides functionality to parse a single Outlook .msg file
and score it for ATS (Application for Teile und Stoffe) probability.
"""

import os
import re
from typing import Dict, List, Optional
import extract_msg


class ATSEmailScorer:
    """Scores emails for ATS (Application for Teile und Stoffe) probability."""
    
    def __init__(self):
        # High probability keywords (case insensitive)
        self.high_keywords = [
            'antrag', 'ats', 'afts', 'aft&s', 'aftus', 
            'antrag teile und stoffe', 'antrag für teile und stoffe',
            'teile und stoffe', 'application materials'
        ]
        
        # Medium probability keywords
        self.medium_keywords = [
            'freigabe', 'approval', 'genehmigung', 'zulassung',
            'material', 'substance', 'chemical', 'produkt'
        ]
        
        # Attachment filename patterns for ATS forms
        self.ats_patterns = [
            r'.*ats.*', r'.*afts.*', r'.*aft&s.*', r'.*antrag.*',
            r'.*teile.*stoffe.*', r'.*application.*'
        ]
        
        # Safety Data Sheet patterns
        self.sds_patterns = [
            r'.*sdb.*', r'.*msds.*', r'.*sds.*', r'.*safety.*data.*sheet.*'
        ]
        
        # Technical/Product Data Sheet patterns
        self.tds_patterns = [
            r'.*pdb.*', r'.*tdb.*', r'.*tds.*', r'.*pds.*',
            r'.*technical.*data.*sheet.*', r'.*product.*data.*sheet.*'
        ]
        
        # Email addresses to ignore (our own emails)
        self.ignore_senders = [
            'irm-standartization-office@rolls-royce.com'
        ]
        
        # Subject patterns to ignore
        self.ignore_subjects = [
            'qctp', 'pbr', 'din', 'rqsc', 'ballot', 'la', 'edns'
        ]
    
    def score_email(self, subject: str, sender: str, attachments: List[str]) -> Dict:
        """
        Score an email for ATS probability.
        
        Args:
            subject: Email subject line
            sender: Email sender address
            attachments: List of attachment filenames
            
        Returns:
            Dictionary containing:
            - total_score: Total numerical score
            - probability: "HIGH", "MEDIUM", "LOW", or "NONE"
            - is_ats_application: Boolean indicating if this is likely an ATS application
            - reasoning: List of strings explaining the score
            - details: Dictionary with score breakdown
        """
        subj_l = subject.lower()
        sender_l = sender.lower()
        attachments_l = [a.lower() for a in attachments]
        
        scores = {
            "subject_score": 0.0,
            "body_score": 0.0,  # Not available from .msg-only parsing
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
            reasoning.append(f"Subject contains ATS-related keywords (score: {scores['subject_score']:.1f})")
        
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
            scores["attachment_score"] += 10.0  # Bonus for having both form and data sheets
        
        if scores["attachment_score"]:
            reasoning.append(f"Attachments suggest ATS content (score: {scores['attachment_score']:.1f})")
        
        return self._format_result(scores, reasoning, subject, sender)
    
    def _format_result(self, scores: Dict, reasoning: List[str], subject: str, sender: str) -> Dict:
        """Format the scoring result into a structured dictionary."""
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
            "details": scores,
            "subject": subject,
            "sender": sender
        }


def score_msg_file(msg_path: str) -> Optional[Dict]:
    """
    Parse and score a single .msg file for ATS probability.
    
    Args:
        msg_path: Path to the .msg file
        
    Returns:
        Dictionary containing email metadata and ATS score, or None if parsing fails.
        Structure:
        {
            "subject": str,
            "sender": str,
            "attachments": List[str],
            "ats_score": {
                "total_score": float,
                "probability": str,
                "is_ats_application": bool,
                "reasoning": List[str],
                "details": Dict
            }
        }
        
    Raises:
        FileNotFoundError: If the .msg file doesn't exist
        Exception: If there's an error parsing the .msg file
    """
    if not os.path.exists(msg_path):
        raise FileNotFoundError(f"Message file not found: {msg_path}")
    
    if not msg_path.lower().endswith('.msg'):
        raise ValueError(f"File is not a .msg file: {msg_path}")
    
    try:
        # Parse the .msg file
        msg = extract_msg.Message(msg_path)
        
        # Extract email data
        subject = msg.subject or ""
        sender = msg.sender or ""
        attachments = [
            att.longFilename or att.shortFilename or f"attachment_{i+1}"
            for i, att in enumerate(msg.attachments)
        ]
        
        # Score the email
        scorer = ATSEmailScorer()
        score_data = scorer.score_email(subject, sender, attachments)
        
        return {
            "subject": subject,
            "sender": sender,
            "attachments": attachments,
            "msg_path": msg_path,
            "ats_score": score_data
        }
        
    except Exception as e:
        raise Exception(f"Error parsing {msg_path}: {e}")


def print_score_summary(result: Dict):
    """
    Print a human-readable summary of the scoring result.
    
    Args:
        result: Result dictionary from score_msg_file()
    """
    if result is None:
        print("No result to display.")
        return
    
    print("=" * 60)
    print("ATS EMAIL SCORE SUMMARY")
    print("=" * 60)
    print(f"Subject: {result['subject']}")
    print(f"Sender: {result['sender']}")
    print(f"Attachments: {len(result['attachments'])}")
    if result['attachments']:
        for att in result['attachments']:
            print(f"  - {att}")
    
    score = result['ats_score']
    print(f"\nTotal Score: {score['total_score']:.1f}")
    print(f"Probability: {score['probability']}")
    print(f"ATS Application: {'YES' if score['is_ats_application'] else 'NO'}")
    
    print("\nScore Breakdown:")
    for key, value in score['details'].items():
        if value != 0:
            print(f"  {key}: {value:.1f}")
    
    print("\nReasoning:")
    for reason in score['reasoning']:
        print(f"  - {reason}")
    print("=" * 60)


# ========== MAIN ==========
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python score_msg.py <path_to_msg_file>")
        sys.exit(1)
    
    msg_file = sys.argv[1]
    
    try:
        result = score_msg_file(msg_file)
        print_score_summary(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

