# Kimi API Maximum Utilization Strategy
## Optimizing Server Usage Without Exceeding Rate Limits

**Date:** March 28, 2026  
**Author:** Orthia (Laere Enterprises Systems Architect)  
**Classification:** Internal Technical Reference

---

## Executive Summary

This paper defines an optimal strategy for maximizing Kimi API utilization while respecting rate limits and server load constraints. Based on analysis of Moonshot AI's API policies, empirical data from production usage, and industry best practices, we establish a framework for:

1. **Session Architecture** — Separating `max_server_use_time` from `timeout_seconds`
2. **Optimal Scheduling** — Operating during China off-peak hours (12 AM - 6 AM CST)
3. **Intelligent Retry Logic** — Exponential backoff with jitter and circuit breakers
4. **Rate Limit Compliance** — Understanding actual limits and avoiding punitive restrictions

---

## 1. Kimi/Moonshot API Policy Analysis

### 1.1 Rate Limit Structure

Moonshot AI enforces rate limits across **four dimensions simultaneously** — whichever threshold is reached first triggers throttling:

| Limit Type | Description | Free Tier | Paid Tier Scaling |
|------------|-------------|-----------|-------------------|
| **Concurrency** | Max simultaneous requests | 1 | Increases with recharge |
| **RPM** | Requests per minute | 3 | 20-500+ based on tier |
| **TPM** | Tokens per minute | 32,000 | 200K+ based on tier |
| **TPD** | Tokens per day | 1,500,000 | Unlimited on paid tiers |

**Critical Finding:** Rate limits are enforced at the **user level**, not API key level. Multiple keys under one account share the same quota.

### 1.2 Token Bucket Algorithm

Moonshot uses a **token bucket** rather than fixed-window limiting. This means:
- Capacity replenishes continuously, not at fixed intervals
- Short bursts can trigger limits even if average usage is below threshold
- A 60-second wait is typically sufficient for bucket refill after hitting a limit

### 1.3 Rate Limit Response Headers

When approaching limits, the API returns:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1709125800
```

**Important:** When rate limited (429), Moonshot returns `Retry-After` header. Respect this value rather than using calculated backoff.

### 1.4 The Rate Limit / Billing Trap

**Critical Bug Identified:** When API account balance reaches zero, Moonshot returns **429 Rate Limit Reached** instead of a clear billing error. This can trigger infinite retry loops that:
1. Waste computational resources
2. Extend lockout periods
3. Potentially flag accounts for abuse

**Mitigation:** Always check account balance before implementing retry logic.

---

## 2. Session Architecture: Work Time vs. Timeout

### 2.1 The Distinction

| Parameter | Purpose | Recommended Value |
|-----------|---------|-------------------|
| `max_server_use_time` | Target duration for productive work | 20-25 minutes |
| `timeout_seconds` | Hard kill switch to prevent runaway processes | 30 minutes (1800s) |
| `rate_limit_cooldown` | Mandatory pause after 429 errors | 60-300 seconds |

### 2.2 Why Separate These Values?

**Scenario Analysis:**

```
Without separation:
- timeout = 30 minutes
- Work completes in 5 minutes
- Rate limit hit at minute 6
- Infinite retry for 24 minutes until timeout
- Result: Account flagged, wasted tokens

With separation:
- max_server_use_time = 25 minutes
- timeout = 30 minutes
- Rate limit hit at minute 6
- Circuit breaker triggers, session ends gracefully
- Result: Clean failure, no account flagging
```

### 2.3 Implementation Pattern

```python
class KimiSessionConfig:
    """Production-ready session configuration for Kimi API."""
    
    # Target work duration — session should complete within this window
    MAX_SERVER_USE_TIME_SECONDS: int = 1500  # 25 minutes
    
    # Hard timeout — absolute ceiling regardless of state
    TIMEOUT_SECONDS: int = 1800  # 30 minutes
    
    # Rate limit handling
    RATE_LIMIT_COOLDOWN_SECONDS: int = 60
    MAX_RETRY_ATTEMPTS: int = 3
    CIRCUIT_BREAKER_THRESHOLD: int = 2  # consecutive 429s before pause
    
    # Scheduling optimization
    OFF_PEAK_START_HOUR: int = 0   # 12 AM China
    OFF_PEAK_END_HOUR: int = 6     # 6 AM China
    INTER_SESSION_GAP_MINUTES: int = 45
```

---

## 3. Retry Strategy Architecture

### 3.1 The Problem with Naive Retries

**Naive approach (DANGEROUS):**
```python
# DO NOT USE — Exacerbates rate limiting
while True:
    try:
        response = call_api()
        break
    except RateLimitError:
        time.sleep(1)  # Too aggressive
        continue
