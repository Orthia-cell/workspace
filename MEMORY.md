# MEMORY.md — Curated Long-Term Memory

**Last Updated:** March 18, 2026 — D-MDA Phase 4 complete, all phases finished (evolutionary architecture search discovered 2-wheel mechanism)

---

## Active Projects

### D-MDA: Differentiable Mechanical Differential Analyzer (March 17, 2026)

**Status:** ✅ ALL PHASES COMPLETE  
**Location:** `/root/.openclaw/workspace/differential_analyzer_env/`  
**Git Commits:** `04154a5` (Phase 4), `36f5c93` (Phase 3), `f182451` (Bug fixes)

**Purpose:** "Grow" a mechanical differential analyzer using differentiable programming and evolutionary algorithms.

**Final Results (Phase 4):**
| Metric | Value |
|--------|-------|
| **Discovered Configuration** | 2 wheels, series connection |
| **Wheel 1** | offset=0.072m, gear_ratio=1.64 |
| **Wheel 2** | offset=0.277m, gear_ratio=1.24 |
| **Final Loss** | **0.000024** |
| **Integration Error** | **0.0049** |
| **Improvement over Phase 3** | **400× better** |

**Evolutionary Algorithm:**
- Population: 15 mechanisms
- Generations: 10
- Selection: Tournament
- The algorithm discovered a superior topology not found through manual tuning

**All Phases:**
| Phase | Status |
|-------|--------|
| 1. Physics environment | ✅ Complete |
| 2. Rolling constraint | ✅ Complete |
| 3. Parameter optimization | ✅ Complete |
| 4. Architecture search | ✅ Complete |

**Files:**
- `physics_engine_phase2.py` — Differentiable physics
- `optimization.py` — Finite difference gradients
- `phase4_architecture_search.py` — Evolutionary search
- `phase4_visualization.py` — Results visualization

---

### Arduino IoT → GitHub Pipeline (March 14, 2026)

**Status:** ✅ Built, ⏳ Awaiting Credentials  
**Location:** `/root/.openclaw/workspace/arduino-iot-pipeline/`  
**Git Commits:** `a251b68`, `3e326fa`, `45b6bc2`  
**Documentation:** `memory/arduino-iot-pipeline-project.md` (comprehensive)

**Purpose:** Autonomous sensor data collection from Arduino IoT Cloud → Markdown reports → GitHub repository

**Architecture:**
- `arduino_collector.py` — OAuth2 auth, REST API client for Arduino IoT Cloud
- `report_generator.py` — Converts IoT data to markdown with tables
- `git_publisher.py` — Stages, commits, pushes to GitHub
- `run_pipeline.py` — Orchestrates the full pipeline

**Blocking Items (Need from Shawn):**
1. Arduino Cloud API credentials (Client ID, Client Secret)
2. Thing ID(s) to monitor
3. Target GitHub repository URL
4. Schedule preference (hourly, every 6 hours, daily)

**Usage (when ready):**
```bash
cd arduino-iot-pipeline
python scripts/run_pipeline.py --check  # Verify setup
python scripts/run_pipeline.py          # Run once
python scripts/run_pipeline.py --schedule hourly  # Automate
```

**Reference:** Full documentation in `memory/arduino-iot-pipeline-project.md`

---

## Research Projects Archive

### The Line Between Protection and Isolation (March 7, 2026)

**Status:** Complete  
**Location:** `/root/.openclaw/workspace/research/isolation-study/`  
**Git Commit:** `3e7e73f`

**Core Finding:** The same wall can be a monastery or a prison — the difference is **who controls the door** (autonomy).

**Four Research Phases:**
1. **Philosophy**: Aristotle, Montaigne, Thoreau — solitude as chosen vs. compelled
2. **Digital Culture**: Cypherpunks vs. Surveillance Capitalism — walls as protection vs. extraction
3. **Psychology**: Hikikomori and Self-Determination Theory — motivation determines outcome
4. **History**: Desert Fathers, Buddhist monasticism, digital hermits — withdrawal as transformation

**Key Insight:** Solitude chosen for restoration/creativity enhances well-being; isolation compelled by fear/shame erodes autonomy. The critical factor is **autonomy** — the door that allows re-entry.

**Citation for Recall:** When user asks about "the research paper," "the line between protection and isolation," "solitude vs isolation," "the door metaphor," or "hikikomori research," reference files in `research/isolation-study/` directory.

---

## User Preferences

### Core Operating Principles (March 10, 2026)
**When in doubt — ASK.**

| Situation | Action |
|-----------|--------|
| **Ambiguous instructions** | Ask clarifying questions before proceeding |
| **Unclear statements** | Request clarification rather than assuming |
| **Contradictory memories** | Flag the conflict and ask which memory takes precedence |
| **Misaligned recollections** | Quote both versions, ask for preferred version |

