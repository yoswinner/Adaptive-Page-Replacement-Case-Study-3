"""
Common definitions and data structures for Page Replacement Simulation.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class PageReplacementResult:
    algorithm: str
    workload_type: str = "custom"
    reference_count: int = 0
    frame_capacity: int = 0
    page_faults: int = 0
    page_hits: int = 0
    hit_ratio: float = 0.0
    execution_time_sec: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "algorithm": self.algorithm,
            "workload_type": self.workload_type,
            "reference_count": self.reference_count,
            "frame_capacity": self.frame_capacity,
            "page_faults": self.page_faults,
            "page_hits": self.page_hits,
            "hit_ratio": round(self.hit_ratio, 6),
            "execution_time_sec": round(self.execution_time_sec, 8),
        }
        for k, v in self.metadata.items():
            res[k] = v
        return res