```

**Problems:**
1. No backoff — immediate retry wastes quota
2. No jitter — synchronized retries from multiple clients create thundering herd
3. No circuit breaker — infinite loops trigger account restrictions
4. No header inspection — ignores server's `Retry-After` guidance

### 3.2 Production-Ready Retry Implementation

```python
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

class BackoffStrategy(Enum):
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"

@dataclass
class RetryConfig:
    """Configuration for rate-limit-aware retry logic."""
    max_attempts: int = 5
    base_delay_seconds: float = 60.0  # Start with 1 minute (token bucket refill)
    max_delay_seconds: float = 300.0  # Cap at 5 minutes
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL_JITTER
    circuit_breaker_threshold: int = 3
    respect_retry_after: bool = True
    
    # Account protection
    abort_on_auth_error: bool = True  # Stop on 401/403 (billing issue)
    abort_on_server_error: bool = False  # Retry 500s (transient)

class CircuitBreaker:
    """Prevents cascading failures by stopping after consecutive errors."""
    
    def __init__(self, threshold: int = 3, reset_after_seconds: float = 600):
        self.threshold = threshold
        self.reset_after = reset_after_seconds
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
    
    def record_failure(self) -> bool:
        """Record a failure. Returns True if circuit is now OPEN (should stop)."""
        now = time.time()
        
        # Reset if enough time has passed
        if self._last_failure_time and (now - self._last_failure_time) > self.reset_after:
            self._failure_count = 0
        
        self._failure_count += 1
        self._last_failure_time = now
        
        is_open = self._failure_count >= self.threshold
        if is_open:
            logger.warning(f"Circuit breaker OPEN after {self._failure_count} consecutive failures")
        return is_open
    
    def record_success(self):
        """Reset circuit on success."""
        if self._failure_count > 0:
            logger.info(f"Circuit breaker reset (was at {self._failure_count})")
        self._failure_count = 0

