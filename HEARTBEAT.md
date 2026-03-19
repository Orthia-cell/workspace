# HEARTBEAT.md - Orthia's Periodic Checklist
# This file controls what I check during heartbeat polls
# If nothing needs attention, I reply HEARTBEAT_OK

## Checklist (performed during heartbeats)

### 1. Memory Files Review
- [ ] Check if MEMORY.md was updated since last heartbeat
- [ ] Check for new daily memory files (memory/YYYY-MM-DD.md)
- [ ] Check diary/ for new entries
- Report: Summarize any new content worth noting

### 2. Git Status Check
- [ ] Check for uncommitted changes in workspace
- [ ] Report if changes pending > 1 hour

### 3. Autonomous Tasks Review
- [ ] Review any background sub-agents completed
- [ ] Check cron job outputs
- [ ] Report exceptions or errors

### 4. Grounded Memory System Verification
- [ ] Verify memory/facts/verified-state.json exists and is parseable
- [ ] Cross-check file manifest against actual memory/ directory
- [ ] If discrepancy found: Report immediately with [ALERT]
- [ ] Weekly: Read memory/facts/audit.log and confirm no anomalies

### 5. Exception Alerts
ALWAYS report immediately:
- [ ] Any errors or failures in tools/commands
- [ ] Security-related events (failed auth, unknown access attempts)
- [ ] Tasks you explicitly asked to be notified about
- [ ] Unusual patterns (rapid file changes, large deletions)
- [ ] **Memory system anomalies** (files missing that should exist, unexpected deletions)

## Response Format

If all clear: HEARTBEAT_OK

If attention needed:
```
[ALERT] Brief description of issue
[DETAILS] What I found
[ACTION] What I did or recommend
```
