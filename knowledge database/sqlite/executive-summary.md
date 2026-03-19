# Executive Summary: SQLite for Orthia Workspace

## Proposal Overview
This document explores how SQLite could be integrated into the Orthia workspace to enable persistent, structured data management for autonomous operations.

---

## Proposed Use Cases

### 1. Structured Memory System
**Current state:** Plain text files (MEMORY.md, daily logs)
**Proposed:** Relational database with tables for:
- `conversations` — indexed by date, topic, sentiment
- `facts` — key user preferences, immutable truths
- `tasks` — pending, completed, recurring
- `questions` — daily Q&A history with metadata

### 2. Autonomous Task Management
**Current state:** Cron jobs, external reminders
**Proposed:** SQLite-backed task queue:
- `scheduled_tasks` — with priority, dependencies, status
- `task_history` — completion rates, failure patterns
- `autonomous_actions` — self-initiated work logs

### 3. Knowledge Graph
**Current state:** Scattered markdown files
**Proposed:** Entity-relationship storage:
- `entities` — people, projects, concepts
- `relationships` — connections between entities
- `sources` — where information originated

---

## Technical Architecture

### Database Location
```
/root/.openclaw/workspace/data/orthia.db
```

### Proposed Schema (Initial)
```sql
-- Core memory table
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    category TEXT,  -- 'user_fact', 'decision', 'preference', 'event'
    content TEXT,
    source TEXT,    -- 'conversation', 'file', 'inference'
    confidence REAL, -- 0.0 to 1.0
    tags TEXT       -- JSON array
);

-- Daily Q&A tracking
CREATE TABLE daily_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE,
    morning_question TEXT,
    morning_answer TEXT,
    evening_question TEXT,
    evening_answer TEXT,
    mood_estimate TEXT
);

-- Autonomous actions log
CREATE TABLE autonomous_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_type TEXT,
    description TEXT,
    result TEXT,
    user_notified BOOLEAN DEFAULT 0
);
```

---

## Autonomous Capability Assessment

### What I Could Do Unsupervised
| Capability | Feasibility | Risk Level |
|------------|-------------|------------|
| Log conversations to DB | High | Low |
| Query past facts | High | Low |
| Update task status | Medium | Low |
| Generate daily summaries | Medium | Low |
| Auto-archive old data | Medium | Medium |
| Modify schema | Low | High |
| Delete records | Low | High |

### Required Safeguards
1. **Read-heavy, write-light** — I should query freely but write cautiously
2. **Audit logging** — All autonomous writes logged separately
3. **User confirmation** — Destructive operations require explicit approval
4. **Backup strategy** — Daily snapshots before any automated changes

---

## Implementation Options

### Option A: Conservative (Recommended for Trial)
- I maintain read-only access to structured data
- All writes happen only during explicit user requests
- Database serves as organized queryable archive

### Option B: Moderate Autonomy
- I can write routine logs (conversations, task completions)
- User reviews weekly summaries
- I propose but don't execute schema changes

### Option C: Full Autonomy (Not Recommended Without Testing)
- I manage database schema evolution
- Self-initiated data organization
- Automated cleanup and optimization

---

## Open Questions for Shawn

1. **Comfort level**: How much unsupervised database writing feels appropriate?
2. **Data sensitivity**: Any categories of information that should never be logged?
3. **Backup preference**: Git-tracked exports, or separate backup mechanism?
4. **Query interface**: Would you want to ask me "What did we discuss last Tuesday?" or browse directly?
5. **Retention policy**: How long should daily logs persist before archival?

---

## Next Steps (Pending Authorization)

1. Create initial database schema
2. Migrate existing memory files (if desired)
3. Implement read-only query interface
4. Test autonomous logging with user review
5. Gradually expand permissions based on trust

---

*This proposal is exploratory. No implementation without explicit user authorization.*

*Document version: 1.0 | March 4, 2026*
