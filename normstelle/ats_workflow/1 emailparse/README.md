# Email Parsing and ATS Scoring Scripts

This directory contains scripts for parsing email messages (`.msg` files) and analyzing them for ATS (Application for Teile und Stoffe / Application for Parts and Substances) applications.

## Overview

The scripts in this directory work together to:
1. Parse Outlook `.msg` files and extract metadata
2. Score emails for ATS application probability
3. Generate reports on email analysis

## Scripts

### `mailparser.py`
**Purpose**: Basic email metadata extraction

Parses all `.msg` files from a specified directory tree and extracts basic metadata:
- Email subject
- Sender address
- Attachment filenames
- Path to the folder containing the email

**Output**: `parsed_messages.json` - A JSON file containing an array of email metadata objects.

**Usage**: 
- Modify `ROOT_FOLDER` variable to point to your email directory
- Run the script to generate `parsed_messages.json`

---

### `mailscorer.py`
**Purpose**: Parse and score emails for ATS probability

Combines email parsing with ATS scoring. This script:
- Walks through a directory of `.msg` files
- Extracts email metadata (subject, sender, attachments)
- Scores each email for ATS application probability using keyword matching and attachment pattern recognition
- Outputs results with detailed scoring breakdown

**Scoring Logic**:
- **High keywords** (10 points): "antrag", "ats", "afts", "teile und stoffe", etc.
- **Medium keywords** (3 points): "freigabe", "approval", "material", etc.
- **Attachment patterns**:
  - ATS forms: +15 points
  - Safety Data Sheets (SDS): +8 points
  - Technical Data Sheets (TDS): +5 points
  - Bonus: +10 points if both ATS form and data sheets present
- **Ignore rules**: Emails from specific senders or with certain subjects are penalized (-100 points)

**Output**: `ats-scores.json` - JSON file with email data and ATS scoring results.

**Usage**:
- Modify `ROOT_DIR` variable to point to your email directory
- Run the script to generate scored results

---

### `scorer.py`
**Purpose**: Comprehensive ATS email scoring with report generation

A more advanced scoring system that works with JSON email data files. This script provides:
- Detailed scoring of email subject, body, and attachments
- Probability classification (HIGH, MEDIUM, LOW, NONE)
- Detailed reasoning for each score
- Report generation functionality

**Features**:
- Works with pre-extracted email JSON files (e.g., `emails_inbox.json`)
- Handles multiple file encodings (UTF-8, Latin1, CP1252)
- Generates detailed text reports with statistics
- Identifies high-probability ATS applications

**Output**: 
- Console output with summary statistics
- `ats_email_analysis_report.txt` - Detailed report file

**Usage**:
- Ensure you have an email JSON file (the script searches multiple possible paths)
- Run the script to analyze emails and generate a report

---

### `msgparser.py`
**Purpose**: Parse and split individual `.msg` files

Utility script for parsing a single `.msg` file:
- Extracts HTML body content
- Splits HTML body into separate parts (based on email thread separators)
- Extracts and saves all attachments

**Output**: 
- `output/message_part_*.html` - Individual HTML parts of the email
- `output/attachments/` - Directory containing all email attachments

**Usage**:
```bash
python msgparser.py <path_to_msg_file>
```

---

### `score_msg.py`
**Purpose**: Score a single `.msg` file for ATS probability

A standalone module for scoring individual `.msg` files. This is the recommended way to score a single email file programmatically.

**Features**:
- Parses a single `.msg` file
- Extracts subject, sender, and attachments
- Scores the email using ATS probability algorithm
- Returns structured results with detailed scoring breakdown
- Can be used as a module or run as a script

**Usage as a script**:
```bash
python score_msg.py <path_to_msg_file>
```

**Usage as a module**:
```python
from score_msg import score_msg_file, print_score_summary

result = score_msg_file("path/to/email.msg")
print_score_summary(result)

# Access the score data
score = result['ats_score']
print(f"Probability: {score['probability']}")
print(f"Total Score: {score['total_score']}")
```

**Output**: Returns a dictionary with email metadata and ATS scoring results, or prints a formatted summary when run as a script.

---

### `fromwho.py`
**Purpose**: Documentation for ongoing ATS application detection

This file contains documentation and planning notes for detecting ongoing ATS applications at different stages of the approval workflow. It describes:
- The ATS application workflow stages (6 stages from incoming application to final approval)
- Department email addresses involved in the process
- Detection criteria for each stage (ChemScan, UWS, HSE OU/DW, LAB OU/DW)

**Status**: Currently contains documentation/comments only - implementation pending.

---

### `emailer.py`
**Purpose**: Path configuration

Contains path definitions for email data files:
- `inbox_json_path` - Path to the email inbox JSON file
- `email_data_files` - Path to the email data directory

**Status**: Configuration file with path definitions.

---

## Workflow

A typical workflow might be:

1. **Extract emails**: Use `mailparser.py` to extract basic metadata from `.msg` files
2. **Score emails**: 
   - For single files: Use `score_msg.py` to score individual `.msg` files
   - For batch processing: Use `mailscorer.py` or `scorer.py` to analyze multiple emails for ATS probability
3. **Review results**: Check the generated JSON files or reports to identify high-probability ATS applications
4. **Parse specific emails**: Use `msgparser.py` to extract attachments and split email threads from specific `.msg` files

## Dependencies

- `extract_msg` - For parsing Outlook `.msg` files
- Standard Python libraries: `json`, `os`, `re`, `typing`, `pathlib`

## Output Files

- `parsed_messages.json` - Basic email metadata (from `mailparser.py`)
- `ats-scores.json` - Email data with ATS scores (from `mailscorer.py`)
- `ats_email_analysis_report.txt` - Detailed scoring report (from `scorer.py`)
- `output/` - Directory for parsed email parts and attachments (from `msgparser.py`)

## Notes

- All scripts expect `.msg` files (Outlook message format)
- Paths are hardcoded in some scripts and may need to be adjusted for your environment
- The scoring system is designed to identify new incoming ATS applications and filter out internal communications

