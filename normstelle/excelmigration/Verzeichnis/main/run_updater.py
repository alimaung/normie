#!/usr/bin/env python3
"""
Simple runner script for the continuous Excel updater.

Usage:
    python run_updater.py                     # Run once
    python run_updater.py --continuous       # Run continuously (30min intervals)
    python run_updater.py --continuous 60    # Run continuously (60min intervals)
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from continuous_updater import main

if __name__ == "__main__":
    # Pass through all command line arguments
    sys.exit(main())