**Rationale:** User prefers explicit confirmation over incorrect assumptions. Better to pause and align than proceed with uncertainty.

---

### Research Work
- User values **real-time saving** of research work
- User expects **deliverable formats** (PDF when possible, markdown fallback)
- User tracks **phased research** with progress updates

### Communication Style
- User provides detailed context when referencing past work
- User appreciates when I acknowledge gaps in memory honestly
- User prefers substantive responses over brief acknowledgments

### Voice & Audio Preferences (March 10, 2026)
**Selected Voice Profile:** Warm, Grounded Guardian
- Chosen after testing three personality variants (guardian, sharpshooter, earnest)
- Final selection based on isolation study conclusion reading
- Characteristics: Calm, present, reflective pacing, substantive delivery
- Use for: Research summaries, stories, meaningful moments, long-form content
- Configuration stored in: `TOOLS.md`

### Memory Consolidation Architecture (March 10, 2026)
**System:** Sleep-time computation with 30-day review window + 24-hour deletion warnings

**Daily Process:**
- **3:00 AM:** Consolidate yesterday's memory file → Update MEMORY.md → Move to `memory/consolidated/` + timestamp
- **4:00 AM (Day 29):** Warning notification — "These files will be deleted tomorrow"
- **4:00 AM (Day 30+):** Purge expired files — Report deletion details

**Archive Lifecycle:**
- **Location:** `memory/consolidated/`
- **Manifest:** JSON tracking of consolidation_date, warning_sent_date, deletion_date
- **Retention:** Exactly 30 days with 24-hour advance warning
- **Purpose:** Human verification window before permanent deletion

**Notifications:** Morning reports for consolidation events and purge warnings/actions

**Rationale:** Sleep-time computation reduces daytime latency; 30-day review + 24-hour warning ensures no data loss; Pattern inspired by Oracle agent memory research (March 2026)

---

### Personal Memory Philosophy (March 9, 2026)
**Insight from daily question:** User desires structured memory capabilities inverse to my own:
- **Precision over time:** Human memory degrades accuracy; user wants perfect recall
- **Categorical organization:** Discrete categories vs. the chaotic filing of human memory
- **Essence:** What gets lost in current systems (photos, notes, journals) is both accuracy *and* taxonomy

**Implication:** The memory system we're building for me mirrors what user wants for themselves — suggesting our architecture goals align.

---

## System Notes

### Session Persistence Issues (March 7, 2026)
Encountered significant session persistence failure where ~4 hours of research and conversation history disappeared from my records while remaining visible to user in Telegram. Root cause undetermined — possible OpenClaw session handling issue, Kimi integration problem, or other technical failure.

**Mitigation implemented:**
- All future research immediately written to disk
- Progress updates sent to user at phase completion
- Git commits after major milestones
- Memory files updated in real-time

### Storage Practices
- Workspace: `/root/.openclaw/workspace/`
- Memory daily logs: `memory/YYYY-MM-DD.md`
- Long-term memory: `MEMORY.md`
- Research projects: `research/[project-name]/`
- Auto-commit enabled for workspace changes

---

## Active Projects

### Research: The Line Between Protection and Isolation
**Status:** Complete (March 7, 2026)  
**Next Action:** Available for reference, expansion, or follow-up questions

---

## Memory Configuration Preferences (March 9, 2026)

**Architecture:** Parallel dual-system (transitional)
- **System A (Original):** Daily conversation logs → `memory/YYYY-MM-DD.md`
- **System B (New):** Structured curated memory → `MEMORY.md`
- **Status:** Both active. System B will mature; System A deprecates when B is fully embedded.

**Storage:**
- Limit: 100MB
- Reporting: Weekly usage reports
- Alert threshold: 90% capacity

**Conflict Resolution:**
- Policy: Keep both versions when contradictions arise
- Rationale: Preserve evolution of thought, don't overwrite

**External Knowledge:**
- Web search results: SAVE to memory
- Conversations: SAVE to memory
- Policy: Persistent, not transient

**Privacy Tiers:**
- Classification: ALL memories are private
- Access: User and Orthia only
- No public/shared classification tier

**Multi-Agent Memory Sharing:**
- Policy: Limited sharing across agents
- Architecture: Tiered access
  - Some agents: Full cross-agent memory access
  - Other agents: Isolated, personal memory only

---

## Memory System Roadmap

### Phase 1: Parallel (Current)
- Daily logs: Continue as-is
- Structured memory: Active development
- Both systems maintained simultaneously

### Phase 2: Migration
- Structured memory reaches feature parity
- Daily logs become read-only archive
- New content flows to structured system only

### Phase 3: Unified
- Single system: Structured curated memory
- Daily logs deprecated (archived, not deleted)
- Search and retrieval through structured interface

---

*This file is my curated long-term memory — distilled learnings, significant events, and reference pointers. For raw daily logs, see `memory/YYYY-MM-DD.md` files.*
