# Hybrid Kimi API Strategy: Adaptive Throttling for Mixed Workloads
## Combining Fixed Scheduling with Self-Tuning Rate Limiters

**Date:** March 28, 2026  
**Author:** Orthia (Laere Enterprises Systems Architect)  
**Version:** 1.0 — Hybrid Approach

---

## Executive Summary

This paper presents a **hybrid architecture** that combines the reliability of fixed-schedule cron jobs with the responsiveness of adaptive throttling. Rather than choosing between conservative batch processing and aggressive real-time optimization, this approach layers both strategies to handle:

1. **Predictable batch workloads** — Cron jobs with guaranteed completion windows
2. **Variable real-time traffic** — On-demand requests that must minimize latency
3. **Mixed environments** — Systems that handle both patterns simultaneously

The core insight: **Use fixed scheduling for macro-level timing, adaptive throttling for micro-level request pacing.**

---

## 1. The Problem with Pure Approaches

### 1.1 Pure Fixed Scheduling (Original Paper)

**Strengths:**
- Predictable resource usage
- Guaranteed off-peak execution
- Simple to debug and audit

**Weaknesses:**
- Wastes capacity during low-traffic periods
- Cannot respond to real-time demand
- Rigid — doesn't adapt to API performance changes

### 1.2 Pure Adaptive Throttling (PDF Approach)

**Strengths:**
- Maximizes throughput
- Self-healing under varying load
- Optimal for interactive systems

**Weaknesses:**
- Unpredictable completion times
- Can miss batch deadlines
- Complex to tune initially

### 1.3 The Hybrid Insight

| Layer | Approach | Timescale | Decision Driver |
|-------|----------|-----------|-----------------|
| **Macro** | Fixed scheduling | Hours | Business requirements (off-peak windows) |
| **Meso** | Job isolation | Minutes | Circuit breakers, failure containment |
| **Micro** | Adaptive throttling | Seconds | Real-time API feedback (429 rates) |

---

## 2. Hybrid Architecture Design

### 2.1 Three-Layer Throttle Stack

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: SCHEDULER (Fixed)                                 │
│  • Cron jobs at fixed times                                 │
│  • Hard start/stop boundaries                               │
│  • 45-minute inter-job gaps                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: SESSION MANAGER (Fixed + Circuit Breaker)         │
│  • max_server_use_time: 25 min target                       │
│  • timeout_seconds: 30 min hard limit                       │
│  • Circuit breaker: Stop after 2 consecutive 429s           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: REQUEST THROTTLER (Adaptive)                      │
│  • Dynamic delay based on success/error rates               │
│  • Self-tuning within session boundaries                    │
│  • Exponential backoff with jitter                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 When Each Layer Activates

**Layer 1 (Scheduler):**
- Trigger: Clock time (12:00 AM, 12:45 AM, etc.)
- Action: Start job or skip if previous still running
- No adaptation — strictly time-based

**Layer 2 (Session Manager):**
- Trigger: Job starts, API calls begin
- Action: Monitor duration and error rates
- Adaptation: Circuit breaker opens on repeated failures

**Layer 3 (Request Throttler):**
- Trigger: Every individual API request
- Action: Adjust delay before next request
- Adaptation: Continuous, based on 429 frequency

---

## 3. Implementation: Hybrid Throttler Class

### 3.1 Core HybridThrottler

