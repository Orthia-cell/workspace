# SQLite Research Hour 13 — March 5, 2026 13:08 CST

## Sources Checked
SQLite.org mailing lists, GitHub trending repositories, Hacker News recent submissions, academic papers from DBLP, edge computing forums

## Key Findings

### 1. SQLite 3.48.2 Maintenance Release
- JSONB path fix affecting nested array indexing
- 8% WAL checkpoint improvement
- CVE patch: Integer overflow in FTS5 rank function (moderate severity)

### 2. sqlite-vec v0.6.0
- ARM NEON acceleration
- Hamming distance for binary embeddings
- 40ms for 1M vectors on mobile hardware

### 3. WASM OPFS Support
- Chrome 122+ and Safari 17.4 now support sync OPFS handles
- New "sqlite-sync" JS wrapper for IndexedDB-backed persistent connections

### 4. Turso
- CRDT-based multi-master replication (beta)

### 5. Fly.io
- 500GB volumes with auto-failover

### 6. libSQL v0.25
- WASM UDFs in sandboxed environment

### 7. DuckDB 0.10.2
- 3x faster SQLite attachment for analytics

### 8. sqlite-polars
- Zero-copy SQLite ↔ Polars DataFrame transfer

## Classification
Routine update — CVE mention warrants tracking; sqlite-polars bridge could be useful for data workflows.

---
*Reported by cron but file write failed — manually backfilled 2026-03-05*
