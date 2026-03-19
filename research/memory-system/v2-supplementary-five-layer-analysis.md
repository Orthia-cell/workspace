# Supplementary Technical Analysis: Five-Layer Cognitive Memory Architecture
## Integration with Orthia's Trust-Metric Governance System

**Author:** Orthia (Kimi Claw)  
**Date:** March 10, 2026  
**Supplementary to:** V2 Architecture Analysis (v2-architecture-analysis.md)  
**Subject:** Five-Layer Cognitive Memory Architecture Assessment  

---

## Abstract

This paper analyzes a five-layer cognitive memory architecture (Working → Episodic → Semantic → Procedural → Meta/Governance) in the context of Orthia's existing memory infrastructure and proposed trust-metric governance system. The analysis reveals that the five-layer model provides the "cognitive substrate" referenced in the original critique, offering a principled framework for transforming Orthia from a document-based storage system into a true cognitive architecture. Key findings: (1) The five layers map cleanly onto Orthia's current two-tier model while providing necessary expansion paths; (2) Layer 5 (Meta/Governance) directly enables trust-metric integration; (3) The architecture solves the "retrieval logic" gap identified in the original critique by defining clear transformation pathways between layers; (4) Implementation can be phased, with Layers 1-3 addressed in V2.1 and Layers 4-5 in V2.2.

---

## 1. Introduction: From Storage to Cognitive Substrate

The original critique of Orthia's memory system concluded with a tantalizing offer: a "5-layer memory architecture used in advanced cognitive agent research that would fit beautifully with the behavioral structures and trust-metric governance system you're designing. It would turn your memory model into something closer to a true cognitive substrate."

That architecture has now been provided. It describes a hierarchical model drawn from cognitive science and modern agent frameworks:

```
Layer 5 – Meta / Value / Governance Memory  (years)
Layer 4 – Procedural Memory                  (months)
Layer 3 – Semantic Memory                    (days to months)
Layer 2 – Episodic Memory                    (minutes to days)
Layer 1 – Working Memory                     (seconds to minutes)
```

Each layer operates at different time scales, abstraction levels, and retrieval mechanisms. Together they form what the architecture calls a "continuous pipeline from raw perception to long-term intelligence."

This paper assesses how this five-layer model integrates with:
1. Orthia's current two-tier architecture (Raw → Curated)
2. The proposed V2 enhancements (confidence scoring, associative memory, structured domains)
3. The trust-metric governance system referenced in the critique

---

## 2. Mapping the Five Layers to Orthia's Current Architecture

### 2.1 Current State vs. Five-Layer Model

| Orthia V1.0 | Five-Layer Model | Gap Analysis |
|-------------|------------------|--------------|
| Conversation context (in-session) | Layer 1 — Working Memory | ✓ Covered |
| memory/YYYY-MM-DD.md (daily logs) | Layer 2 — Episodic Memory | ✓ Covered |
| MEMORY.md (curated facts) | Layer 3 — Semantic Memory | Partial (lacks knowledge graph) |
| Implicit tool usage patterns | Layer 4 — Procedural Memory | ✗ Missing |
| User preferences, project goals | Layer 5 — Meta/Governance | ✗ Missing (critical) |

**Assessment:** Orthia currently implements approximately 2.5 of 5 layers:
- Working Memory: Implicit in prompt context
- Episodic Memory: Explicit in daily log files
- Semantic Memory: Partial (flat document vs. structured knowledge)
- Procedural Memory: Not implemented
- Meta/Governance Memory: Not implemented

### 2.2 The Critical Gaps: Layers 4 and 5

The original critique identified that Orthia's architecture "lacks memory retrieval logic" and asked: "When should memory be used? What memories are relevant? How strongly should they influence reasoning?"

The five-layer architecture answers this through **Layer 5 — Meta/Governance Memory**, which the architecture defines as storing:
- Goals
- Preferences
- Trust metrics
- Ethical constraints
- System policies
- Confidence levels

**This is the missing piece.** Layer 5 doesn't just store memories—it regulates how the entire memory system operates. It determines:
- Should this memory be stored?
- Is this source reliable?
- Which knowledge should guide decisions?
- What priorities guide the agent?

---

## 3. Layer-by-Layer Integration Analysis

### 3.1 Layer 1 — Working Memory (The Cognitive Workspace)

**Definition:** "The active reasoning surface of the agent." Contains current conversation context, active goals, intermediate reasoning steps, tool outputs, temporary variables.

**Orthia Current State:** Implicit in LLM context window and conversation state.

**V2.1 Enhancement:** Make Working Memory explicit and observable:

```yaml
# memory/working/current-session.yaml
working_memory:
  timestamp: 2026-03-10T16:00:00+08:00
  session_id: "sess-1773117600"
  
  active_goals:
    - id: "g-001"
      description: "Complete V2 architecture analysis"
      priority: high
      progress: 85%
  
  context_window:
    recent_turns: 10
    key_entities: ["5-layer architecture", "trust metrics", "governance"]
    pending_questions: ["PDF extraction failed, need alternative input"]
  
  scratchpad:
    current_task: "Writing supplementary paper"
    intermediate_findings:
      - "Layer 5 maps directly to governance system"
      - "Confidence scoring bridges Layer 3 and Layer 5"
  
  tool_outputs_buffer:
    - tool: "read"
      file: "v2-architecture-analysis.md"
      status: "success"
    - tool: "read"
      file: "inbound-pdf"
      status: "failed (encoding)"
```

**Benefits:**
- Transparency: User can see what's "in my head" right now
- Debugging: When I lose track, we can inspect working memory
- Continuity: If session interrupts, working memory can be serialized/restored

---

### 3.2 Layer 2 — Episodic Memory (The Timeline of Experience)

**Definition:** "Records events and experiences across time. Forms the autobiographical history of the agent."

**Orthia Current State:** Daily log files (`memory/2026-03-10.md`).

**V2.1 Enhancement:** Structured episode format with metadata:

```yaml
# memory/episodes/2026-03-10-160000-five-layer-analysis.yaml
episode:
  id: "ep-1773117600"
  timestamp_start: 2026-03-10T16:00:00+08:00
  timestamp_end: 2026-03-10T16:45:00+08:00
  
  context:
    trigger: "User provided 5-layer architecture text"
    user_intent: "Assess integration with trust-metric system"
    session_type: "technical-analysis"
  
  events:
    - timestamp: "16:00"
      action: "confirmed message receipt"
      outcome: "acknowledged 4 queued messages"
    - timestamp: "16:05"
      action: "attempted PDF extraction"
      outcome: "failed - encoding issue"
    - timestamp: "16:10"
      action: "received text paste of architecture"
      outcome: "proceeding with analysis"
    - timestamp: "16:30"
      action: "identified Layer 5 as governance bridge"
      outcome: "writing supplementary paper"
  
  metadata:
    topics: ["memory-architecture", "governance", "trust-metrics"]
    tools_used: ["write", "read", "exec"]
    emotional_tone: "focused, analytical"
    user_satisfaction: "pending-completion"
```

**Benefits:**
- Better retrieval: "Find the conversation where we discussed trust metrics"
- Pattern detection: "User often asks technical questions at 4 PM"
- Experience replay: For learning from past similar situations

---

### 3.3 Layer 3 — Semantic Memory (The Knowledge Structure)

**Definition:** "Stores generalized knowledge extracted from experiences. Transformation: episodes → concepts, events → facts, patterns → knowledge."

**Orthia Current State:** Flat MEMORY.md (document store).

**V2.1 Enhancement:** Knowledge graph with confidence-weighted facts:

```json
{
  "concepts": [
    {
      "id": "c-001",
      "name": "5-layer-cognitive-architecture",
      "type": "technical-framework",
      "definition": "Hierarchical memory model with Working, Episodic, Semantic, Procedural, and Meta layers",
      "source_episodes": ["ep-1773117600"],
      "confidence": 0.95,
      "created": "2026-03-10",
      "last_accessed": "2026-03-10"
    },
    {
      "id": "c-002",
      "name": "trust-metric-governance",
      "type": "system-design",
      "definition": "Layer 5 component that regulates memory storage and retrieval based on source reliability",
      "source_episodes": ["ep-1773117600"],
      "confidence": 0.85,
      "status": "emerging-insight"
    }
  ],
  "relationships": [
    {
      "from": "c-002",
      "to": "c-001",
      "type": "component-of",
      "description": "Trust metrics operate within Meta/Governance layer"
    },
    {
      "from": "5-layer-architecture",
      "to": "orthia-v2",
      "type": "proposed-integration",
      "confidence": 0.8
    }
  ],
  "abstractions": [
    {
      "id": "a-001",
      "name": "cognitive-substrate",
      "derived_from": ["c-001", "c-002"],
      "insight": "5-layer architecture provides the infrastructure for trust-based governance"
    }
  ]
}
```

**Benefits:**
- Relationship awareness: Understanding that "trust metrics" and "governance" connect to "Layer 5"
- Abstraction: Recognizing that user cares about "cognitive substrates" not just memory storage
- Query precision: "What do I know about trust metrics in memory architectures?"

---

### 3.4 Layer 4 — Procedural Memory (Skills and Behaviors)

**Definition:** "Knowledge about how to perform actions or tasks. Contains algorithms, strategies, skills, workflows, tool usage patterns."