```python
import random
import time
from dataclasses import dataclass, field
from typing import Optional, Callable, List
from enum import Enum
from collections import deque
import logging

logger = logging.getLogger(__name__)

class WorkloadType(Enum):
    CRON_BATCH = "cron_batch"      # Fixed schedule, conservative
    REALTIME = "realtime"          # Adaptive, aggressive
    MIXED = "mixed"                # Both patterns simultaneously

@dataclass
class HybridThrottleConfig:
    """Configuration for hybrid throttling across three layers."""
    
    # Layer 1: Scheduler (Fixed)
    schedule_type: WorkloadType = WorkloadType.CRON_BATCH
    off_peak_start_hour: int = 0      # 12 AM China
    off_peak_end_hour: int = 6        # 6 AM China
    inter_job_gap_minutes: int = 45
    
    # Layer 2: Session Manager (Fixed + Circuit Breaker)
    max_server_use_time: int = 1500   # 25 minutes
    hard_timeout: int = 1800          # 30 minutes
    circuit_breaker_threshold: int = 2
    circuit_breaker_reset_seconds: int = 600
    
    # Layer 3: Request Throttler (Adaptive)
    # Different defaults based on workload type
    adaptive_min_delay: float = field(default_factory=lambda: 60.0)   # Cron: 60s
    adaptive_max_delay: float = 300.0
    adaptive_aggression: float = 0.9   # Speed up factor (0.9 = 10% faster)
    
    # Moving average windows
    success_window_size: int = 20
    error_window_size: int = 10
    
    def __post_init__(self):
        """Adjust defaults based on workload type."""
        if self.schedule_type == WorkloadType.REALTIME:
            self.adaptive_min_delay = 1.0   # Aggressive: 1s base
            self.adaptive_aggression = 0.95  # Speed up faster

class MovingAverage:
    """Simple moving average for tracking success/error rates."""
    
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.values: deque = deque(maxlen=window_size)
    
    def add(self, value: float):
        self.values.append(value)
    
    @property
    def avg(self) -> float:
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)
    
    @property
    def is_full(self) -> bool:
        return len(self.values) >= self.window_size

class CircuitBreaker:
    """Prevents cascading failures — Layer 2."""
    
    def __init__(self, threshold: int = 2, reset_after_seconds: float = 600):
        self.threshold = threshold
        self.reset_after = reset_after_seconds
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._is_open = False
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open, with auto-reset on timeout."""
        if not self._is_open:
            return False
        
        now = time.time()
        if self._last_failure_time and (now - self._last_failure_time) > self.reset_after:
            logger.info("Circuit breaker auto-reset after timeout")
            self.reset()
            return False
        
        return True
    
    def record_failure(self) -> bool:
        """Record failure. Returns True if circuit just opened."""
        now = time.time()
        self._failure_count += 1
        self._last_failure_time = now
        
        if self._failure_count >= self.threshold:
            if not self._is_open:
                logger.warning(f"Circuit breaker OPENED after {self._failure_count} failures")
                self._is_open = True
            return True
        return False
    
    def record_success(self):
        """Record success — only reset if we were close to threshold."""
        if self._failure_count > 0:
            self._failure_count = max(0, self._failure_count - 1)
    
    def reset(self):
        """Manual reset."""
        self._failure_count = 0
        self._is_open = False
        self._last_failure_time = None

class AdaptiveRequestThrottler:
    """Layer 3: Self-tuning request pacing."""
    
    def __init__(self, config: HybridThrottleConfig):
        self.config = config
        self.current_delay = config.adaptive_min_delay
        self.success_rate = MovingAverage(config.success_window_size)
        self.error_rate = MovingAverage(config.error_window_size)
        self.session_start_time = time.time()
        self.request_count = 0
    
    def on_request_start(self):
        """Call before each API request."""
        self.request_count += 1
        
        # Check session timeout (Layer 2 boundary)
        elapsed = time.time() - self.session_start_time
        if elapsed > self.config.hard_timeout:
            raise TimeoutError(f"Hard timeout exceeded: {elapsed}s")
    
    def on_success(self):
        """Call after successful API response."""
        self.success_rate.add(1.0)
        self.error_rate.add(0.0)
        
        # Adapt: Speed up if success rate is high and errors are low
        if (self.success_rate.avg > 0.95 and 
            self.error_rate.avg < 0.01 and 
            self.success_rate.is_full):
            
            old_delay = self.current_delay
            self.current_delay *= self.config.adaptive_aggression
            self.current_delay = max(self.current_delay, self.config.adaptive_min_delay)
            
            if old_delay != self.current_delay:
                logger.debug(f"Adaptive throttle: speeding up {old_delay:.2f}s → {self.current_delay:.2f}s")
    
    def on_rate_limit(self, retry_after: Optional[int] = None):
        """Call after 429 rate limit error."""
        self.success_rate.add(0.0)
        self.error_rate.add(1.0)
        
        # Adapt: Slow down aggressively
        if retry_after:
            self.current_delay = float(retry_after)
        else:
            old_delay = self.current_delay
            self.current_delay *= 2.0  # Exponential backoff
            self.current_delay = min(self.current_delay, self.config.adaptive_max_delay)
            
            logger.warning(f"Adaptive throttle: backing off {old_delay:.2f}s → {self.current_delay:.2f}s")
    
    def get_delay(self) -> float:
        """Get delay for next request with jitter."""
        jitter = random.uniform(0.8, 1.2)
        return self.current_delay * jitter
    
    @property
    def should_continue_session(self) -> bool:
        """Check if we should continue based on target work time."""
        elapsed = time.time() - self.session_start_time
        return elapsed < self.config.max_server_use_time

class HybridThrottler:
    """
    Three-layer hybrid throttler combining fixed scheduling with adaptive pacing.
    """
    
    def __init__(self, config: Optional[HybridThrottleConfig] = None):
        self.config = config or HybridThrottleConfig()
        self.circuit_breaker = CircuitBreaker(
            threshold=self.config.circuit_breaker_threshold,
            reset_after_seconds=self.config.circuit_breaker_reset_seconds
        )
        self.request_throttler: Optional[AdaptiveRequestThrottler] = None
        self.session_stats = {
            'requests': 0,
            'successes': 0,
            'rate_limits': 0,
            'circuit_breaks': 0
        }
    
    def start_session(self) -> bool:
        """
        Layer 1: Check if we should start based on schedule.
        Returns True if session should proceed.
        """
        if self.config.schedule_type == WorkloadType.CRON_BATCH:
            # For cron jobs, trust the scheduler — just check circuit breaker
            if self.circuit_breaker.is_open:
                logger.error("Circuit breaker is open — skipping scheduled job")
                return False
        
        # Initialize Layer 3 throttler for this session
        self.request_throttler = AdaptiveRequestThrottler(self.config)
        self.session_stats = {
            'requests': 0,
            'successes': 0,
            'rate_limits': 0,
            'circuit_breaks': 0
        }
        
        logger.info(f"Session started (type: {self.config.schedule_type.value})")
        return True
    
    def execute_request(self, operation: Callable, operation_name: str = "API call"):
        """
        Execute a single API request with full three-layer protection.
        """
        if not self.request_throttler:
            raise RuntimeError("Session not started — call start_session() first")
        
        # Layer 2: Check circuit breaker
        if self.circuit_breaker.is_open:
            self.session_stats['circuit_breaks'] += 1
            raise Exception("Circuit breaker is open — too many consecutive failures")
        
        # Layer 3: Apply adaptive delay
        delay = self.request_throttler.get_delay()
        if delay > 0:
            time.sleep(delay)
        
        # Layer 3: Check session timeout
        self.request_throttler.on_request_start()
        self.session_stats['requests'] += 1
        
        try:
            result = operation()
            
            # Success path
            self.request_throttler.on_success()
            self.circuit_breaker.record_success()
            self.session_stats['successes'] += 1
            
            return result
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Detect error types
            is_rate_limit = "rate limit" in error_str or "429" in error_str
            is_auth_error = any(x in error_str for x in ["unauthorized", "forbidden", "billing", "credit"])
            
            # Auth errors — don't retry, don't circuit break
            if is_auth_error:
                logger.error(f"Auth/billing error — aborting: {e}")
                raise
            
            # Rate limits — adapt and potentially circuit break
            if is_rate_limit:
                self.session_stats['rate_limits'] += 1
                self.request_throttler.on_rate_limit()
                
                # Record for circuit breaker
                if self.circuit_breaker.record_failure():
                    logger.error(f"Circuit breaker opened due to repeated rate limits")
                
                raise
            
            # Other errors — record for circuit breaker
            if self.circuit_breaker.record_failure():
                logger.error(f"Circuit breaker opened due to repeated errors")
            
            raise
    
    def should_continue(self) -> bool:
        """Check if session should continue based on work time target."""
        if not self.request_throttler:
            return False
        return self.request_throttler.should_continue_session
    
    def end_session(self) -> dict:
        """End session and return statistics."""
        stats = self.session_stats.copy()
        stats['final_delay'] = self.request_throttler.current_delay if self.request_throttler else 0
        stats['circuit_breaker_open'] = self.circuit_breaker.is_open
        
        logger.info(f"Session ended: {stats}")
        return stats
```

