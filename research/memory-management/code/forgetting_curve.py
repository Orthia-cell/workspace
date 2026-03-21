"""
Forgetting Curve Visualization and Analysis
Implements Ebbinghaus forgetting curve models.
"""

import numpy as np
import json
from datetime import datetime
from typing import List, Tuple, Optional


class ForgettingCurveModel:
    """
    Models the Ebbinghaus forgetting curve.
    
    The forgetting curve follows exponential decay:
    R(t) = R_0 * e^(-t/S)
    
    Where:
    - R(t) is retention at time t
    - R_0 is initial retention (typically 1.0)
    - S is the stability factor (memory strength)
    - t is time (in hours or days)
    """
    
    def __init__(self, initial_retention: float = 1.0, stability_days: float = 2.0):
        """
        Initialize forgetting curve model.
        
        Args:
            initial_retention: Starting retention level (0-1)
            stability_days: Memory stability in days (higher = more stable)
        """
        self.R0 = initial_retention
        self.S = stability_days
        
    def retention_at_time(self, days: float) -> float:
        """Calculate expected retention after given days."""
        return self.R0 * np.exp(-days / self.S)
    
    def time_for_retention(self, target_retention: float) -> float:
        """Calculate days until retention drops to target level."""
        if target_retention <= 0 or target_retention >= self.R0:
            return 0
        return -self.S * np.log(target_retention / self.R0)
    
    def optimal_review_time(self, min_retention: float = 0.3) -> float:
        """
        Calculate optimal review time.
        
        Args:
            min_retention: Review when retention drops to this level
            
        Returns:
            Days until review is optimal
        """
        return self.time_for_retention(min_retention)
    
    def get_retention_schedule(self, days: List[float]) -> List[Tuple[float, float]]:
        """Get retention values for a schedule of days."""
        return [(d, self.retention_at_time(d)) for d in days]
    
    def simulate_spaced_repetition(self, 
                                   review_schedule: List[float],
                                   retention_boost: float = 0.9) -> List[Tuple[float, float, float]]:
        """
        Simulate retention with spaced repetition reviews.
        
        Args:
            review_schedule: List of days when reviews occur
            retention_boost: Retention level after each review
            
        Returns:
            List of (day, retention_before, retention_after)
        """
        results = []
        current_stability = self.S
        
        for review_day in review_schedule:
            # Calculate retention just before review
            retention_before = self.retention_at_time(review_day)
            
            # Reset after review (with increased stability)
            self.R0 = retention_boost
            current_stability *= 1.5  # Each review strengthens memory
            self.S = current_stability
            
            results.append((review_day, retention_before, retention_boost))
        
        return results


class ComparativeAnalysis:
    """Compare different memory retention strategies."""
    
    STRATEGIES = {
        'cramming': {'initial_stability': 0.5, 'boost': 0.6},
        'poor_review': {'initial_stability': 1.0, 'boost': 0.7},
        'standard': {'initial_stability': 2.0, 'boost': 0.9},
        'excellent': {'initial_stability': 3.0, 'boost': 0.95},
    }
    
    @classmethod
    def compare_strategies(cls, days: List[float]) -> dict:
        """Compare retention across different strategies."""
        results = {}
        
        for name, params in cls.STRATEGIES.items():
            model = ForgettingCurveModel(
                stability_days=params['initial_stability']
            )
            schedule = model.get_retention_schedule(days)
            results[name] = schedule
        
        return results
    
    @classmethod
    def print_comparison(cls, days: List[float]):
        """Print formatted comparison table."""
        results = cls.compare_strategies(days)
        
        print("\n" + "=" * 80)
        print("MEMORY RETENTION STRATEGY COMPARISON")
        print("=" * 80)
        print(f"\n{'Day':>6}", end="")
        for name in cls.STRATEGIES.keys():
            print(f"{name:>15}", end="")
        print()
        print("-" * 80)
        
        for i, day in enumerate(days):
            print(f"{day:>6.0f}", end="")
            for name in cls.STRATEGIES.keys():
                retention = results[name][i][1] * 100
                print(f"{retention:>14.1f}%", end="")
            print()


