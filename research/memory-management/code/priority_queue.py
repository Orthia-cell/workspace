"""
Multi-Tier Memory Management System
Implements priority-based memory with retirement mechanisms.

Based on: Visual Working Memory research, Homeostatic Plasticity, AI Memory Systems
"""

import heapq
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import json


class MemoryTier(Enum):
    """Memory tiers with different characteristics."""
    WORKING = 1      # Immediate, high fidelity, small capacity
    EPISODIC = 2     # Context-rich, specific events
    SEMANTIC = 3     # Abstract knowledge, long-term
    ARCHIVE = 4      # Cold storage, rarely accessed


@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""
    id: str
    content: str
    tier: MemoryTier
    created_at: float
    last_accessed: float
    access_count: int = 0
    priority_score: float = 1.0
    connections: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    # Retirement criteria
    failed_retrievals: int = 0
    last_retrieval_success: Optional[float] = None
    
    def __lt__(self, other):
        # For priority queue ordering
        return self.priority_score > other.priority_score


class MultiTierMemoryManager:
    """
    Implements a multi-tier memory system with:
    - Dynamic prioritization
    - Automatic retirement
    - Cross-tier promotion/demotion
    - Connection tracking
    """
    
    def __init__(self, 
                 working_capacity: int = 7,
                 episodic_capacity: int = 100,
                 semantic_capacity: int = 10000,
                 retirement_threshold: float = 0.1):
        
        self.capacities = {
            MemoryTier.WORKING: working_capacity,
            MemoryTier.EPISODIC: episodic_capacity,
            MemoryTier.SEMANTIC: semantic_capacity,
            MemoryTier.ARCHIVE: float('inf')
        }
        
        self.retirement_threshold = retirement_threshold
        self.memories: Dict[str, MemoryEntry] = {}
        self.tiers: Dict[MemoryTier, List[str]] = {
            tier: [] for tier in MemoryTier
        }
        
        # Statistics
        self.stats = {
            'promotions': 0,
            'demotions': 0,
            'retirements': 0,
            'accesses': 0
        }
    
    def add_memory(self, memory_id: str, content: str, 
                   initial_tier: MemoryTier = MemoryTier.EPISODIC,
                   connections: Optional[List[str]] = None,
                   metadata: Optional[Dict] = None) -> MemoryEntry:
        """Add a new memory to the system."""
        now = time.time()
        
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            tier=initial_tier,
            created_at=now,
            last_accessed=now,
            connections=connections or [],
            metadata=metadata or {}
        )
        
        self.memories[memory_id] = entry
        self.tiers[initial_tier].append(memory_id)
        
        # Enforce capacity constraints
        self._enforce_capacity(initial_tier)
        
        return entry
    
    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Attempt to retrieve a memory.
        Updates statistics and may trigger tier changes.
        """
        if memory_id not in self.memories:
            # Track failed retrieval if we have partial match
            self._handle_failed_retrieval(memory_id)
            return None
        
        entry = self.memories[memory_id]
        now = time.time()
        
        # Update access stats
        entry.last_accessed = now
        entry.access_count += 1
        entry.last_retrieval_success = now
        entry.failed_retrievals = 0
        
        self.stats['accesses'] += 1
        
        # Recalculate priority
        self._update_priority(entry)
        
        # Consider promotion
        self._consider_promotion(entry)
        
        return entry
    
    def _update_priority(self, entry: MemoryEntry):
        """Calculate priority score based on multiple factors."""
        now = time.time()
        
        # Base factors
        recency = 1.0 / (1 + (now - entry.last_accessed) / 86400)  # Decay per day
        frequency = min(1.0, entry.access_count / 10)  # Cap at 10 accesses
        connectivity = min(1.0, len(entry.connections) / 5)  # Cap at 5 connections
        
        # Age factor (newer items get slight boost)
        age_days = (now - entry.created_at) / 86400
        age_factor = 1.0 / (1 + age_days / 30)  # Decay over months
        
        # Combine factors
        entry.priority_score = (
            recency * 0.4 +
            frequency * 0.3 +
            connectivity * 0.2 +
            age_factor * 0.1
        )
    
    def _consider_promotion(self, entry: MemoryEntry):
        """Promote frequently accessed items to higher tiers."""
        if entry.tier == MemoryTier.WORKING:
            return  # Already highest
        
        # Promotion criteria
        if entry.access_count >= 3 and entry.priority_score > 0.7:
            new_tier = MemoryTier(entry.tier.value - 1)
            self._change_tier(entry, new_tier)
            self.stats['promotions'] += 1
    
    def _consider_demotion(self, entry: MemoryEntry):
        """Demote infrequently accessed items."""
        if entry.tier == MemoryTier.ARCHIVE:
            return  # Already lowest
        
        now = time.time()
        days_since_access = (now - entry.last_accessed) / 86400
        
        # Demotion criteria
        if days_since_access > 30 or entry.priority_score < 0.2:
            new_tier = MemoryTier(entry.tier.value + 1)
            self._change_tier(entry, new_tier)
            self.stats['demotions'] += 1
    
    def _change_tier(self, entry: MemoryEntry, new_tier: MemoryTier):
        """Move memory between tiers."""
        if entry.tier == new_tier:
            return
        
        self.tiers[entry.tier].remove(entry.id)
        entry.tier = new_tier
        self.tiers[new_tier].append(entry.id)
        
        # Enforce capacity in new tier
        self._enforce_capacity(new_tier)
    
    def _enforce_capacity(self, tier: MemoryTier):
        """Ensure tier doesn't exceed capacity."""
        capacity = self.capacities[tier]
        tier_memories = self.tiers[tier]
        
        if len(tier_memories) <= capacity:
            return
        
        # Sort by priority and demote lowest
        entries = [self.memories[mid] for mid in tier_memories]
        entries.sort(key=lambda e: e.priority_score)
        
        to_demote = entries[:-capacity]  # Remove lowest priority
        for entry in to_demote:
            self._consider_demotion(entry)
    
    def _handle_failed_retrieval(self, memory_id: str):
        """Track failed retrieval attempts for existing memories."""
        # Find similar memories and increase their failed count
        for entry in self.memories.values():
            if memory_id in entry.connections or memory_id in entry.content:
                entry.failed_retrievals += 1
                
                # Consider retirement after repeated failures
                if entry.failed_retrievals >= 3:
                    self._consider_retirement(entry)
    
    def _consider_retirement(self, entry: MemoryEntry):
        """Retire memories that are no longer useful."""
        now = time.time()
        days_since_success = float('inf')
        if entry.last_retrieval_success:
            days_since_success = (now - entry.last_retrieval_success) / 86400
        
        # Retirement criteria
        should_retire = (
            entry.failed_retrievals >= 5 or
            (days_since_success > 90 and entry.access_count < 3) or
            entry.priority_score < self.retirement_threshold
        )
        
        if should_retire and entry.tier != MemoryTier.ARCHIVE:
            self._change_tier(entry, MemoryTier.ARCHIVE)
            self.stats['retirements'] += 1
    
    def get_tier_contents(self, tier: MemoryTier) -> List[MemoryEntry]:
        """Get all memories in a specific tier."""
        return [self.memories[mid] for mid in self.tiers[tier]]
    
    def get_high_priority_items(self, n: int = 10) -> List[MemoryEntry]:
        """Get top N highest priority items across all tiers."""
        all_entries = list(self.memories.values())
        all_entries.sort(key=lambda e: e.priority_score, reverse=True)
        return all_entries[:n]
    
    def maintenance_cycle(self):
        """
        Run maintenance: update priorities, enforce capacities, retire old items.
        Should be called periodically (e.g., daily).
        """
        now = time.time()
        
        for entry in list(self.memories.values()):
            # Update priority based on decay
            self._update_priority(entry)
            
            # Check for demotion/retirement
            days_since_access = (now - entry.last_accessed) / 86400
            
            if days_since_access > 7:
                self._consider_demotion(entry)
            
            if days_since_access > 30:
                self._consider_retirement(entry)
        
        # Enforce all capacities
        for tier in MemoryTier:
            self._enforce_capacity(tier)
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        tier_counts = {tier.name: len(ids) for tier, ids in self.tiers.items()}
        
        return {
            'total_memories': len(self.memories),
            'tier_distribution': tier_counts,
            **self.stats
        }


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("MULTI-TIER MEMORY MANAGER DEMO")
    print("=" * 60)
    
    # Create manager
    manager = MultiTierMemoryManager(
        working_capacity=5,
        episodic_capacity=10,
        semantic_capacity=50
    )
    
    # Add memories with different characteristics
    memories = [
        ("m1", "Critical API endpoint", ["api", "critical"]),
        ("m2", "Meeting notes from yesterday", ["meeting", "recent"]),
        ("m3", "Project architecture overview", ["architecture", "project"]),
        ("m4", "Coffee shop WiFi password", ["wifi", "misc"]),
        ("m5", "Research paper on memory", ["research", "memory"]),
        ("m6", "Old phone number", ["contact", "old"]),
        ("m7", "Current project deadline", ["deadline", "urgent"]),
    ]
    
    for mid, content, connections in memories:
        manager.add_memory(mid, content, 
                         initial_tier=MemoryTier.EPISODIC,
                         connections=connections)
    
    print(f"\nAdded {len(memories)} memories")
    
    # Simulate access patterns
    print("\n" + "-" * 40)
    print("SIMULATING ACCESS PATTERNS")
    print("-" * 40)
    
    # Frequently access some items
    frequent_items = ["m1", "m3", "m7"]
    for _ in range(5):
        for mid in frequent_items:
            manager.retrieve(mid)
    
    # Occasionally access others
    occasional_items = ["m2", "m5"]
    for mid in occasional_items:
        manager.retrieve(mid)
    
    # Never access: m4, m6 (will be candidates for demotion)
    
    print("\nAccess patterns:")
    print("  High frequency: m1, m3, m7 (5x each)")
    print("  Medium frequency: m2, m5 (1x each)")
    print("  Low frequency: m4, m6 (0x)")
    
    # Run maintenance
    manager.maintenance_cycle()
    
    # Show results
    print("\n" + "-" * 40)
    print("MEMORY DISTRIBUTION AFTER ACCESS:")
    print("-" * 40)
    
    for tier in MemoryTier:
        entries = manager.get_tier_contents(tier)
        if entries:
            print(f"\n{tier.name} ({len(entries)} items):")
            for entry in entries:
                print(f"  {entry.id}: '{entry.content[:30]}...' "
                      f"(score: {entry.priority_score:.3f}, "
                      f"accesses: {entry.access_count})")
    
    # Show high priority items
    print("\n" + "-" * 40)
    print("TOP 5 HIGH PRIORITY ITEMS:")
    print("-" * 40)
    
    top_items = manager.get_high_priority_items(5)
    for i, entry in enumerate(top_items, 1):
        print(f"{i}. {entry.id} [{entry.tier.name}] "
              f"(score: {entry.priority_score:.3f})")
        print(f"   '{entry.content}'")
    
    # Show stats
    print("\n" + "-" * 40)
    print("SYSTEM STATISTICS:")
    print("-" * 40)
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
