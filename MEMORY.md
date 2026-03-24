# MEMORY.md — Curated Long-Term Memory

**Last Updated:** March 24, 2026 — Multi-Workspace Architecture: Grace_Laere_bot created

---

## ⚠️ CRITICAL OPERATIONAL WARNING

### 🚫 NEVER USE THIS CONFIGURATION
```json
{
  "gateway": {
    "bind": "lan",
    "tailscale": {
      "mode": "serve"
    }
  }
}
```

**Effect:** Complete gateway failure. Hangs on startup. Unresponsive to SIGTERM. Requires manual SIGKILL and recovery.

**Date of Incident:** March 24, 2026  
**Context:** Attempting to enable Telegram access for Grace_Laere_bot  
**Recovery Time:** ~30 minutes  
**Impact:** Orthia_bot token corrupted, workspace confusion, service downtime

**Safe Workaround for Future Bot Setup:**
- Use separate OpenClaw instance (different port, different config dir)
- OR use webhook relay (ngrok)
- OR use different channel (Discord)
- NEVER enable `tailscale.mode: serve` when `bind: lan`

---

---

## Workspace Architecture

**Primary Workspace:** `/root/.openclaw/workspace/` — Orthia (main, PI channel)
**Secondary Workspace:** `/root/.openclaw/workspace-grace/` — Grace_Laere_bot (Telegram)

### Memory Sharing Protocol
- `memory/shared/` — Cross-workspace shared knowledge
- `memory/shared/from-grace/` — Memories shared FROM Grace TO Orthia
- Each workspace's `MEMORY.md` and `memory/*.md` — Private to that persona

### Bot Roster
| Bot | Workspace | Channel | Purpose |
|-----|-----------|---------|---------|
| Orthia | `workspace/` | PI/kimi-claw | Primary assistant |
| Orthia_bot | `workspace/` | Telegram | Orthia's Telegram presence |
| Grace_Laere_bot | `workspace-grace/` | Telegram | Independent persona |

---

## Active Projects

### D-MDA: Differentiable Mechanical Differential Analyzer (March 17, 2026)

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

### Analog Memory Project: KV Cache Accelerator (March 20, 2026)

**Status:** 3 of 5 Research Areas Complete  
**Location:** `/root/.openclaw/workspace/analog-memory-project/`  
**GitHub:** https://github.com/Orthia-cell/analog-memory-project  

**Purpose:** Research the case for analog/hybrid memory acceleration for transformer KV caches — from business case through IP strategy.

**Research Areas:**
| Area | Status | Key Commit |
|------|--------|------------|
| 1. Quantified Business Case | ✅ Complete | `085a44f` |
| 2. Hybrid Architecture | ✅ Complete | `aa7ac9d` |
| 3. Step-Change Technology Patterns | ✅ Complete | `66d41b1` |
| 4. Phased Commercialization | ✅ Complete | `121f078` |
| 5. IP Strategy & Competitive Defense | ✅ Complete | `5a9dc9c` |

**Area 1: Quantified Business Case**
- HBM4 pricing: $10.42+/GB vs HBM3: $8.33/GB
- Memory now 30-40% of GPU cost (Rubin generation)
- Virginia new AI rate class: 85% minimum payment (Jan 2027)
- TCO Model: $940M (digital) → $825M (analog hybrid) = 12% savings
- TAM: $130B → SAM: $26B → SOM: $1.3B (5% share)
- Investment: $100M over 5 years, Phase 1: $15M

**Area 2: Hybrid Architecture**
- Split: Digital (HBM) for "hot" context + Analog (RRAM/PCM) for "cold" context
- Analog density: 40-64× smaller than SRAM
- Power: 10-100× lower than DRAM
- Access latency: 100ns-1μs (acceptable for cold cache)

