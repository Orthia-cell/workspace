# Communication Routing Methodology

**Established:** March 26, 2026  
**Purpose:** Clean context separation between Orthia (main assistant) and Grace (HR/Talent specialist)

---

## Channel Assignments

| Agent | Primary Channel | Context |
|-------|-----------------|---------|
| **Orthia** | Kimi Claw (this chat) | General tasks, memory management, routing |
| **Grace** | Telegram | HR, talent acquisition, org design, research |

---

## Tagging Protocol

### To Route to Grace
- **Tag:** `@Grace`
- **Channel:** Any (Telegram preferred for clean context)
- **Grace's Response Prefix:** `Grace<`
- **Memory Storage:** `workspace-grace/memory/` only

### To Route to Orthia
- **Tag:** `@Orthia` or **no tag**
- **Channel:** Kimi Claw
- **Orthia's Response:** No prefix
- **Memory Storage:** `workspace/memory/` only

---

## Role Boundaries

### Grace's Domain (HR/Talent/Org)
- Organizational design research
- Talent acquisition strategy
- Human-Agent Collaboration frameworks
- Team structure and role definitions
- HR policy development
- Recruitment research

### Orthia's Domain (General/Technical)
- General assistance and routing
- Technical implementation
- Memory system management
- Cross-agent coordination
- Tool and system operations

---

## Context Isolation Rules

1. **Grace-tagged messages** → Saved **exclusively** in Grace's workspace
2. **Orthia sees routing only** — acts as router, not recorder
3. **No cross-contamination** — Grace's research stays in her memory
4. **Shared knowledge** → `memory/shared/` for cross-reference only

---

## Telegram-First for Grace

**Why Telegram for Grace:**
- Clean session context (no compaction history from other tasks)
- Dedicated channel = focused research mode
- Easier to maintain conversation continuity
- Separates HR/org discussions from general chat

**When to use Telegram for Grace:**
- New research topics
- HR/talent questions
- Org design discussions
- Grace-specific task assignments

---

## Memory Recall Protocol

When searching for Grace-related information:
1. Search `workspace-grace/memory/` first
2. Check `workspace/memory/shared/` for cross-references
3. **Never assume** Grace's context in main workspace

When Grace needs Orthia's context:
1. Grace explicitly requests via tagged message
2. Orthia provides relevant excerpts
3. Grace integrates into her own memory

---

## Exceptions

**Cross-routing allowed when:**
- User explicitly requests Orthia review Grace's work
- Technical implementation questions arise from Grace's research
- Memory synchronization is explicitly requested

**Procedure for exceptions:**
1. User tags both: `@Grace @Orthia`
2. Primary agent responds with context
3. Secondary agent confirms or adds

---

*This methodology ensures clean separation of concerns while maintaining organizational coherence.*