class EbbinghausData:
    """Original Ebbinghaus experimental data points."""
    
    # From Ebbinghaus (1885) - retention after learning nonsense syllables
    ORIGINAL_DATA = [
        (0, 100),      # Immediate
        (20, 58),      # 20 minutes
        (60, 44),      # 1 hour
        (480, 36),     # 8 hours
        (1440, 34),    # 1 day
        (2880, 28),    # 2 days
        (10080, 25),   # 1 week
        (30240, 21),   # 1 month
    ]
    
    @classmethod
    def get_data(cls) -> List[Tuple[float, float]]:
        """Get original Ebbinghaus data (minutes, retention %)."""
        return cls.ORIGINAL_DATA
    
    @classmethod
    def fit_curve(cls) -> ForgettingCurveModel:
        """Fit a forgetting curve model to Ebbinghaus data."""
        # Convert minutes to days
        days = [m / 1440 for m, _ in cls.ORIGINAL_DATA[1:]]  # Skip t=0
        retentions = [r / 100 for _, r in cls.ORIGINAL_DATA[1:]]
        
        # Simple curve fitting (find best S)
        best_s = None
        best_error = float('inf')
        
        for s in np.linspace(0.5, 5.0, 100):
            model = ForgettingCurveModel(stability_days=s)
            predicted = [model.retention_at_time(d) for d in days]
            error = sum((p - r) ** 2 for p, r in zip(predicted, retentions))
            
            if error < best_error:
                best_error = error
                best_s = s
        
        return ForgettingCurveModel(stability_days=best_s)


# Example usage and analysis
if __name__ == "__main__":
    print("=" * 80)
    print("FORGETTING CURVE ANALYSIS")
    print("=" * 80)
    
    # 1. Basic curve demonstration
    print("\n" + "-" * 60)
    print("1. BASIC FORGETTING CURVE (Stability = 2 days)")
    print("-" * 60)
    
    model = ForgettingCurveModel(stability_days=2.0)
    
    print("\nRetention without review:")
    days_list = [0, 0.04, 0.25, 1, 2, 3, 7, 14, 30]
    labels = ['Now', '1 hour', '6 hours', '1 day', '2 days', 
              '3 days', '1 week', '2 weeks', '1 month']
    
    for day, label in zip(days_list, labels):
        retention = model.retention_at_time(day) * 100
        bar = "█" * int(retention / 5)
        print(f"{label:>10}: {retention:>5.1f}% {bar}")
    
    # 2. Spaced repetition simulation
    print("\n" + "-" * 60)
    print("2. SPACED REPETITION SIMULATION")
    print("-" * 60)
    
    review_schedule = [1, 3, 7, 14, 30]
    
    model = ForgettingCurveModel(stability_days=1.0)
    results = model.simulate_spaced_repetition(review_schedule, retention_boost=0.9)
    
    print("\nStandard schedule: Day 1, 3, 7, 14, 30")
    print(f"{'Review #':>10} {'Day':>6} {'Before Review':>15} {'After Review':>15}")
    print("-" * 50)
    
    for i, (day, before, after) in enumerate(results, 1):
        print(f"{i:>10} {day:>6.0f} {before*100:>14.1f}% {after*100:>14.1f}%")
    
    # 3. Optimal review timing
    print("\n" + "-" * 60)
    print("3. OPTIMAL REVIEW TIMING")
    print("-" * 60)
    
    model = ForgettingCurveModel(stability_days=2.0)
    
    for threshold in [0.5, 0.3, 0.2]:
        optimal = model.optimal_review_time(threshold)
        print(f"Review at {threshold*100:.0f}% retention: {optimal:.1f} days")
    
    # 4. Strategy comparison
    ComparativeAnalysis.print_comparison([1, 3, 7, 14, 30])
    
    # 5. Fit to original Ebbinghaus data
    print("\n" + "=" * 80)
    print("FIT TO ORIGINAL EBBINGHAUS DATA (1885)")
    print("=" * 80)
    
    fitted_model = EbbinghausData.fit_curve()
    print(f"\nBest fit stability: {fitted_model.S:.2f} days")
    print(f"{'Time':>12} {'Original':>12} {'Fitted':>12} {'Error':>10}")
    print("-" * 50)
    
    for minutes, original in EbbinghausData.ORIGINAL_DATA[1:]:
        days = minutes / 1440
        fitted = fitted_model.retention_at_time(days) * 100
        error = fitted - original
        time_str = f"{minutes/60:.1f}h" if minutes < 1440 else f"{days:.0f}d"
        print(f"{time_str:>12} {original:>11.1f}% {fitted:>11.1f}% {error:>+9.1f}%")