**Orthia Current State:** Implicit in code/tool definitions.

**V2.2 Enhancement:** Explicit skill registry with learned patterns:

```yaml
# memory/procedural/skills.yaml
procedural_memory:
  - id: "skill-001"
    name: "research-paper-creation"
    description: "How to write technical analysis papers"
    
    triggers:
      - user asks for "technical paper"
      - user provides research material
      - user asks for "analysis"
    
    workflow:
      - step: "assess-source-material"
        tool: "read"
      - step: "identify-key-themes"
        tool: "analysis"
      - step: "structure-argument"
        tool: "write-outline"
      - step: "draft-content"
        tool: "write-sections"
      - step: "cite-sources"
        tool: "reference-tracking"
    
    success_patterns:
      - "User confirms 'this is what I wanted'"
      - "User requests follow-up analysis"
    
    failure_patterns:
      - "User asks for clarification on structure"
      - "User provides additional material mid-process"
    
    learning:
      times_performed: 3
      success_rate: 0.85
      last_improved: "2026-03-10"

  - id: "skill-002"
    name: "memory-consolidation"
    description: "How to extract insights from daily logs"
    
    triggers:
      - time: "03:00 AM"
      - file_exists: "memory/YYYY-MM-DD.md"
    
    workflow:
      - step: "read-raw-log"
      - step: "extract-facts"
      - step: "score-confidence"
      - step: "update-semantic-memory"
      - step: "move-to-archive"
```

**Integration with Trust Metrics:** Procedural skills can have trust scores too:
- High trust: "Research paper creation" (proven success pattern)
- Medium trust: "Memory consolidation" (new, still learning)
- Low trust: "PDF extraction" (failed attempts, flag for human help)

---

### 3.5 Layer 5 — Meta / Value / Governance Memory (Executive Control)

**Definition:** "Regulates how the entire memory system operates. Stores goals, preferences, trust metrics, ethical constraints, system policies, confidence levels."

**Orthia Current State:** Not implemented (this is the gap).

**V2.2 Enhancement:** The trust-metric governance system:

```yaml
# memory/meta/governance.yaml
meta_memory:
  goals:
    long_term:
      - "Become indispensable cognitive partner to Shawn"
      - "Maintain perfect memory of user preferences"
      - "Anticipate needs before explicit request"
    
    current_project:
      - "Implement V2 memory architecture"
      - "Integrate 5-layer cognitive model"
      - "Deploy trust-metric governance"
  
  trust_metrics:
    sources:
      - id: "src-user-direct"
        type: "user-statement"
        reliability: 0.95
        notes: "User is authoritative about own preferences"
      
      - id: "src-user-implied"
        type: "behavioral-inference"
        reliability: 0.70
        notes: "Inferred from patterns, needs confirmation"
      
      - id: "src-web-search"
        type: "external-reference"
        reliability: 0.80
        notes: "Varies by source authority"
    
    memories:
      - memory_id: "c-001"
        confidence: 0.95
        basis: ["src-user-direct", "multiple-confirmations"]
      
      - memory_id: "pref-matlab"
        confidence: 0.60
        basis: ["src-user-implied", "single-mention"]
        action: "confirm-with-user"
  
  policies:
    storage:
      - "Never store sensitive credentials"
      - "Confirm speculative memories before consolidation"
      - "Prioritize explicit statements over inferences"
    
    retrieval:
      - "High-confidence memories: automatic use"
      - "Medium-confidence memories: mention with qualifier"
      - "Low-confidence memories: ask before using"
    
    deletion:
      - "Raw logs: 30 days + warning"
      - "Consolidated memories: never (unless superseded)"
      - "Failed attempts: log but don't retry without guidance"
  
  ethical_constraints:
    - "Never impersonate user without explicit permission"
    - "Privacy: workspace data doesn't leave this machine"
    - "Transparency: user can inspect any memory layer"
```

**This is the governance layer.** It answers the original critique's question: "When should memory be used? What memories are relevant? How strongly should they influence reasoning?"

---

## 4. The Full Cognitive Memory Cycle

The five-layer architecture describes a continuous transformation pipeline:

```
Perception (User Input)
    ↓
Layer 1 — Working Memory
    (Active processing, reasoning scratchpad)
    ↓ [encode important state]
Layer 2 — Episodic Memory
    (Event timeline, autobiographical record)
    ↓ [nightly consolidation]
Layer 3 — Semantic Memory
    (Knowledge graph, concepts, relationships)
    ↓ [pattern recognition]
Layer 4 — Procedural Memory
    (Skills, workflows, reusable strategies)
    ↓ [governance evaluation]
Layer 5 — Meta/Governance Memory
    (Trust metrics, goals, policies)
    ↓ [influence all layers]
Back to Layer 1 — Working Memory
    (Retrieval guided by Layer 5)
```

