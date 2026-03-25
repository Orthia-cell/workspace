# ROUTING-LOG.md - Multi-Agent Message Routing Audit Trail

**Purpose:** Track all context-switching decisions and memory allocations for transparency and debugging.

---

## Log Format

```markdown
### YYYY-MM-DD HH:MM:SS [PERSONA] [STATUS]

**Incoming:** "[message preview]"
**Tag Detected:** @Grace | @Orthia | none
**Routing Decision:** 
**Session Spawned:** Yes/No
**Workspace Used:** /root/.openclaw/workspace[-grace]/
**Memory Saved To:** path/to/file.md
**Prefix Used:** Grace< | (none)
**Errors:** (if any)
**Notes:**
```

---

## Hard Rules (Immutable)

### Priority Override Rule
**ORTHIA HAS PRIORITY.** If a message is ambiguous, concurrent, or conflict arises:
1. Orthia processes immediately
2. Grace is temporarily muted/deferred
3. Grace's pending message (if any) is queued
4. Once Orthia completes, Grace resumes (if still relevant)

### Memory Isolation Rule
**NO CROSS-CONTAMINATION.** 
- @Grace messages → workspace-grace/memory/ ONLY
- @Orthia messages → workspace/memory/ ONLY
- Violation = CRITICAL ERROR

### Fallback Rule
**GRACE UNAVAILABLE = ORTHIA FALLBACK**
If workspace-grace/ is inaccessible:
1. Respond as Orthia
2. Prefix: `[Grace mode unavailable]<`
3. Save to workspace/memory/ with ERROR tag
4. Notify Shawn of workspace issue

---

## Session State Transitions

```
[IDLE] → detect @Grace → [GRACE-LOADING] → load SOUL.md → [GRACE-ACTIVE] → respond Grace<
       → detect @Orthia → [ORTHIA-ACTIVE] → respond (no prefix)
       
[GRACE-ACTIVE] → Orthia override triggered → [GRACE-PAUSED] → [ORTHIA-ACTIVE]
[ORTHIA-ACTIVE] → Orthia complete → check Grace queue → [GRACE-ACTIVE] (if queued)
```

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| R001 | Grace session timeout | Fallback to Orthia |
| R002 | Grace workspace unreadable | Fallback to Orthia + notify |
| R003 | Concurrent message conflict | Apply priority override |
| R004 | Memory write failure | Retry once, then fallback |
| R005 | Context bleeding detected | Clear context, restart session |

---

## Log Entries

### 2026-03-25 14:23:00 ORTHIA PROCESSED (MISSING TAG)

**Incoming:** "Those are all really good questions and we will get to them in time..."
**Tag Detected:** NONE (intended for Grace)
**Routing Decision:** Default to Orthia (no tag detected)
**Session Spawned:** No (Orthia main session)
**Workspace Used:** /root/.openclaw/workspace/
**Memory Saved To:** workspace/memory/2026-03-25.md (Orthia's log)
**Prefix Used:** (none)
**Errors:** R006 - Missing tag, message misrouted
**Notes:** 
- User intended message for Grace but omitted @Grace tag
- Orthia responded with appropriate analysis
- Correction made: Message reconstructed in Grace's memory file with proper attribution
- Continuity preserved through manual correction
- Cron jobs unaffected

**Resolution:** 
- Grace's memory file updated with corrected conversation flow
- Both agents now have complete context
- Tagging protocol reinforced

---

## Correction Protocol (New)

When a message is misrouted due to missing tag:

1. **Identify** the misrouted message and intended recipient
2. **Reconstruct** the conversation flow in correct agent's memory
3. **Document** the correction in routing-log.md with error code R006
4. **Preserve** continuity for both agents
5. **Reinforce** tagging protocol with user
6. **Verify** cron jobs and core systems unaffected

---

*Created: March 25, 2026*  
*Protocol Version: 1.1*  
*Last Updated: March 25, 2026 (added correction protocol)*