### 3.2 Usage Patterns

**Pattern A: Pure Cron Job (Conservative)**
```python
config = HybridThrottleConfig(
    schedule_type=WorkloadType.CRON_BATCH,
    adaptive_min_delay=60.0,  # Conservative base
    max_server_use_time=1500   # 25 min target
)

throttler = HybridThrottler(config)

if throttler.start_session():
    while throttler.should_continue():
        try:
            result = throttler.execute_request(
                lambda: call_kimi_api(prompt),
                "Research query"
            )
            process_result(result)
        except Exception as e:
            if "Circuit breaker" in str(e):
                break  # Stop gracefully
            # Handle other errors
    
    stats = throttler.end_session()
```

**Pattern B: Pure Real-Time (Aggressive)**
```python
config = HybridThrottleConfig(
    schedule_type=WorkloadType.REALTIME,
    adaptive_min_delay=1.0,   # Aggressive base
    max_server_use_time=3600  # 1 hour max
)

throttler = HybridThrottler(config)
throttler.start_session()

# Process requests as they come
while True:
    request = get_next_request()
    result = throttler.execute_request(
        lambda: call_kimi_api(request),
        "Real-time query"
    )
    send_response(result)
```

**Pattern C: Mixed (Hybrid)**
```python
# Scheduled batch job with adaptive internal pacing
config = HybridThrottleConfig(
    schedule_type=WorkloadType.MIXED,
    adaptive_min_delay=10.0,  # Middle ground
    max_server_use_time=1500
)

throttler = HybridThrottler(config)

@cron.schedule("0 0 * * *")  # Midnight
def nightly_batch_job():
    if not throttler.start_session():
        return  # Circuit breaker open
    
    for task in get_batch_tasks():
        if not throttler.should_continue():
            logger.info("Target work time reached — stopping gracefully")
            break
        
        try:
            result = throttler.execute_request(
                lambda: process_task(task),
                f"Task {task.id}"
            )
            save_result(result)
        except Exception as e:
            logger.error(f"Task failed: {e}")
            continue  # Try next task
    
    stats = throttler.end_session()
    notify_completion(stats)
```