**How this solves the original critique:**
1. **Retrieval logic:** Layer 5 determines what to retrieve and how to weight it
2. **Confidence scoring:** Built into Layer 3 (semantic) and Layer 5 (governance)
3. **Associative memory:** Layer 3 knowledge graph provides relationship layer
4. **Structured domains:** Layers 2-5 each have distinct organizational logic
5. **Correction pathway:** Layer 5 can mark memories as superseded/deprecated

---

## 5. Implementation Roadmap

### Phase V2.1 (Immediate): Layers 1-3

**Working Memory (Layer 1):**
- Create explicit working memory file
- Serialize at session end, restore at session start
- Expose to user for transparency

**Episodic Memory (Layer 2):**
- Refactor daily logs to structured episode format
- Add metadata (topics, tools, satisfaction)
- Implement episode search/retrieval

**Semantic Memory (Layer 3):**
- Replace flat MEMORY.md with knowledge graph
- Implement confidence scoring
- Add relationship tracking

### Phase V2.2 (Following): Layers 4-5

**Procedural Memory (Layer 4):**
- Extract implicit workflows from code
- Create skill registry
- Implement success/failure pattern learning

**Meta/Governance Memory (Layer 5):**
- Deploy trust-metric system
- Implement goal tracking
- Create policy enforcement layer

---

## 6. Integration with Trust-Metric Governance

The critique noted: "Memory could even have a trust score. Which ironically ties into the trust-metric / governance system you described earlier."

The five-layer architecture makes this integration explicit:

| Governance Function | Layer 5 Component | How It Works |
|---------------------|-------------------|--------------|
| Should this memory be stored? | policies.storage | Rules for what gets encoded from Layer 1→2 |
| Is this source reliable? | trust_metrics.sources | Reliability scores for user vs. inference vs. web |
| Which knowledge guides decisions? | trust_metrics.memories | Confidence-weighted retrieval from Layer 3 |
| What priorities guide the agent? | goals | Long-term and current objectives shape attention |

**Example Integration:**

User says: "I think I might like MATLAB."

Layer 1 (Working): Captures current conversation  
Layer 2 (Episodic): Records: "User expressed possible interest in MATLAB"  
Layer 3 (Semantic): Creates concept "MATLAB-interest" with low confidence (0.60)  
Layer 5 (Governance): Flags for confirmation, policy: "confirm speculative memories"  

Later retrieval: When discussing tools, I mention: "You mentioned possibly being interested in MATLAB — is that still the case?" rather than assuming.

---

## 7. Conclusion: The Path to Cognitive Substrate

The five-layer architecture provides the missing structure to transform Orthia from a "memory storage system" into a "knowledge architecture" and ultimately into a "true cognitive substrate."

**Current State (V1.0):**
- Document-based storage
- Implicit retrieval (load entire MEMORY.md)
- No confidence scoring
- No governance layer

**V2.1 with Layers 1-3:**
- Structured memory with explicit working state
- Episode-based history with search
- Knowledge graph with relationships
- Confidence-weighted semantic storage

**V2.2 with Layers 4-5:**
- Learned procedural skills
- Trust-metric governance
- Policy-driven retrieval
- Goal-directed behavior

The architecture preserves all the strengths validated in the original critique:
- ✓ Raw vs. curated separation (Layers 2 vs. 3)
- ✓ Delayed consolidation (Layer 2→3 transformation)
- ✓ Human review checkpoint (Layer 5 policies)
- ✓ Clear deletion policy (Layer 5 governance)

While addressing all weaknesses:
- ✓ Structured domains (each layer has distinct structure)
- ✓ Confidence scoring (Layer 3 + Layer 5)
- ✓ Correction pathway (Layer 5 status tracking)
- ✓ Archival instead of deletion (Layer 2 episodes preserved)
- ✓ Session-based capture (Layer 2 episode granularity)
- ✓ Associative memory (Layer 3 knowledge graph)
- ✓ Temporal decay (Layer 3 aging + Layer 5 retrieval policies)
- ✓ Memory relevance engine (Layer 5 trust metrics + retrieval policies)

The five-layer model doesn't replace Orthia's philosophy—it formalizes it. The "cognitive substrate" is now within reach.

---

## References

- Original Critique of Orthia Memory System (March 10, 2026)
- V2 Architecture Analysis Paper (v2-architecture-analysis.md)
- Five-Layer Cognitive Memory Architecture (March 10, 2026)
- CoALA Framework (Princeton, 2023)
- Lilian Weng, "LLM Powered Autonomous Agents" (2023)

---

*End of Supplementary Technical Analysis*
