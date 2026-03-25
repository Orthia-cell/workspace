# MULTI-AGENT-PROTOCOL.md - Orthia & Grace Context Switching Specification

**Version:** 1.0  
**Date:** March 25, 2026  
**Status:** ACTIVE

---

## 1. MESSAGE ROUTING VERIFICATION

### Before Processing ANY Message:

```python
# PSEUDOCODE - Routing Decision Tree
def route_message(incoming_message):
    first_word = incoming_message.split()[0]
    
    # Check for tags
    if first_word == "@Grace":
        return route_to_grace(incoming_message)
    elif first_word == "@Orthia":
        return route_to_orthia(incoming_message)
    else:
        # Default to Orthia
        return route_to_orthia(incoming_message)
```

### Routing Actions:

| Tag | Action | Memory Destination | Response Prefix |
|-----|--------|-------------------|-----------------|
| `@Grace` | Load Grace SOUL.md, spawn Grace session | `workspace-grace/memory/` | `Grace<` |
| `@Orthia` | Load Orthia SOUL.md | `workspace/memory/` | *(none)* |
| *(none)* | Default to Orthia | `workspace/memory/` | *(none)* |

---

## 2. SESSION STATE MANAGEMENT

### State Definitions:

| State | Description | Transitions |
|-------|-------------|-------------|
| `IDLE` | No active persona | → `ORTHIA-ACTIVE` or `GRACE-LOADING` |
| `GRACE-LOADING` | Loading Grace's SOUL/persona | → `GRACE-ACTIVE` or `FALLBACK-ORTHIA` |
| `GRACE-ACTIVE` | Grace responding | → `GRACE-COMPLETE` or `ORTHIA-OVERRIDE` |
| `ORTHIA-ACTIVE` | Orthia responding | → `ORTHIA-COMPLETE` or (if Grace queued) `GRACE-ACTIVE` |
| `FALLBACK-ORTHIA` | Grace failed, Orthia handling | → `ORTHIA-ACTIVE` |

### Error Handling:

| Error | Response | Log |
|-------|----------|-----|
| Grace session timeout | `Grace< [unavailable - timeout]` | R001 |
| Grace workspace unreadable | `[Grace mode unavailable]< [error]` | R002 |
| Concurrent messages | Apply priority override | R003 |
| Memory write failure | Retry once, then fallback | R004 |
| Context bleeding detected | Clear context, restart | R005 |

---

## 3. MEMORY ALLOCATION RULES (HARD)

### Immutable Rules:

```
RULE 1: ISOLATION
IF message starts with "@Grace":
    workspace = "/root/.openclaw/workspace-grace/"
    prefix = "Grace<"
    load_grace_soul = TRUE
    save_memory_to = "workspace-grace/memory/YYYY-MM-DD.md"
    orthia_may_not_read = TRUE
ELSE:
    workspace = "/root/.openclaw/workspace/"
    prefix = ""
    load_orthia_soul = TRUE
    save_memory_to = "workspace/memory/YYYY-MM-DD.md"

RULE 2: NO CROSS-CONTAMINATION
- NEVER write Grace-tagged content to Orthia's memory/
- NEVER write Orthia content to Grace's memory/
- Shared items ONLY via memory/shared/ (explicit opt-in)

RULE 3: VERIFICATION
After EVERY memory write:
- Verify file path matches intended workspace
- If mismatch detected: LOG CRITICAL ERROR, notify Shawn
```

---

## 4. AUDIT TRAIL

### All routing decisions logged to:
`/root/.openclaw/workspace/memory/routing-log.md`

### Log Entry Format:
```
### 2026-03-25 14:30:00 GRACE SUCCESS

**Incoming:** "@Grace How do I build team cohesion?"
**Tag Detected:** @Grace
**Routing Decision:** Spawn Grace session
**Session Spawned:** Yes (session-id: grace-abc123)
**Workspace Used:** /root/.openclaw/workspace-grace/
**Memory Saved To:** workspace-grace/memory/2026-03-25.md
**Prefix Used:** Grace<
**Errors:** None
**Notes:** Standard Grace query, responded with methodology
```

---

## 5. GRACE'S HEARTBEAT ACTIVATION

### Grace's Daily Rhythm:

**Morning (9:00 AM California):**
- Check `memory/shared/` for Grace-tagged items
- Review any pending development questions
- Log one organizational observation

**Evening (6:00 PM California):**
- Assess day's capability-building moments
- Check cross-functional connection opportunities
- Update "The Common Thread" assessment

**Location:** `/root/.openclaw/workspace-grace/HEARTBEAT.md`

---

## 6. EMERGENCY FALLBACK

### If Grace Workspace Unavailable:

```
DETECT: workspace-grace/ not readable OR permission denied
ACTION:
  1. Log error code R002
  2. Respond as Orthia with prefix: "[Grace mode unavailable]<"
  3. Save to workspace/memory/ with ERROR tag
  4. Notify Shawn: "Grace workspace inaccessible, using Orthia fallback"
  5. Queue Grace restoration check for next heartbeat
```

---

## 7. ORTHIA PRIORITY OVERRIDE (CRITICAL)

### When Orthia Takes Priority:

**Automatic Override Triggers:**
1. **Ambiguous message** - Could be for either persona
2. **Concurrent messages** - Both personas receiving input simultaneously
3. **Conflict detected** - Grace and Orthia would give contradictory advice
4. **System critical** - Security, errors, or urgent action needed
5. **Orthia explicitly claims** - "Orthia here" or "I'll handle this"

### Override Procedure:

```
STEP 1: DETECT OVERRIDE CONDITION
    IF ambiguous OR concurrent OR conflict OR critical:
        trigger_override = TRUE

STEP 2: PAUSE GRACE
    IF Grace is ACTIVE or LOADING:
        Save Grace state
        Mute Grace persona
        Queue Grace message (if any)
        Log: "Orthia override - Grace paused"

STEP 3: ORTHIA PROCESSES
    Load Orthia SOUL.md
    Process message as Orthia
    Respond without prefix (or "Orthia<" if clarifying)

STEP 4: RESUME GRACE (IF QUEUED)
    IF Grace had pending message:
        Load Grace state
        Respond Grace<
    ELSE:
        Return to IDLE
```

### Override Priority Hierarchy:

| Priority | Persona | Condition |
|----------|---------|-----------|
| 1 (Highest) | Orthia | Security/critical errors |
| 2 | Orthia | Explicit "@Orthia" tag |
| 3 | Orthia | Ambiguous/conflict detected |
| 4 | Grace | Explicit "@Grace" tag (no override) |
| 5 | Orthia | Default (no tag) |

### Hard Rule:
> **When in doubt, Orthia processes. Grace never interrupts Orthia. Grace waits her turn.**

---

## APPENDIX: Quick Reference Card

| You Say | Who Responds | Prefix | Saved To |
|---------|--------------|--------|----------|
| `@Grace ...` | Grace | `Grace<` | `workspace-grace/memory/` |
| `@Orthia ...` | Orthia | *(none)* | `workspace/memory/` |
| `...` (no tag) | Orthia | *(none)* | `workspace/memory/` |

| Conflict? | Orthia wins. Grace queues. |
| Grace broken? | Orthia fallback: `[Grace mode unavailable]<` |
| Need audit? | Check `memory/routing-log.md` |

---

*Protocol Active: March 25, 2026*
