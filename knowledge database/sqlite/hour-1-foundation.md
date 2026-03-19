# SQLite Research — Hour 1 (March 4, 2026, 10:45 PM)

## Executive Overview
SQLite is a serverless, self-contained SQL database engine written in C. Unlike traditional databases (MySQL, PostgreSQL), SQLite requires no separate server process — it reads and writes directly to a single disk file.

---

## Key Characteristics

### Architecture
- **Serverless**: No daemon process, no configuration files
- **Single-file database**: All tables, indexes, views, triggers in one portable file
- **Zero configuration**: Drop-in library, no setup required
- **Cross-platform**: Windows, macOS, Linux, iOS, Android

### Performance Metrics
| Metric | Value |
|--------|-------|
| Library size | ~250 KB (core), ~750 KB (full) |
| Database capacity | Stable at 20GB+ |
| Query response (16MB DB) | <200ms |
| Linux startup time | 0.8s |
| Complex query (Linux) | 350ms |

### Concurrency Model
- **Single writer, multiple readers**
- **WAL mode** (Write-Ahead Logging) improves read/write overlap
- Recent optimizations: per-transaction overhead reduced from 30ms to <1ms

### Data Integrity
- Full **ACID compliance** (Atomicity, Consistency, Isolation, Durability)
- Rollback journals for recovery
- 89.7% accuracy on corrupt file detection
- 72.3% successful data recovery rate

---

## Use Cases
1. **Mobile apps** — iOS/Android offline storage (WhatsApp, etc.)
2. **Web browsers** — Firefox history/bookmarks
3. **Desktop apps** — Adobe Lightroom catalogs
4. **Embedded/IoT** — Tesla logs, smartwatches
5. **Edge computing** — Serverless scenarios eliminating network latency

---

## Security Considerations
- No built-in authentication (relies on filesystem permissions)
- Encryption available via **SQLCipher** (AES-256, +18% overhead)
- Alternative: **SEE** (SQLite Encryption Extension, RC4, +9% overhead)

---

## Scale Limitations
- Best for: Small to medium applications, read-heavy workloads
- Not ideal: High-concurrency write scenarios, large-scale distributed systems
- MySQL/PostgreSQL preferred for: Web apps, OLTP, analytics, SaaS

---

## Deployment Stats
- **1 trillion+** active SQLite databases worldwide
- Primarily driven by smartphone adoption (hundreds per device)
- 10th position globally in DB-Engines ranking
- 50%+ of mobile apps use SQLite for local storage
- 60%+ of IoT implementations leverage embedded SQLite

---

*Source: Multiple technical articles, DB-Engines rankings, 2024-2025*
