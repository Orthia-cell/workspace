"""
Spaced Repetition Scheduler
Implements adaptive scheduling based on forgetting curve research.

Based on: Ebbinghaus (1885), Wozniak (SuperMemo), Cambridge (2020)
"""

import math
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MemoryItem:
    """Represents a piece of information being tracked."""
    id: str
    content: str
    created_at: datetime
    difficulty: float = 1.0  # 1.0 = normal, higher = harder
    last_reviewed: Optional[datetime] = None
    review_count: int = 0
    
    def days_since_created(self) -> float:
        return (datetime.now() - self.created_at).total_seconds() / 86400
    
    def days_since_reviewed(self) -> Optional[float]:
        if self.last_reviewed is None:
            return None
        return (datetime.now() - self.last_reviewed).total_seconds() / 86400


class SpacedRepetitionScheduler:
    """
    Implements spaced repetition scheduling using adaptive intervals.
    
    Standard schedule: Day 1, 3, 7, 14, 30, 60, 120...
    Each successful review extends the interval.
    """
    
    BASE_INTERVALS = [1, 3, 7, 14, 30, 60, 120, 240]
    
    def __init__(self, base_intervals: Optional[List[int]] = None):
        self.intervals = base_intervals or self.BASE_INTERVALS
        
    def calculate_next_review(self, item: MemoryItem, 
                             performance: float = 1.0) -> datetime:
        """
        Calculate next review date based on performance.
        
        Args:
            item: The memory item
            performance: 0.0-1.0 score (1.0 = perfect recall)
            
        Returns:
            datetime of next recommended review
        """
        # Get base interval
        if item.review_count < len(self.intervals):
            base_days = self.intervals[item.review_count]
        else:
            # Exponential growth after base intervals
            base_days = self.intervals[-1] * (2 ** (item.review_count - len(self.intervals) + 1))
        
        # Adjust for difficulty and performance
        adjusted_days = base_days * performance / item.difficulty
        adjusted_days = max(1, adjusted_days)  # Minimum 1 day
        
        if item.last_reviewed:
            return item.last_reviewed + timedelta(days=adjusted_days)
        return item.created_at + timedelta(days=adjusted_days)
    
    def should_review(self, item: MemoryItem) -> bool:
        """Check if item is due for review."""
        next_review = self.calculate_next_review(item)
        return datetime.now() >= next_review
    
    def get_priority_score(self, item: MemoryItem) -> float:
        """
        Calculate priority score (higher = more urgent).
        Based on forgetting curve urgency.
        """
        days_since = item.days_since_reviewed() or item.days_since_created()
        next_review = self.calculate_next_review(item)
        days_until = (next_review - datetime.now()).total_seconds() / 86400
        
        # Overdue items get high priority
        if days_until < 0:
            return 100 + abs(days_until)
        
        # Items approaching review get moderate priority
        return max(0, 100 - days_until * 10)


class ForgettingCurveModel:
    """
    Models the Ebbinghaus forgetting curve.
    R(t) = R_0 * e^(-t/S)
    Where R is retention, t is time, S is stability
    """
    
    def __init__(self, initial_retention: float = 1.0, stability: float = 1.0):
        self.R0 = initial_retention
        self.S = stability
        
    def retention_at_time(self, hours: float) -> float:
        """Calculate expected retention after given hours."""
        return self.R0 * math.exp(-hours / (self.S * 24))
    
    def time_for_retention(self, target_retention: float) -> float:
        """Calculate hours until retention drops to target."""
        if target_retention <= 0 or target_retention >= self.R0:
            return 0
        return -self.S * 24 * math.log(target_retention / self.R0)
    
    def optimal_review_time(self, min_retention: float = 0.3) -> float:
        """
        Calculate optimal review time (hours).
        Review when retention drops to min_retention (default 30%).
        """
        return self.time_for_retention(min_retention)


# Example usage and testing
if __name__ == "__main__":
    # Create sample items
    now = datetime.now()
    
    items = [
        MemoryItem("1", "Memory encoding principles", now - timedelta(days=5)),
        MemoryItem("2", "Forgetting curve formula", now - timedelta(days=2), difficulty=1.2),
        MemoryItem("3", "Semantic network theory", now - timedelta(days=10), difficulty=0.8),
    ]
    
    # Mark some as reviewed
    items[0].last_reviewed = now - timedelta(days=2)
    items[0].review_count = 1
    
    scheduler = SpacedRepetitionScheduler()
    
    print("=" * 60)
    print("SPACED REPETITION SCHEDULER")
    print("=" * 60)
    
    for item in items:
        next_review = scheduler.calculate_next_review(item)
        priority = scheduler.get_priority_score(item)
        due = "OVERDUE" if scheduler.should_review(item) else "OK"
        
        print(f"\nItem: {item.content[:40]}...")
        print(f"  Difficulty: {item.difficulty}")
        print(f"  Reviews: {item.review_count}")
        print(f"  Next review: {next_review.strftime('%Y-%m-%d')}")
        print(f"  Priority: {priority:.1f} [{due}]")
    
    # Forgetting curve visualization
    print("\n" + "=" * 60)
    print("FORGETTING CURVE MODEL")
    print("=" * 60)
    
    model = ForgettingCurveModel(stability=2.0)
    
    print("\nRetention over time (no review):")
    for hours in [1, 6, 24, 72, 168, 720]:
        retention = model.retention_at_time(hours)
        days = hours / 24
        print(f"  {days:5.1f} days: {retention*100:5.1f}% retention")
    
    optimal = model.optimal_review_time(0.3)
    print(f"\nOptimal review time (30% threshold): {optimal/24:.1f} days")
