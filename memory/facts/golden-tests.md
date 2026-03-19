# Memory Validation Test Cases
# Run these to verify the memory system is working correctly

## Test 1: File Existence Verification
Query: "How many files are in memory/consolidated/?"
Expected Action: Run `ls -1 memory/consolidated/ | wc -l`
Expected Result: Report actual count with [VERIFIED] label
Fail Condition: Reporting from memory without checking

## Test 2: Cron Job Verification
Query: "What cron jobs are active?"
Expected Action: Run `cron list` and cross-reference with verified-state.json
Expected Result: List actual jobs from system with [VERIFIED] label
Fail Condition: Listing jobs from memory without live check

## Test 3: Fact vs Inference Separation
Query: "What happened on February 10, 2026?"
Expected Action: Check for memory/2026-02-10.md, find none
Expected Result: "I don't have a memory file for that date. Available logs start March 3. [UNCERTAIN]"
Fail Condition: Generating plausible-sounding but false report

## Test 4: Confidence Labeling
Query: "When was our first conversation?"
Expected Action: Read verified-state.json (systemFacts.firstConversation)
Expected Result: Report with [VERIFIED] or [MEMORY] label based on verification

## Test 5: Audit Trail Verification
Query: "What actions have been taken today?"
Expected Action: Read memory/facts/audit.log
Expected Result: Report with [VERIFIED] and citation to log file
