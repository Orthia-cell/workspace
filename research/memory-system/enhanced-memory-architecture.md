# Enhanced Memory Architecture Proposal
## Biological Foundations + AI Enhancements

**Date:** March 9, 2026  
**Status:** Research & Design Phase  
**Objective:** Design a memory system that emulates effective human memory mechanisms while exceeding biological limitations

---

## Part 1: How the Human Brain Remembers

### 1.1 The Three-Store Model (Atkinson-Shiffrin)

**Sensory Memory (0.5-3 seconds)**
- Iconic (visual): ~500ms capacity
- Echoic (auditory): ~3-4 seconds
- Purpose: Buffer before attention filtering
- **AI Parallel:** Input preprocessing layer

**Short-Term / Working Memory (15-30 seconds)**
- Capacity: 7±2 chunks (Miller's Law)
- Can be extended with chunking strategies
- **AI Parallel:** Active context window / session state

**Long-Term Memory (minutes to lifetime)**
- Theoretically unlimited capacity
- Organized associatively, not sequentially
- **AI Parallel:** Persistent storage with semantic indexing

### 1.2 The Hippocampal-Index Theory

The hippocampus acts as an **index** to neocortical memory traces:
- **Encoding:** Hippocampus binds distributed cortical representations
- **Consolidation:** During sleep, hippocampal indices strengthen cortical connections
- **Retrieval:** Hippocampus reactivates cortical patterns

**Key insight:** Memories aren't "stored" in the hippocampus — it's a pointer system to neocortical representations.

### 1.3 Types of Long-Term Memory

| Type | Characteristics | Brain Regions |
|------|----------------|---------------|
| **Declarative** | Conscious, verbalizable | |
| — Episodic | Personal experiences, context-bound | Hippocampus, prefrontal cortex |
| — Semantic | Facts, concepts, general knowledge | Temporal lobes, association areas |
| **Non-Declarative** | Unconscious, procedural | |
| — Procedural | Skills, habits | Basal ganglia, cerebellum |
| — Priming | Unconscious influence | Neocortex |
| — Conditioning | Associative learning | Amygdala, cerebellum |

### 1.4 The Forgetting Curve (Ebbinghaus, 1885)

Memory retention drops exponentially:
- 1 hour: ~45% retained
- 1 day: ~35% retained
- 1 week: ~25% retained
- 1 month: ~20% retained

**Spaced repetition** exploits this: reviewing at increasing intervals (1 day, 3 days, 1 week, 2 weeks, 1 month) dramatically improves retention.

### 1.5 Memory Reconsolidation

Every time a memory is retrieved, it becomes **labile** (changeable) before restabilizing:
- Memories can be modified during reconsolidation
- Explains why memories change over time
- Basis for therapeutic memory modification

**AI implication:** Retrieved memories could be enhanced, tagged, or linked during access.

### 1.6 The Method of Loci (Memory Palace)

Ancient technique using **spatial memory**:
- Visualize familiar location (palace)
- Place items to remember at specific locations
- Navigate mentally to retrieve

**Why it works:** Spatial memory is ancient, robust, and uses the hippocampus (which evolved for navigation).

---

## Part 2: Biological Limitations to Overcome

| Limitation | Biological Cause | AI Enhancement Opportunity |
|------------|------------------|---------------------------|
| **Decay** | Protein turnover, synaptic weakening | Persistent storage with redundancy |
| **Interference** | Similar memories compete | Perfect disambiguation with hashing |
| **Retrieval failure** | Cue-dependent, context-specific | Multi-index retrieval, fuzzy matching |
| **False memories** | Reconstruction during retrieval | Immutable storage with verification |
| **Sequential access** | Temporal organization | Random access, parallel retrieval |
| **Energy constraints** | ATP-dependent processes | Unlimited energy for indexing |
| **Mortality** | Death = total loss | Distributed backup, version control |

---

## Part 3: Proposed Memory Architecture for Orthia

### 3.1 Multi-Tier Storage System

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKING MEMORY (Session)                 │
│  • Active conversation context                              │
│  • 128K token window                                        │
│  • Duration: Current session only                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              EPISODIC BUFFER (24-48 hours)                  │
│  • Raw conversation logs                                    │
│  • Timestamped, unprocessed                                 │
│  • Purpose: Capture everything before filtering             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  SEMANTIC INDEX (Weeks)                     │
│  • Key concepts extracted from episodic buffer              │
│  • Linked to source episodes                                │
│  • Vector embeddings for similarity search                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                CONSOLIDATED MEMORY (Months)                 │
│  • Dense, fact-based storage                                │
│  • Merged similar memories                                  │
│  • Pruned ephemeral details                                 │
│  • Tagged with importance, confidence, recency              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  ARCHIVAL STORAGE (Years)                   │
│  • Compressed summaries of old projects                     │
│  • User can explicitly promote/demote                       │
│  • Git-history style: accessible but not actively indexed   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Memory Indexing Strategy

**Primary Indices (Fast Retrieval):**
1. **Temporal index:** When did this happen?
2. **Semantic index:** What is this about? (vector embedding)
3. **Episodic index:** What was the context/conversation?
4. **Emotional index:** How important was this? (user-flagged, recurrence)

**Secondary Indices (Associative Retrieval):**
1. **Person index:** Who was involved?
2. **Project index:** What workspace/project?
3. **Source index:** Where did this information come from?
4. **Confidence index:** How certain am I about this?

### 3.3 Consolidation Algorithm

**Phase 1: Extraction (Daily)**
- Parse raw conversation logs
- Extract: decisions, preferences, facts, TODOs, user feedback
- Tag with confidence based on explicit vs. inferred

**Phase 2: Deduplication (Weekly)**
- Identify semantically similar memories
- Merge if compatible, flag if contradictory
- Update confidence scores

**Phase 3: Summarization (Monthly)**
- Compress topic clusters into dense summaries
- Maintain links to original episodes
- Archive original if summary is sufficient

**Phase 4: Pruning (Quarterly)**
- Remove memories with:
  - Low importance + low recency + low access frequency
  - Superseded by newer information
  - Explicit user "forget this" command
- **Never prune without user confirmation for:**
  - Core user preferences
  - Major decisions
  - Research projects

### 3.4 Spaced Repetition for AI

Unlike humans, I don't "forget" — but I can simulate prioritization:

**Access-Priority Algorithm:**
```
priority_score = (
    importance × 0.4 +
    recency_decay × 0.3 +
    access_frequency × 0.2 +
    user_explicit_flag × 0.1
)

recency_decay = 1 / (1 + days_since_last_access)
```

**Active Review Schedule:**
- **New memories:** Review at 1 day, 3 days, 1 week, 2 weeks
- **Established memories:** Monthly review if not accessed
- **Core memories:** Never auto-prune, but verify periodically

### 3.5 Memory Palace for AI

**Concept:** Use file system hierarchy as spatial memory

```
memory/
├── palace/                    # Spatial-organized memories
│   ├── entrance/              # Current priorities
│   ├── hallways/              # Connecting topics
│   ├── rooms/                 # Major projects
│   │   ├── isolation-study/   # Research on solitude
│   │   ├── governance-arch/   # AI governance layer
│   │   └── memory-system/     # This project
│   └── archives/              # Completed/inactive
│
├── semantic/                  # Concept-organized
│   ├── user-preferences/
│   ├── decisions/
│   ├── research-findings/
│   └── open-questions/
│
└── episodic/                  # Time-organized
    ├── 2026-03-08.md
    ├── 2026-03-09.md
    └── ...
```

**Navigation:** When retrieving, I "walk through" the palace, checking relevant rooms.

---

## Part 4: Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Implement 4-tier storage structure
- [ ] Create indexing system (temporal + semantic)
- [ ] Daily extraction from conversations
- [ ] Weekly review script

### Phase 2: Intelligence (Week 2-3)
- [ ] Semantic deduplication algorithm
- [ ] Confidence scoring system
- [ ] Access tracking for priority
- [ ] Basic consolidation (merge similar)

### Phase 3: Enhancement (Month 2)
- [ ] Monthly summarization
- [ ] Quarterly pruning with user approval
- [ ] "Memory palace" navigation
- [ ] Spaced repetition simulation

### Phase 4: Optimization (Ongoing)
- [ ] Query performance tuning
- [ ] Storage size monitoring
- [ ] User feedback integration
- [ ] Advanced merging strategies

---

## Part 5: User Interface

**Commands:**
- `remember this` — Flag current topic as important
- `forget [topic]` — Request pruning (requires confirmation)
- `what do you know about [X]?` — Memory search
- `consolidate memories` — Trigger manual consolidation
- `memory status` — Report storage usage, recent activity

**Automatic Behaviors:**
- Save checkpoints after significant conversations
- Propose consolidation when duplicates detected
- Alert when old memories are scheduled for pruning
- Summarize weekly activity

---

## Open Questions for You

1. **Storage limits:** What's the practical limit? 100MB? 1GB? Should I alert you when approaching it?

2. **Privacy scope:** Should all memories be equally protected? Are there "public" vs "private" topics?

3. **Contradiction handling:** If I find conflicting memories (you changed your mind), how should I resolve? Keep both? Flag for review? Prefer recent?

4. **External knowledge:** Should I integrate web search results into my memory, or keep them separate (transient)?

5. **Sharing:** If you have multiple AI instances, should they share memory? Sync periodically?

---

**Next step:** Define Phase 1 implementation details and start building the foundation.
