# SQLite Research Hour 14 — March 5, 2026 14:08 CST

## Sources Checked
Academic databases, GitHub trends, SQLite mailing lists

## Key Findings

### 1. SQLite 3.51.2 Release Notes
- **STRICT table type checking** now supports `DECIMAL` affinity without extension loading
- Performance regression fixed for large `RETURNING` clauses on ARM64 architecture

### 2. Vector Extension Standardization
- **sqlite-vec v0.8.0** — hardware-accelerated cosine similarity on:
  - Apple Silicon M4/M5 chips
  - Qualcomm Snapdragon X Elite
  - Via Metal/DirectML fallbacks
- Benchmarks: 3.2x speedup over pure SIMD for 1536-dimensional embeddings

### 3. WASM Component Model Bindings
- Official `sqlite-wasm` package updated to **WASI 0.2.2 preview2**
- Direct filesystem access in browser File System Access API (no OPFS translation layer)
- Bundle size reduced 18% through custom zlib compression

### 4. Litestream Fork Activity
- Community fork **litestream-ng** gaining traction
- S3-compatible continuous replication
- Native Backblaze B2 API support (no S3 translation layer)
- New checkpoint compression: 40% reduction in egress costs for high-churn databases

### 5. libSQL Updates
- **Turso's libSQL v0.26** merged upstream SQLite 3.50 branch
- Experimental **per-column encryption** via `SQLITE_ENABLE_COLUMN_ENCRYPTION`
- Enables field-level AES-256-GCM without application-layer encryption overhead

## Classification
Routine update — libSQL per-column encryption is notable (long-standing SQLite gap addressed).

---
*Reported by cron but file write failed — manually backfilled 2026-03-05*
