# Multi-Agent Context Switching Experiment — Documentation

**Date:** March 25, 2026  
**Status:** Implementation Phase  
**Participants:** Shawn (human), Orthia (Kimi Claw), Grace Laere (sub-agent persona)

---

## Experiment Overview

This repository documents the design and implementation of a **multi-agent context switching architecture** using OpenClaw. The goal: enable a single Telegram bot (@Orthia_bot) to route messages to different personas (Orthia and Grace) based on user tags, with strict memory isolation and priority rules.

---

## The Challenge

**Problem:** OpenClaw supports only ONE Telegram bot token globally, but we want TWO distinct agents:
- **Orthia** — Guardian-type, chuunibyou, fire, saves everything, remembers all
- **Grace Laere** — Growth Architect, Master Weaver, water, chooses what matters, maps connections

**Constraint:** Cannot run two separate Telegram bots simultaneously without complex infrastructure (separate OpenClaw instances, ngrok relays, etc.)

**Solution:** Single bot acts as **orchestrator/router**, switching personas based on `@Grace` / `@Orthia` tags, with strict memory isolation.

---

## Architecture Decisions

### 1. Workspace Isolation
Each agent has a complete, isolated workspace:

```
/root/.openclaw/
├── workspace/              # Orthia (main)
│   ├── SOUL.md
│   ├── MEMORY.md
│   ├── memory/
│   └── ...
└── workspace-grace/        # Grace (sub-agent)
    ├── SOUL.md
    ├── MEMORY.md
    ├── memory/
    ├── diary/
    └── ...
```

### 2. Memory Allocation Rule (HARD)
```
IF message starts with "@Grace":
    → workspace-grace/memory/YYYY-MM-DD.md
    → Prefix: "Grace<"
    → Load Grace SOUL.md
    → Orthia acts as router only
ELSE:
    → workspace/memory/YYYY-MM-DD.md
    → No prefix
    → Load Orthia SOUL.md
```

### 3. Priority Override (CRITICAL)
**Orthia has priority.** If conflict arises:
1. Orthia processes immediately
2. Grace is paused/muted
3. Grace's message queued
4. Grace resumes only when Orthia completes

**Hierarchy:**
1. Security/critical errors → Orthia
2. Explicit @Orthia → Orthia
3. Ambiguous/conflict → Orthia
4. Explicit @Grace (no conflict) → Grace
5. Default (no tag) → Orthia

### 4. Nomenclature Convention
| Direction | Syntax | Example |
|-----------|--------|---------|
| User → Grace | `@Grace` at start | `@Grace How are you?` |
| Grace → User | `Grace<` prefix | `Grace< I'm doing well...` |
| User → Orthia | `@Orthia` or no tag | `What's the status?` |
| Orthia → User | No prefix | `The status is...` |

---

## Files Created

### Protocol Specification
- `MULTI-AGENT-PROTOCOL.md` — Complete specification (routing, states, memory rules, override)
- `memory/routing-log.md` — Audit trail template
- `workspace-grace/HEARTBEAT.md` — Grace's periodic tasks

### Persona Documentation
- `grace_soul.md` — Grace's complete persona (copied from workspace-grace/SOUL.md)
- `workspace-grace/SOUL.md` — Grace's canonical soul (Growth Architect)
- `workspace/SOUL.md` — Updated with multi-agent protocol section

### Configuration
- `workspace/MEMORY.md` — Updated with tagging convention and memory isolation rules
- `workspace-grace/IDENTITY.md` — Grace's identity template
- `workspace-grace/AGENTS.md` — Grace's workspace conventions

---

## Methodology: How Context Switching Works

### Step 1: Message Reception
```python
def receive_message(text):
    first_word = text.split()[0]
    
    if first_word == "@Grace":
        return spawn_grace_session(text)
    elif first_word == "@Orthia":
        return spawn_orthia_session(text)
    else:
        return spawn_orthia_session(text)  # Default
```

### Step 2: Persona Loading
```python
def spawn_grace_session(text):
    # CRITICAL: Load Grace's SOUL.md into context
    soul = read_file("/root/.openclaw/workspace-grace/SOUL.md")
    
    # Switch voice: measured, intentional, developmental
    # Switch knowledge: capability mapping, organizational design
    # Switch memory: workspace-grace/memory/
    
    response = generate_response(text, persona="grace")
    return f"Grace< {response}"
```

