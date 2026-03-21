# Memory Management Research

A comprehensive research project on memory management techniques derived from cognitive neuroscience, AI research, and educational psychology.

## Overview

This repository contains:
- **Full research paper** on memory management science
- **Working Python implementations** of key algorithms
- **Visualizations and analysis** of forgetting curves
- **Reference materials** and citations

## Directory Structure

```
research/memory-management/
├── paper/
│   └── main.md              # Complete research paper (Markdown)
├── code/
│   ├── spaced_repetition.py # Adaptive scheduling algorithm
│   ├── memory_network.py    # Semantic network with spreading activation
│   ├── priority_queue.py    # Multi-tier memory management
│   └── forgetting_curve.py  # Ebbinghaus curve modeling
├── figures/                 # Generated visualizations
├── references/              # Bibliography and citations
└── README.md               # This file
```

## Quick Start

### Running the Code Examples

```bash
cd research/memory-management/code

# Spaced repetition scheduler
python spaced_repetition.py

# Semantic memory network
python memory_network.py

# Multi-tier memory manager
python priority_queue.py

# Forgetting curve analysis
python forgetting_curve.py
```

### Generating the PDF

The research paper is available in Markdown format at `paper/main.md`. To convert to PDF:

```bash
# Using pandoc
pandoc paper/main.md -o paper/memory_management_research.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  --toc

# Or using markdown-pdf (Node.js)
markdown-pdf paper/main.md -o paper/memory_management_research.pdf
```

## Key Concepts

### 1. The Memory Triad
- **Encoding**: Converting information into storable form
- **Storage**: Maintaining information over time
- **Retrieval**: Accessing stored information when needed

### 2. Forgetting Curve
Based on Ebbinghaus (1885), modified by modern research:

| Time | Retention (No Review) | With Spaced Review |
|------|----------------------|-------------------|
| 1 hour | 55% | — |
| 1 day | 33% | 90% |
| 1 week | 20% | 85-90% |
| 1 month | 10% | 80-85% |

### 3. Spaced Repetition Schedule
Optimal review intervals: Day 1, 3, 7, 14, 30, 60...

### 4. Semantic Networks
- **Hub nodes**: High-connectivity concepts
- **Bridge connections**: Cross-domain links
- **Small-world topology**: High clustering + short paths

### 5. Multi-Tier Architecture
| Tier | Capacity | Characteristics |
|------|----------|-----------------|
| Working | ~7 items | Immediate access |
| Episodic | ~100 items | Context-rich |
| Semantic | ~10,000 items | Long-term knowledge |
| Archive | Unlimited | Cold storage |

## Research Summary

### What to Keep
- Information with high connective value
- Frequently accessed items
- Emotionally/semantically weighted content
- Future-relevant knowledge

### How to Rank Priority
- Recency of access
- Frequency of access
- Connection density
- Predicted future utility

### When to Retire
- After repeated failed retrievals (≥3)
- No access for extended periods (>30 days)
- Superseded by newer information
- Low priority scores (<0.1)

### Interconnectedness Benefits
- **Pattern completion**: Reconstruct from partial cues
- **Resilient retrieval**: Multiple pathways to information
- **Inference generation**: Connect distant concepts
- **Creative insight**: Cross-domain bridges enable novelty

## References

See `references/bibliography.md` for full citations.

Key sources:
- Ebbinghaus, H. (1885). *Über das Gedächtnis*
- Wozniak, P. SuperMemo algorithm
- Cambridge (2020). Adaptive forgetting curves
- Penn State (2025). Semantic network reorganization
- IFIByNE-CONICET (2025). Associative memory research

## License

Research use only. Cite appropriately.

---

**Author:** Orthia Research Division  
**Date:** March 22, 2026  
**Version:** 1.0