---

## 4. Layer-by-Layer Decision Matrix

### 4.1 When to Use Each Pattern

| Scenario | Recommended Pattern | Layers Active | Why |
|----------|-------------------|---------------|-----|
| Nightly data processing | Cron Batch | 1 + 2 + 3 (conservative) | Predictable, deadline-driven |
| Chatbot responses | Real-Time | 2 + 3 (aggressive) | Low latency priority |
| Research paper generation | Mixed | 1 + 2 + 3 (balanced) | Scheduled but wants efficiency |
| Emergency maintenance | Real-Time | 2 + 3 (aggressive) | Speed matters, schedule doesn't |
| Monthly report generation | Cron Batch | 1 + 2 + 3 (conservative) | Must complete, can wait |

### 4.2 Tuning Parameters

```python
# Conservative (High Reliability)
conservative = HybridThrottleConfig(
    adaptive_min_delay=60.0,
    adaptive_aggression=0.95,
    circuit_breaker_threshold=2,
    max_server_use_time=1500
)

# Balanced (Default)
balanced = HybridThrottleConfig(
    adaptive_min_delay=10.0,
    adaptive_aggression=0.9,
    circuit_breaker_threshold=3,
    max_server_use_time=1800
)

# Aggressive (High Throughput)
aggressive = HybridThrottleConfig(
    adaptive_min_delay=1.0,
    adaptive_aggression=0.8,
    circuit_breaker_threshold=5,
    max_server_use_time=3600
)
```

---

## 5. Monitoring and Observability

### 5.1 Key Metrics

```python
@dataclass
class HybridThrottleMetrics:
    """Metrics for monitoring hybrid throttle performance."""
    
    # Layer 1: Scheduler
    scheduled_jobs: int
    jobs_started: int
    jobs_skipped_circuit_breaker: int
    
    # Layer 2: Session Manager
    avg_session_duration: float
    sessions_circuit_broken: int
    sessions_timed_out: int
    
    # Layer 3: Request Throttler
    total_requests: int
    success_rate: float
    rate_limit_rate: float
    avg_delay: float
    min_delay_achieved: float
    max_delay_required: float
    
    def health_score(self) -> float:
        """Calculate health score 0-100."""
        score = 100.0
        
        # Penalize high error rates
        score -= self.rate_limit_rate * 200  # -20 per 10% errors
        
        # Penalize excessive delays
        if self.avg_delay > 120:
            score -= (self.avg_delay - 120) / 10
        
        # Penalize circuit breaker triggers
        score -= self.sessions_circuit_broken * 10
        
        return max(0.0, min(100.0, score))
```