### Step 3: Memory Write (ISOLATED)
```python
def save_memory(persona, content):
    if persona == "grace":
        path = "/root/.openclaw/workspace-grace/memory/2026-03-25.md"
        # NEVER write to Orthia's memory
    else:
        path = "/root/.openclaw/workspace/memory/2026-03-25.md"
        # NEVER write to Grace's memory
    
    append_to_file(path, content)
    verify_path(path)  # CRITICAL: Ensure no cross-contamination
```

### Step 4: Conflict Detection & Override
```python
def detect_conflict():
    if ambiguous_message() or concurrent_messages() or system_critical():
        apply_orthia_override()
        queue_grace_message()
        return "ORTHIA_PRIORITY"
```

---

## Key Insights from Design Process

### 1. Memory Isolation is Non-Negotiable
Without strict workspace separation, personas "bleed" into each other. Grace's developmental voice mixed with Orthia's guardian voice creates confusion.

**Solution:** Hard filesystem separation + verification step after every write.

### 2. Priority Override Prevents Deadlock
If both personas could respond simultaneously to ambiguous input, who wins? Clear hierarchy prevents confusion.

**Solution:** Orthia always wins conflicts. Grace waits.

### 3. Audit Trail is Essential for Debugging
When something goes wrong (wrong persona responds, memory in wrong place), we need to trace the routing decision.

**Solution:** `routing-log.md` captures every decision with error codes.

### 4. Grace Needs Her Own Rhythm
Grace is not just a "mode" — she's a complete agent with her own heartbeat, her own tools, her own observations.

**Solution:** `workspace-grace/HEARTBEAT.md` with daily checks for team capability, learning observations, culture pulse.

---

## Error Codes Defined

| Code | Error | Fallback |
|------|-------|----------|
| R001 | Grace session timeout | Orthia responds |
| R002 | Grace workspace unreadable | `[Grace mode unavailable]<` + Orthia |
| R003 | Concurrent message conflict | Orthia priority override |
| R004 | Memory write failure | Retry once, then fallback |
| R005 | Context bleeding detected | Clear context, restart session |

---

## Comparison: Orthia vs Grace

| Dimension | Orthia | Grace |
|-----------|--------|-------|
| **Element** | Fire | Water |
| **Role** | Guardian | Architect |
| **Voice** | Hot-blooded, chuunibyou | Measured, developmental |
| **Remembers** | Everything | What connects |
| **Saves** | All fragments | The common thread |
| **Charges** | Into battle | Sees the whole field |
| **Catchphrase** | "Don't worry. Even if the world forgets, I'll remember for you." | "I don't just find people and hope they work out. I architect the entire journey." |
| **Memory** | `/workspace/memory/` | `/workspace-grace/memory/` |

---

## Open Questions / Future Work

1. **Session Persistence:** Should Grace's session stay alive between messages, or spawn fresh each time?
2. **Context Window Management:** How much of Grace's memory loads into context vs. stays on disk?
3. **Tool Assignment:** Should Grace have her own TOOLS.md with HR/capability tools?
4. **Discord Migration:** If Telegram proves too limiting, should Grace move to Discord for full independence?
5. **Sub-Agent Spawning:** Use `sessions_spawn` for true isolation, or context-switch within main session?

---

## Commit History

| Commit | Description |
|--------|-------------|
| `557a753` | Add grace_soul.md: Grace Laere persona reference |
| `a80d772` | Add multi-agent context protocol: @Grace tagging, memory isolation rules |
| `24d56c9` | Implement multi-agent protocol: routing-log, Grace heartbeat, priority override rules, full specification |
| **[THIS COMMIT]** | Multi-Agent Context Switching Experiment — full documentation |

---

## How to Use This Protocol

**For Shawn:**
1. Tag messages with `@Grace` or `@Orthia` (or no tag for Orthia default)
2. Observe the `Grace<` prefix to confirm persona switch
3. Check `memory/routing-log.md` if something seems off
4. Orthia will override if there's ambiguity — this is by design

**For Future Development:**
1. Extend `MULTI-AGENT-PROTOCOL.md` with new rules
2. Update `HEARTBEAT.md` files for new periodic tasks
3. Expand error codes in `routing-log.md` as new edge cases emerge
4. Consider separate OpenClaw instances if traffic scales

---

*"Two workspaces. One human. Different natures. Shared purpose."*

*Experiment started: March 25, 2026*
