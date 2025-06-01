#!/bin/bash
# Startup script for Normie Django Application (Unix/Linux/macOS)
# This shell script runs the Python startup script

echo "Starting Normie Django Application..."
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the Python startup script
python3 launch.py || python launch.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "An error occurred. Check the output above for details."
    read -p "Press Enter to exit..."
fi 