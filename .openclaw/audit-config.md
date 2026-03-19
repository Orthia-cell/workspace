# Audit Configuration for Orthia
# Created: 2026-02-26
# Purpose: Track autonomous actions and system changes

## Git Auto-Commit
- Script: .openclaw/auto-commit.sh
- Frequency: Every hour via cron
- Captures: All file changes in workspace

## Daily Digest
- Schedule: 9:00 PM PST (midnight your time)
- Delivery: To be configured
- Contents: Summary of day's activities

## Exception Alerts
- Immediate notification for: errors, security events, explicit requests
- Delivery: Same channel as daily digest

## Memory Locations
- Daily logs: memory/YYYY-MM-DD.md
- Long-term: MEMORY.md
- Diary: diary/ (my private notes)
- This file: .openclaw/audit-config.md