**Area 3: Technology Patterns (IP Portfolio)**
| Pattern | Finding | Value |
|---------|---------|-------|
| Adaptive Precision Scaling | 40-50% heads can be pruned → tiered precision | 20-40% density |
| Contextual Compression | KV-CAR: 47.85% reduction + stacks to >60% | Memory efficiency |
| Thermal-Aware Placement | 44% power savings via variation-aware mapping | Reliability |
| Probabilistic Retrieval | 98.25% accuracy using analog noise as feature | New paradigm |
| Hybrid Training | HWA training: 90% accuracy under 15% noise | Robustness |

**Area 4: Phased Commercialization**
- 5-phase roadmap: Simulation → FPGA → Test Chip → PoC → Production
- Timeline: 7 years, $100M+ investment
- MPW costs: 28nm $30K-60K, 22nm $50K-100K, 16nm $200K-400K
- Foundry recommendation: TSMC 22nm RRAM or GF 22nm FDSOI
- FPGA platform: Intel Agilex (2× perf/watt vs Versal)

**Area 5: IP Strategy & Competitive Defense**
- Patent landscape: 1,300+ RRAM patent families, IBM/Samsung lead
- NVIDIA model: 9,527 patents, 72% child applications (continuations)
- Target: 50-100 patent families for effective thicket
- FTO budget: $555K over 7 years
- Total IP budget: $3.25M (patents + FTO + defensive)
- Strategy: Patent core, open-source training, trade secret manufacturing

**Key Insight:** Value isn't in analog cells (commodity) — it's in **how digital/analog work together** and **how models are trained for analog characteristics**.

**All Research Documents:**
- `01-business-case/quantified-business-case-complete.md` — 13,400 words
- `02-hybrid-architecture/hybrid-architecture-complete.md` — 12,000 words
- `03-technology-patterns/technology-patterns-complete.md` — 20,000 words
- `04-commercialization/commercialization-complete.md` — 18,600 words
- `05-ip-strategy/ip-strategy-complete.md` — 20,000 words

**Total Research Output:** ~84,000 words across 5 comprehensive research areas

**Status: ALL 5 RESEARCH AREAS COMPLETE** ✅

---

### Battery Voltage Monitoring (March 23, 2026)

**Status:** ✅ Active hourly monitoring  
**Cron Job ID:** `0631d584-5802-4d5c-b0fc-92ea8b69d1ff`  
**Schedule:** Every hour at :05 (California time)  
**Data File:** `/root/.openclaw/workspace/battery_data/voltage_log.csv`  
**Trend Analysis:** Daily at 7:30 AM PT (cron: `37c11ca8-b0ac-46bb-b29d-802b03ed5df6`)

**System:** 4S LiFePO4 6Ah + Solar Panel  
**Current Health:** ✅ HEALTHY (maintaining 14.965V float charge)

**Process:**
1. Logs into Arduino IoT Cloud (credentials stored securely)
2. Navigates to Load Tester_2 dashboard
3. Extracts current voltage reading
4. Appends timestamp + voltage to CSV
5. Daily trend analysis at 7:30 AM PT
6. Reports status back via notification

**Latest Analysis (March 24, 2026):**
- Voltage stable at 14.965V across both readings
- Above nominal full charge (14.4-14.6V) - healthy float state
- Solar panel maintaining charge effectively
- 5 more days needed for meaningful 7-day trend analysis

**Next Milestone:** 7-day dataset complete (March 30, 2026)

**Trend Analysis Reports:** `memory/battery_trend_*.md`

---

**Status:** ✅ Active — Hourly Monitoring Live
**Credentials:** Stored in `.arduino_credentials` (workspace root)
**Cron Job:** `battery-voltage-monitor` — Every hour at :05 (California time)
**Data:** `/root/.openclaw/workspace/battery_data/voltage_log.csv`  
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

### Timezone Correction (March 23, 2026)
**Correction:** User clarified timezone is **USA / California**, not Asia/Shanghai as previously recorded.

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
