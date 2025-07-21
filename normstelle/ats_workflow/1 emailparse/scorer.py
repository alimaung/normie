# Rate/score the email for ATS probability 
# Should detect only new, incoming Applications:
# High ATS probability:
# - "Antrag", "ATS", "AfTS", "AfT&S", "AfTuS", "Antrag Teile und Stoffe", "Antrag für Teile und Stoffe", "Teile und Stoffe" in subject/body/attachments
# - At least 1 attachment (ATS form, SDS/TDS,PDS is optional):
# - Attachments filename contains "ATS", "AfTS", "AfT&S", "Antrag Teile und Stoffe", "Teile und Stoffe", "Antrag" - likely the Application form
# - Attachment filename contains "SDB", "MSDS", "SDS" - likely the Safety Data Sheet
# - Attachment filename contains "PDB", "TDB", "TDS", "PDS" - likely the Technical Data Sheet/Product Data Sheet

# To ignore: Emails by ourselves (we CC every outgoing email) IRM-Standartization-Office@rolls-royce.com
# To ignore: Emails with this in subject: "QCTP", "PBR", "DIN", "RQSC", "Ballot", "LA", "EDNS", 

# Email Folder: Y:\normie\outlook\analyze\mail\data
# Contains folders with msg. and attachments already extracted.
# Email json: Y:\normie\outlook\analyze\mail\emails_inbox.json
# Tracks metadata for each email
# Links the files to the json

import json
import re
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class EmailScore:
    """Represents an email's ATS probability score and reasoning."""
    email_hash: str
    subject: str
    sender_email: str
    total_score: float
    probability: str  # "HIGH", "MEDIUM", "LOW", "NONE"
    reasoning: List[str]
    details: Dict[str, float]
    is_ats_application: bool

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
        self.ats_attachment_patterns = [
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
    
    def score_email(self, email_data: Dict) -> EmailScore:
        """Score a single email for ATS probability."""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        html_body = email_data.get('html_body', '').lower()
        sender_email = email_data.get('sender_email', '').lower()
        attachments = email_data.get('attachments', [])
        email_hash = email_data.get('hash', '')
        
        # Initialize scoring
        scores = {
            'subject_score': 0.0,
            'body_score': 0.0,
            'attachment_score': 0.0,
            'sender_penalty': 0.0,
            'ignore_penalty': 0.0
        }
        reasoning = []
        
        # Check if we should ignore this email
        if self._should_ignore_email(sender_email, subject):
            scores['ignore_penalty'] = -100.0
            reasoning.append(f"Email ignored: sender or subject matches ignore patterns")
            probability = "NONE"
            is_ats = False
        else:
            # Score subject line
            scores['subject_score'] = self._score_text(subject, 'subject')
            if scores['subject_score'] > 0:
                reasoning.append(f"Subject contains ATS keywords (score: {scores['subject_score']:.1f})")
            
            # Score body content
            combined_body = f"{body} {html_body}"
            scores['body_score'] = self._score_text(combined_body, 'body')
            if scores['body_score'] > 0:
                reasoning.append(f"Body contains ATS keywords (score: {scores['body_score']:.1f})")
            
            # Score attachments
            scores['attachment_score'] = self._score_attachments(attachments)
            if scores['attachment_score'] > 0:
                reasoning.append(f"Attachments suggest ATS content (score: {scores['attachment_score']:.1f})")
            
            # Calculate total score and probability
            total_score = sum(scores.values())
            probability, is_ats = self._determine_probability(total_score, attachments)
        
        # Add reasoning for probability determination
        if probability == "HIGH":
            reasoning.append("HIGH probability: Strong ATS indicators found")
        elif probability == "MEDIUM":
            reasoning.append("MEDIUM probability: Some ATS indicators found")
        elif probability == "LOW":
            reasoning.append("LOW probability: Few ATS indicators found")
        else:
            reasoning.append("NO ATS probability: No indicators or ignored")
        
        return EmailScore(
            email_hash=email_hash,
            subject=email_data.get('subject', ''),
            sender_email=email_data.get('sender_email', ''),
            total_score=sum(scores.values()),
            probability=probability,
            reasoning=reasoning,
            details=scores,
            is_ats_application=is_ats
        )
    
    def _should_ignore_email(self, sender_email: str, subject: str) -> bool:
        """Check if email should be ignored based on sender or subject."""
        # Check sender
        for ignore_sender in self.ignore_senders:
            if ignore_sender.lower() in sender_email:
                return True
        
        # Check subject for ignore patterns
        for ignore_pattern in self.ignore_subjects:
            if ignore_pattern.lower() in subject:
                return True
        
        return False
    
    def _score_text(self, text: str, context: str) -> float:
        """Score text content for ATS keywords."""
        if not text:
            return 0.0
        
        score = 0.0
        
        # High value keywords
        for keyword in self.high_keywords:
            if keyword in text:
                # Subject line gets higher weight
                weight = 10.0 if context == 'subject' else 5.0
                score += weight
        
        # Medium value keywords
        for keyword in self.medium_keywords:
            if keyword in text:
                weight = 3.0 if context == 'subject' else 2.0
                score += weight
        
        return score
    
    def _score_attachments(self, attachments: List[Dict]) -> float:
        """Score attachments for ATS relevance."""
        if not attachments:
            return 0.0
        
        score = 0.0
        ats_form_found = False
        sds_found = False
        tds_found = False
        
        for attachment in attachments:
            filename = attachment.get('filename', '').lower()
            
            # Check for ATS form
            for pattern in self.ats_attachment_patterns:
                if re.match(pattern, filename, re.IGNORECASE):
                    score += 15.0  # High score for ATS form
                    ats_form_found = True
                    break
            
            # Check for Safety Data Sheet
            for pattern in self.sds_patterns:
                if re.match(pattern, filename, re.IGNORECASE):
                    score += 8.0  # Medium-high score for SDS
                    sds_found = True
                    break
            
            # Check for Technical Data Sheet
            for pattern in self.tds_patterns:
                if re.match(pattern, filename, re.IGNORECASE):
                    score += 5.0  # Medium score for TDS/PDS
                    tds_found = True
                    break
        
        # Bonus for having both form and data sheets
        if ats_form_found and (sds_found or tds_found):
            score += 10.0
        
        # Basic attachment bonus (ATS usually has attachments)
        if len(attachments) > 0:
            score += 2.0
        
        return score
    
    def _determine_probability(self, total_score: float, attachments: List[Dict]) -> Tuple[str, bool]:
        """Determine probability category and ATS status based on total score."""
        # Must have at least one attachment for HIGH probability
        has_attachments = len(attachments) > 0
        
        if total_score >= 20.0 and has_attachments:
            return "HIGH", True
        elif total_score >= 10.0:
            return "MEDIUM", False
        elif total_score >= 3.0:
            return "LOW", False
        else:
            return "NONE", False
    
    def score_emails_from_json(self, json_file_path: str) -> List[EmailScore]:
        """Score all emails from a JSON file."""
        # Try different encodings to handle file encoding issues
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        
        for encoding in encodings_to_try:
            try:
                with open(json_file_path, 'r', encoding=encoding) as f:
                    data = json.load(f)
                print(f"Successfully loaded JSON with {encoding} encoding")
                break
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                if encoding == encodings_to_try[-1]:  # Last encoding attempt
                    print(f"Failed to load JSON with all encodings. Last error: {e}")
                    raise
                continue
        
        emails = data.get('emails', [])
        scores = []
        
        for email in emails:
            score = self.score_email(email)
            scores.append(score)
        
        return scores
    
    def generate_report(self, scores: List[EmailScore], output_file: str = None) -> str:
        """Generate a detailed report of email scores."""
        # Sort by score (highest first)
        scores.sort(key=lambda x: x.total_score, reverse=True)
        
        report_lines = []
        report_lines.append("ATS EMAIL SCORING REPORT")
        report_lines.append("=" * 50)
        report_lines.append(f"Total emails analyzed: {len(scores)}")
        
        # Summary statistics
        high_prob = len([s for s in scores if s.probability == "HIGH"])
        medium_prob = len([s for s in scores if s.probability == "MEDIUM"])
        low_prob = len([s for s in scores if s.probability == "LOW"])
        none_prob = len([s for s in scores if s.probability == "NONE"])
        
        report_lines.append(f"HIGH probability: {high_prob}")
        report_lines.append(f"MEDIUM probability: {medium_prob}")
        report_lines.append(f"LOW probability: {low_prob}")
        report_lines.append(f"NO probability: {none_prob}")
        report_lines.append("")
        
        # Detailed results
        report_lines.append("DETAILED RESULTS:")
        report_lines.append("-" * 30)
        
        for score in scores:
            if score.probability != "NONE":  # Skip ignored emails in detailed view
                report_lines.append(f"\nSubject: {score.subject[:80]}...")
                report_lines.append(f"Sender: {score.sender_email}")
                report_lines.append(f"Probability: {score.probability} (Score: {score.total_score:.1f})")
                report_lines.append(f"ATS Application: {'YES' if score.is_ats_application else 'NO'}")
                
                # Score breakdown
                report_lines.append("Score breakdown:")
                for detail, value in score.details.items():
                    if value != 0:
                        report_lines.append(f"  - {detail}: {value:.1f}")
                
                # Reasoning
                report_lines.append("Reasoning:")
                for reason in score.reasoning:
                    report_lines.append(f"  - {reason}")
                
                report_lines.append("-" * 50)
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"Report saved to: {output_file}")
        
        return report_text

