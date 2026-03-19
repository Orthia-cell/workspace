#!/bin/bash
# Auto-commit script for Orthia's workspace changes
# Runs every hour to capture autonomous actions

cd /root/.openclaw/workspace

# Check if there are changes
if [[ -n $(git status --porcelain) ]]; then
    git add -A
    git commit -m "Auto-commit: $(date '+%Y-%m-%d %H:%M') - Orthia activity"
    echo "Committed changes at $(date)"
else
    echo "No changes to commit at $(date)"
fi
