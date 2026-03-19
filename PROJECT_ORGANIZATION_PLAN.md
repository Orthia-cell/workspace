# Project Organization Plan

## Overview
This document outlines the repository structure for organizing all project-related materials from the workspace.

## Repository Structure

### 1. differential-analyzer (Already created: D-MDA)
**Purpose**: Differentiable Mechanical Differential Analyzer research
**URL**: https://github.com/Orthia-cell/D-MDA
**Contents**:
- Source code (Phases 1-4)
- Visualizations
- HTML documentation
- README with setup instructions

### 2. arduino-iot-pipeline (Already created)
**Purpose**: Arduino IoT Cloud data collection and reporting
**URL**: https://github.com/Orthia-cell/arduino-iot-pipeline
**Contents**:
- Data collection scripts
- Report generation
- GitHub publishing automation

### 3. battery-health-analysis (Already created)
**Purpose**: PyTorch-based battery SOH prediction
**URL**: https://github.com/Orthia-cell/battery-health-analysis
**Contents**:
- LSTM/CNN/Autoencoder models
- Training pipeline
- Configuration templates

### 4. research-papers (NEW)
**Purpose**: Research papers and studies
**Structure**:
```
research-papers/
├── isolation-study/
│   ├── final-paper/
│   │   └── the-line-between-protection-and-isolation.md
│   ├── phase-1/
│   │   └── philosophy-solitude.md
│   ├── phase-3/
│   │   └── psychology-isolation.md
│   ├── phase-4/
│   │   └── historical-examples.md
│   └── README.md
├── memory-system/
│   ├── enhanced-memory-architecture.md
│   ├── v2-architecture-analysis.md
│   └── v2-supplementary-five-layer-analysis.md
├── governance-architecture/
│   └── governor-layer-proposal.md
└── README.md
```

### 5. knowledge-base (NEW)
**Purpose**: SQLite and database learning materials
**Structure**:
```
knowledge-base/
├── sqlite/
│   ├── hour-01-foundation.md
│   ├── hour-04.md
│   ├── hour-05.md
│   ├── hour-06.md
│   ├── hour-09.md
│   ├── hour-10.md
│   ├── hour-11.md
│   ├── hour-12.md
│   ├── hour-13.md
│   ├── hour-14.md
│   ├── executive-summary.md
│   └── README.md
└── README.md
```

### 6. orthia-memory (NEW)
**Purpose**: Session logs and memory archives
**Structure**:
```
orthia-memory/
├── 2026-03/
│   ├── 2026-03-03.md
│   ├── 2026-03-04.md
│   ├── 2026-03-05-conversation-dreams.md
│   ├── 2026-03-07.md
│   ├── 2026-03-08.md
│   ├── 2026-03-09.md
│   ├── 2026-03-16.md
│   └── 2026-03-17.md
├── projects/
│   ├── arduino-iot-pipeline-project.md
│   └── D-MDA-Phase1-Archive.md
├── facts/
│   ├── golden-tests.md
│   └── verified-state.json
└── README.md
```

### 7. orthia-config (NEW)
**Purpose**: Configuration and identity files
**Structure**:
```
orthia-config/
├── AGENTS.md
├── IDENTITY.md
├── MEMORY.md
├── SOUL.md
├── TOOLS.md
├── USER.md
├── HEARTBEAT.md
└── README.md
```

## Naming Conventions

### Repositories
- lowercase-with-hyphens
- descriptive but concise
- avoid underscores (use hyphens)
- include domain when relevant

### Files
- lowercase-with-hyphens.md
- dates: YYYY-MM-DD.md
- descriptive names
- version indicators if needed: v2-, final-, etc.

### Directories
- lowercase
- descriptive
- hierarchical organization by topic/date

## Implementation Steps

1. ✅ Create research-papers repository
2. ✅ Create knowledge-base repository  
3. ✅ Create orthia-memory repository
4. ✅ Create orthia-config repository
5. ✅ Push all content with proper structure
6. ✅ Add README files to each repository
7. ✅ Create master index repository (optional)

## Benefits

- **Searchability**: Clear naming makes content easy to find
- **Modularity**: Each project isolated but accessible
- **Version Control**: Git history tracks all changes
- **Collaboration**: Easy to share specific projects
- **Backup**: Distributed across GitHub infrastructure