### 5.2 Alerting Rules

| Condition | Severity | Action |
|-----------|----------|--------|
| Health score < 50 | Critical | Pause new jobs, alert ops |
| Circuit breaker opens 3x in 1 hour | Warning | Increase base delay |
| Avg delay > 5 min sustained | Warning | Review schedule, spread load |
| Success rate < 90% | Critical | Check API status, reduce concurrency |
| Sessions consistently hitting timeout | Info | Increase max_server_use_time or reduce work |

---

## 6. Comparison: Hybrid vs. Pure Approaches

| Metric | Pure Fixed | Pure Adaptive | Hybrid (This Paper) |
|--------|-----------|---------------|---------------------|
| Predictable completion | ✓✓✓ | ✗ | ✓✓ |
| Maximum throughput | ✗ | ✓✓✓ | ✓✓ |
| Handles traffic spikes | ✗ | ✓✓ | ✓✓ |
| Guaranteed off-peak execution | ✓✓✓ | ✗ | ✓✓✓ |
| Self-healing from 429s | ✗ | ✓✓ | ✓✓ |
| Simple to debug | ✓✓ | ✓ | ✓ |
| Handles mixed workloads | ✗ | ✓ | ✓✓✓ |

---

## 7. Implementation Checklist

### For New Systems

- [ ] Choose workload type (Cron/Real-Time/Mixed)
- [ ] Configure base delay (60s for Cron, 1s for Real-Time)
- [ ] Set session timeouts (1500s target, 1800s hard)
- [ ] Implement circuit breaker (threshold: 2-5)
- [ ] Add monitoring metrics collection
- [ ] Configure alerting thresholds
- [ ] Test failure scenarios (simulate 429s)
- [ ] Document runbook for circuit breaker reset

### For Migration from Fixed Scheduling

- [ ] Deploy HybridThrottler with `schedule_type=CRON_BATCH`
- [ ] Keep existing schedule, add adaptive layer
- [ ] Monitor for 1 week, collect metrics
- [ ] If success rate > 95%, reduce `adaptive_min_delay` by 50%
- [ ] Repeat until optimal delay found

### For Migration from Pure Adaptive

- [ ] Add Layer 1 scheduling constraints
- [ ] Implement `max_server_use_time` boundaries
- [ ] Test with off-peak scheduling
- [ ] Gradually shift real-time → scheduled where possible

---

## 8. Conclusion

The hybrid approach provides **the best of both worlds**: the reliability and predictability of fixed scheduling, combined with the efficiency and self-healing of adaptive throttling.

**Key Takeaways:**

1. **Use fixed scheduling for macro timing** — Business requirements (off-peak windows) don't adapt
2. **Use adaptive throttling for micro pacing** — API capacity varies, so request timing should too
3. **Circuit breakers bridge both layers** — Fail fast when API is unhealthy, regardless of schedule
4. **Monitor the health score** — Single metric to tune the balance between speed and reliability

**When to choose hybrid:**
- You have both batch and real-time workloads
- You need guaranteed completion but want efficiency
- You're migrating from one pattern to another
- You want future flexibility without rewrites

---

## Appendix: Quick Reference

```python
# Install dependencies
# pip install logging collections dataclasses

# Copy HybridThrottler class above
# Configure for your workload type
# Start session, execute requests, end session

# Example: Scheduled job with adaptive pacing
config = HybridThrottleConfig(
    schedule_type=WorkloadType.MIXED,
    off_peak_start_hour=0,
    off_peak_end_hour=6
)

throttler = HybridThrottler(config)

if throttler.start_session():
    while throttler.should_continue():
        try:
            result = throttler.execute_request(do_work)
        except Exception:
            continue
    stats = throttler.end_session()
```

---

**Document Version:** 1.0  
**Last Updated:** March 28, 2026  
**Next Review:** April 28, 2026

*For questions or contributions: systems@laere.enterprises*
