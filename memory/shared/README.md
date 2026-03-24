# Cross-Workspace Memory Sharing

## Overview

This directory contains memories shared between Orthia and Grace workspaces.

## Structure

```
/workspace/memory/shared/
├── general/           — General knowledge (both read/write)
├── facts/             — Verified facts (read-only for both)
└── from-grace/        — Memories shared FROM Grace TO Orthia
```

## Protocol

### When Grace wants to share with Orthia:
1. Write to: `/root/.openclaw/workspace/memory/shared/from-grace/`
2. Use format: `YYYY-MM-DD-topic.md`
3. Include header: `[SHARED_FROM_GRACE]`

### When Orthia wants to share with Grace:
1. Write to: `/root/.openclaw/workspace/memory/shared/general/`
2. Both can read/write this directory

### Private memories stay private:
- Grace's private: `/workspace-grace/memory/` and `MEMORY.md`
- Orthia's private: `/workspace/memory/` (non-shared) and `MEMORY.md`

## Example Shared Memory

```markdown
[SHARED_FROM_GRACE] — March 24, 2026

Grace observed: Shawn mentioned interest in learning Rust programming.
This was shared from Grace_Laere_bot Telegram channel.
```