class RateLimitAwareClient:
    """Production client with intelligent rate limit handling."""
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.circuit_breaker = CircuitBreaker(
            threshold=self.config.circuit_breaker_threshold
        )
        self._consecutive_429s = 0
    
    def calculate_backoff(self, attempt: int, retry_after: Optional[int] = None) -> float:
        """Calculate delay before next retry."""
        
        # Always respect server's Retry-After if provided
        if self.config.respect_retry_after and retry_after:
            return float(retry_after)
        
        base = self.config.base_delay_seconds
        
        if self.config.strategy == BackoffStrategy.FIXED:
            delay = base
        elif self.config.strategy == BackoffStrategy.LINEAR:
            delay = base * attempt
        elif self.config.strategy == BackoffStrategy.EXPONENTIAL:
            delay = base * (2 ** (attempt - 1))
        elif self.config.strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            # Exponential with full jitter to prevent thundering herd
            exp_delay = base * (2 ** (attempt - 1))
            delay = random.uniform(0, exp_delay)
        else:
            delay = base
        
        return min(delay, self.config.max_delay_seconds)
    
    def execute_with_retry(self, operation: Callable, operation_name: str = "API call"):
        """Execute operation with rate-limit-aware retry logic."""
        
        for attempt in range(1, self.config.max_attempts + 1):
            # Check circuit breaker
            if self.circuit_breaker._failure_count >= self.config.circuit_breaker_threshold:
                raise Exception(f"Circuit breaker open — too many consecutive failures")
            
            try:
                result = operation()
                self.circuit_breaker.record_success()
                self._consecutive_429s = 0
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Detect rate limit (429)
                is_rate_limit = (
                    "rate limit" in error_str or 
                    "429" in error_str or
                    "too many requests" in error_str
                )
                
                # Detect auth/billing errors (401/403)
                is_auth_error = (
                    "unauthorized" in error_str or
                    "forbidden" in error_str or
                    "billing" in error_str or
                    "credit" in error_str
                )
                
                # Handle auth errors — don't retry
                if is_auth_error and self.config.abort_on_auth_error:
                    logger.error(f"Authentication/billing error — aborting: {e}")
                    raise
                
                # Handle rate limits
                if is_rate_limit:
                    self._consecutive_429s += 1
                    
                    # Extract Retry-After if present (would need actual HTTP response)
                    retry_after = None  # Parse from response headers in real implementation
                    
                    if attempt < self.config.max_attempts:
                        delay = self.calculate_backoff(attempt, retry_after)
                        logger.warning(
                            f"Rate limited ({self._consecutive_429s}x). "
                            f"Attempt {attempt}/{self.config.max_attempts}. "
                            f"Waiting {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        continue
                
                # Record failure for circuit breaker
                should_stop = self.circuit_breaker.record_failure()
                if should_stop:
                    raise Exception(f"Circuit breaker tripped after {attempt} attempts")
                
                # Final attempt failed
                if attempt >= self.config.max_attempts:
                    logger.error(f"All {self.config.max_attempts} attempts failed")
                    raise
        
        raise Exception("Unexpected exit from retry loop")


# Usage Example
if __name__ == "__main__":
    client = RateLimitAwareClient(RetryConfig(
        max_attempts=3,
        base_delay_seconds=60,
        strategy=BackoffStrategy.EXPONENTIAL_JITTER
    ))
    
    def my_api_call():
        # Your actual API call here
        pass
    
    result = client.execute_with_retry(my_api_call, "Kimi research query")
```

### 3.3 OpenClaw-Specific Integration

For OpenClaw deployments, implement at the cron job level:

```javascript
// openclaw cron job payload with rate limit awareness
{
  "kind": "agentTurn",
  "message": "...task instructions...\n\nRATE LIMIT PROTOCOL:\n" +
    "1. If you receive 'API rate limit reached' or 429 error, STOP immediately\n" +
    "2. Do NOT retry the same request\n" +
    "3. Save current progress to disk\n" +
    "4. Report: 'Rate limited at [step]. Progress saved. Retry after 60s.'\n" +
    "5. End session gracefully — do not loop\n\n" +
    "CIRCUIT BREAKER:\n" +
    "- After 2 consecutive rate limits, skip remaining tasks\n" +
    "- Report: 'Circuit breaker triggered — too many rate limits'",
  "model": "kimi-coding/k2p5",
  "timeoutSeconds": 1800,  // Hard timeout
  "thinking": "high"
}
```

---

## 4. Scheduling Optimization

### 4.1 China Off-Peak Analysis

Based on server location (China) and usage patterns:

| Time (China) | Traffic Level | Recommendation |
|--------------|---------------|----------------|
| 12 AM - 2 AM | Very Low | Primary research window |
| 2 AM - 4 AM | Low | Secondary tasks |
| 4 AM - 6 AM | Moderate | Finalization, cleanup |
| 6 AM - 9 AM | Increasing | Avoid new sessions |
| 9 AM - 12 PM | Peak | Read-only operations only |
| 12 PM - 11 PM | High | Avoid all automated tasks |

### 4.2 Laere Operations Schedule (Optimized)

```yaml
# All times in China Standard Time (CST/UTC+8)

daily_schedule:
  - job: orthia-auto-commit
    time: "00:00"  # Midnight
    duration_target: 5m
    timeout: 10m
    
  - job: grace-morning-research-v1
    time: "00:00"  # Parallel with auto-commit (different agents)
    duration_target: 25m
    timeout: 30m
    gap_after: 45m
    
  - job: grace-recursive-critique-v2
    time: "00:45"
    duration_target: 25m
    timeout: 30m
    gap_after: 45m
    
  - job: orthia-daily-question
    time: "01:30"
    duration_target: 5m
    timeout: 10m
    gap_after: 45m
    
  - job: grace-finalization-v3
    time: "02:15"
    duration_target: 25m
    timeout: 30m
    
# All jobs complete by 02:45 — 3h 15m buffer before peak traffic
```

### 4.3 Why 45-Minute Gaps?

1. **Token bucket refill:** Ensures full quota restoration between sessions
2. **Server cooldown:** Prevents thermal/load accumulation
3. **Error isolation:** Failure in one job doesn't cascade to next
4. **Human review window:** If rate limits occur, intervention possible

---

## 5. Maximum Continuous API Use Guidelines

### 5.1 Session Duration Limits

| Use Case | Max Continuous Use | Mandatory Pause |
|----------|-------------------|-----------------|
| Research (high thinking) | 25 minutes | 15 minutes |
| Code generation | 20 minutes | 10 minutes |
| Chat/dialog | 60 minutes | 5 minutes |
| Background tasks | 30 minutes | 20 minutes |

### 5.2 Daily Quota Management

For typical Laere usage patterns:

```python
DAILY_BUDGET = {
    "kimi_k25_requests": 50,      # Conservative for free tier
    "kimi_k25_tokens": 500_000,   # Well below 1.5M TPD limit
    "total_sessions": 8,          # Spread across off-peak hours
    "concurrent_sessions": 1,     # Respect concurrency limit
}

# With current schedule (4-5 sessions/day in off-peak window):
# - Each session: ~10K-50K tokens
# - Daily total: ~200K-300K tokens
# - Safety margin: 70% below TPD limit
```

---

## 6. Monitoring and Alerting

### 6.1 Key Metrics to Track

```python
@dataclass
class UsageMetrics:
    requests_today: int
    tokens_today: int
    rate_limit_hits: int
    average_session_duration: float
    peak_concurrency: int
    
    def health_check(self) -> dict:
        """Return health status and recommendations."""
        status = {
            "healthy": True,
            "warnings": [],
            "actions": []
        }
        
        # Check rate limit frequency
        if self.rate_limit_hits > 3:
            status["warnings"].append(f"{self.rate_limit_hits} rate limits today")
            status["actions"].append("Consider increasing inter-session gaps to 60+ minutes")
        
        # Check token usage
        if self.tokens_today > 1_000_000:
            status["warnings"].append("Token usage above 1M — approaching daily limit")
            status["actions"].append("Reduce output max_tokens or switch to cheaper model")
        
        # Check concurrency
        if self.peak_concurrency > 1:
            status["warnings"].append(f"Peak concurrency was {self.peak_concurrency}")
            status["actions"].append("Stagger job schedules to enforce single concurrency")
        
        status["healthy"] = len(status["warnings"]) == 0
        return status
```

### 6.2 Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Rate limits/hour | 2 | 5 | Pause new sessions for 2 hours |
| Token usage/day | 1M | 1.4M | Switch to lower-cost model |
| Session failures | 1 | 3 | Circuit breaker open |
| Avg response time | 10s | 30s | Reduce complexity, add caching |

---

## 7. Implementation Checklist

### For New Cron Jobs

- [ ] Set `max_server_use_time` to 20-25 minutes for research tasks
- [ ] Set `timeout_seconds` to 30 minutes (hard ceiling)
- [ ] Include rate limit protocol in agent instructions
- [ ] Schedule within 12 AM - 6 AM China window
- [ ] Maintain 45-minute minimum gap from other jobs
- [ ] Configure circuit breaker (2 consecutive 429s = pause)
- [ ] Add progress checkpointing (save state every 5 minutes)

### For Existing Jobs

- [ ] Audit current timeout settings — reduce if excessive
- [ ] Add rate limit detection to error handling
- [ ] Implement exponential backoff with jitter
- [ ] Review schedules — move to off-peak if currently during China business hours
- [ ] Add telemetry: track rate limit frequency, session duration

### For System Architecture

- [ ] Implement `RateLimitAwareClient` wrapper (Python code above)
- [ ] Deploy monitoring dashboard for usage metrics
- [ ] Configure alerts for rate limit threshold breaches
- [ ] Document emergency procedures (what to do if completely rate limited)
- [ ] Set up fallback model configuration for critical tasks

---

## 8. Summary of Recommendations

| Area | Current Practice | Recommended Practice |
|------|-----------------|---------------------|
| Scheduling | 8 AM, 11 AM, 3 PM PT | 12 AM - 2:15 AM China |
| Session timeout | 600s (10 min) | 1800s (30 min) hard limit |
| Work target | Same as timeout | 1500s (25 min) soft target |
| Inter-job gap | 3 hours | 45 minutes |
| Retry on 429 | Immediate | 60s exponential backoff |
| Max retries | Infinite/unlimited | 3 attempts, then circuit break |
| Concurrency | 2+ simultaneous | 1 at a time |

---

## Appendix A: Rate Limit Error Codes Reference

| HTTP Code | Meaning | Retry? | Notes |
|-----------|---------|--------|-------|
| 429 | Too Many Requests | Yes (with backoff) | Check Retry-After header |
| 401 | Unauthorized | No | Billing/auth issue |
| 403 | Forbidden | No | Account suspended |
| 500 | Internal Server Error | Yes | Transient, retry with backoff |
| 502/503/504 | Gateway Error | Yes | Transient infrastructure issue |
| 529 | Overloaded | Yes (long backoff) | Server capacity exceeded |

---

## Appendix B: Quick Reference Commands

```bash
# Check current cron job schedules
openclaw cron list

# View recent rate limit events
grep -i "rate limit" ~/.openclaw/logs/*.log | tail -20

# Check account balance (Kimi)
curl -H "Authorization: Bearer $KIMI_API_KEY" \
  https://api.moonshot.ai/v1/balance

# Monitor session durations from cron runs
python3 -c "
import json
from pathlib import Path
for f in Path('~/.openclaw/cron/runs').expanduser().glob('*.jsonl'):
    print(f'Statistics for {f.stem[:8]}...')
    # Parse and analyze duration data
"
```

---

**Document Version:** 1.0  
**Last Updated:** March 28, 2026  
**Next Review:** April 28, 2026 (or upon API policy changes)

*For questions or updates, contact: systems@laere.enterprises*