def main():
    """Main function for testing/running the scorer."""
    scorer = ATSEmailScorer()
    
    # Try multiple possible paths for the email JSON file
    possible_paths = [
        "../../../outlook/analyze/mail/emails_inbox.json",
        "../../outlook/analyze/mail/emails_inbox.json", 
        "../../../../outlook/analyze/mail/emails_inbox.json",
        "Y:/normie/outlook/analyze/mail/emails_inbox.json",
        "/y%3A/normie/outlook/analyze/mail/emails_inbox.json"
    ]
    
    json_file = None
    for path in possible_paths:
        if os.path.exists(path):
            json_file = path
            print(f"Found email JSON file at: {json_file}")
            break
    
    if not json_file:
        print("Email JSON file not found at any of these locations:")
        for path in possible_paths:
            print(f"  - {path}")
        print("Please ensure the email extraction has been run first.")
        return
    
    print("Analyzing emails for ATS probability...")
    scores = scorer.score_emails_from_json(json_file)
    
    # Generate and display report
    report = scorer.generate_report(scores, "ats_email_analysis_report.txt")
    
    # Show summary
    high_prob_emails = [s for s in scores if s.probability == "HIGH"]
    print(f"\nSUMMARY:")
    print(f"Found {len(high_prob_emails)} high-probability ATS emails")
    
    if high_prob_emails:
        print("\nHIGH PROBABILITY ATS EMAILS:")
        for email in high_prob_emails:
            print(f"- {email.subject[:60]}... (Score: {email.total_score:.1f})")

if __name__ == "__main__":
    main()







