# Adaptive Page Replacement Based on Memory-Reference Locality
## Fall Semester 2026-27 | Case Study: CS3

**Students:** Yash Pradhan (24BCE0702), Anjini Pandey (24BCE0714)  
**Course:** BCSE303L – Operating Systems  
**Date:** October 2026  

---

## 1. Abstract
Virtual memory systems rely on page replacement policies to decide which resident page to evict during a page fault. Classic algorithms (FIFO, LRU, LFU, Clock) make fixed assumptions about program behavior that can fail when workload access patterns change. In this case study, we implemented and evaluated an online **Adaptive Page Replacement** policy that detects memory-reference locality within a rolling window. It switches between LRU, Clock, and LFU heuristics without looking ahead at future references.

We tested five baseline algorithms (FIFO, LRU, Optimal, Clock, LFU) and two adaptive configurations (W=50 and W=100) across 1,260 experimental runs covering 252 unique configurations (4 workloads × 3 sizes × 3 capacities). The adaptive engine successfully detected sequential scans and preserved frames across policy transitions. However, our fixed thresholds did not always match the workload statistics. Adaptive W50 matched LRU in 30 of 36 conditions, while LFU performed best among the online policies on high-locality workloads (38.34% vs. 30.84% hit ratio). Our results show that the adaptive approach can make policy decisions using only past references, but its performance depends strongly on how the thresholds are chosen.

## 2. Introduction & Problem Statement
When physical memory frames are full, the OS must choose a page to evict. Fixed policies assume a single type of program behavior, which leads to more page faults when workloads shift—for example, moving from a tight loop to a sequential scan. 

**Research Question:** *"Can an adaptive page-replacement policy select an appropriate strategy according to observed memory-reference locality?"*

Adaptive selection aims to improve performance by matching the replacement rule to the current phase of execution. The main challenges are identifying this phase using only past history, managing the internal state during transitions, and keeping overhead low.

## 3. Objectives
1. Implement FIFO, LRU, Optimal, Clock, and LFU page replacement algorithms.
2. Develop a causal adaptive mechanism based on a rolling observation window.
3. Validate all algorithms against a standard textbook reference string.
4. Test performance across four synthetic workloads (High Locality, Sequential, Random, Looping) at varying sizes (N) and frame capacities (C).
5. Compare adaptive and fixed policies statistically using page faults, hit ratio, and execution time.

## 4. Algorithms
- **FIFO (First-In, First-Out):** Evicts the oldest page.
- **LRU (Least Recently Used):** Evicts the page whose most recent access is oldest, taking advantage of temporal locality.
- **Optimal (Belady's MIN):** Evicts the page needed furthest in the future. This requires complete future knowledge, so it serves only as a theoretical best-case baseline.
- **Clock (Second-Chance):** Approximates LRU using a circular buffer and reference bits. 
- **LFU (Least Frequently Used):** Evicts the page with the lowest reference frequency, breaking ties using the FIFO arrival order.

## 5. Adaptive Mechanism
Our adaptive engine tracks recent page references in a rolling `deque` of size W. It evaluates two metrics:
- **Unique Page Ratio (U):** U = |unique pages in W| / W. 
- **Frequency Coefficient of Variation (CV):** Relative dispersion of access frequencies, computed as standard deviation divided by mean.

**Decision Rules:**
```python
if u_ratio < 0.35:
    selected = "LRU"    # Strong temporal locality
elif u_ratio >= 0.85:
    selected = "Clock"  # Sequential scan
elif cv_f >= 1.0 and u_ratio < 0.70:
    selected = "LFU"    # Skewed popularity
else:
    selected = "LRU"    # Default
```
The engine evaluates metrics every `max(10, W // 2)` steps. 

**Adaptive State Handover:**
When the engine switches policies, the physical resident set itself is NOT flushed. Instead, auxiliary metadata is reconstructed:
- **Switch to LRU:** Resident pages are ordered using their last occurrence in the history window.
- **Switch to LFU:** Page frequencies are initialized directly from the observation window.
- **Switch to Clock:** Reference bits are initialized to 1 and the hand is reset to 0.

**Causality Guarantee:**
The adaptive decision is made before the current reference is appended to the observation window. A causality test mutates future references and verifies that adaptive decisions before the mutation point remain unchanged.

## 6. Workloads and Experimental Setup

**Workload Types:**
1. **High Locality:** Pareto 80/20 distribution (80% accesses to 10 hot pages).
2. **Sequential:** Cyclic scan with 2% random jumps.
3. **Random:** Uniform access over all pages.
4. **Looping:** Fixed loop of 6 pages to test thrashing.

**Experimental Configuration Matrix:**
- **Workloads:** High Locality, Sequential, Random, Looping
- **N (references):** 1,000; 5,000; 20,000
- **Frames:** 3, 5, 8
- **Algorithms:** FIFO, LRU, Optimal, Clock, LFU, Adaptive W50, Adaptive W100
- **Timing repetitions:** 5 per configuration
- **Total unique configurations:** 252
- **Total experimental runs:** 1,260
- **Random seed:** 42

**Experimental Environment:**
| Component | Specification |
|:---|:---|
| CPU | Intel Core Ultra 7 155H |
| RAM | 16 GB |
| OS | Windows 11, 64-bit |
| Python | CPython 3.13.4 |
| Libraries | matplotlib 3.11.2, numpy 2.5.3 |

## 7. Validation and Testing
We wrote a test suite of 29 unit tests to verify our implementations. 

| Test File | Tests | Key Focus |
|:---|---:|:---|
| FIFO | 5 | Queue order |
| LRU | 4 | Recency updates |
| Optimal | 3 | Farthest future lookahead |
| Clock | 4 | Reference bit semantics |
| LFU | 4 | FIFO tie-breaking |
| Adaptive | 9 | causality, scan→Clock, locality→LRU |
| **Total** | **29** | |

Textbook validation was performed on the standard 20-reference string with 3 frames:

| Algorithm | Faults | Hit Ratio | Expected | Status |
|:---|---:|---:|---:|:---|
| FIFO | 15 | 25.00% | 15 | PASS |
| LRU | 12 | 40.00% | 12 | PASS |
| Optimal | 9 | 55.00% | 9 | PASS |
| Clock | 14 | 30.00% | 14 | PASS |
| LFU | 13 | 35.00% | 13 | PASS |

## 8. Results and Discussion

### Page Faults
LFU had the fewest faults among the online policies for high-locality workloads because it effectively protected the "hot" pages. Adaptive W50 matched LRU in 30 out of 36 configurations, achieving slightly fewer faults in the remaining 6. It was never worse than LRU. 

Below are representative page-fault results across the workload classes for N=5,000 and 5 frames (8 frames for Looping):

| Workload | N | Frames | FIFO | LRU | Optimal | Clock | LFU | Adap W50 | Adap W100 |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| High Locality | 5000 | 5 | 3495 | 3458 | 2167 | 3494 | 3083 | 3458 | 3458 |
| Sequential | 5000 | 5 | 4964 | 4962 | 4431 | 4964 | 4650 | 4962 | 4962 |
| Random | 5000 | 5 | 4505 | 4502 | 3409 | 4505 | 4519 | 4502 | 4502 |
| Looping | 5000 | 5 | 5000 | 5000 | 1004 | 5000 | 5000 | 5000 | 5000 |
| Looping | 5000 | 8 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |

Under the random workload, LRU slightly outperformed LFU (4,502 vs. 4,519 faults), which is consistent with the lack of persistent hot pages in a uniform access pattern.

For the high-locality (N=5000, C=5) configuration shown above, LFU achieved a 38.34% hit ratio. LRU, Adaptive W50, and Adaptive W100 all reached a 30.84% hit ratio, while Optimal achieved 56.66%.

![Hit Ratio vs Algorithm](../plots/hit_ratio_vs_algorithm.png)
*Figure 1: Hit Ratio vs Algorithm (High Locality, N=5,000, Frames=5).*

![Adaptive vs Fixed Policies](../plots/adaptive_vs_fixed_policies.png)
*Figure 2: Adaptive vs Fixed Policies across all workloads.*

### Adaptive Behavior
For sequential workloads (N=20,000, W=50), the adaptive engine made 312 total policy transitions, consisting of 156 transitions to Clock and 156 transitions back to LRU. This oscillation happened because the 2% random jumps briefly dropped the U ratio below the 0.85 threshold.

For high-locality windows, the classifier typically selected LRU through the first U-ratio condition before the LFU rule could be reached. The observed CV of about 0.97 also remained below the LFU threshold of 1.0.

There are 50 possible pages in the workload generator. With W=100, the maximum possible unique-page ratio is therefore 50/100 = 0.50, so the U >= 0.85 Clock condition is unreachable for W100. For high-locality windows, the U < 0.35 condition is evaluated before the LFU condition, so LRU is selected whenever the window is classified as strongly local. As a result, Adaptive W100 selected LRU across all 36 W100 configurations.

![Adaptive Behavior by Workload](../plots/adaptive_behavior_by_workload.png)
*Figure 3: Adaptive W50 Behavior (N=5,000, Frames=5). Sequential workloads triggered transitions, but hit ratios remained unaffected.*

### Overall Hit Ratio and Execution Time
Across the full 36-condition summary, Optimal gave the highest mean hit ratio, while FIFO and LRU had the lowest execution overhead. The adaptive variants remained close to LRU in hit ratio but added substantial computational cost.

| Algorithm | Mean Hit Ratio | Mean Execution Time (ms) |
|:---|---:|---:|
| Optimal | 43.34% | 8.082 |
| LFU | 22.87% | 15.816 |
| LRU | 19.45% | 3.507 |
| Adaptive W50 | 19.46% | 18.971 |
| Adaptive W100 | 19.45% | 16.122 |
| Clock | 19.26% | 9.219 |
| FIFO | 19.10% | 2.392 |

Statistical observation: Page-fault counts were deterministic across the five repetitions for each configuration, so their standard deviation was 0. Execution time was measured across the five repetitions and summarized using the mean; variation was retained in the timing plots where applicable.

Execution time increased approximately linearly over the tested workload sizes. The adaptive engines introduced significant overhead: Adaptive W50 took ≈ 5.4× the execution time of LRU, while W100 took ≈ 4.6× LRU due to frequency counting and variance calculations on the rolling window.

![Execution Time vs Algorithm](../plots/execution_time_vs_algorithm.png)
*Figure 4: Execution Time overhead (High Locality, N=20,000, Frames=8).*

### Belady's Anomaly
We reproduced Belady's Anomaly using a classic textbook string, where FIFO faults increased from 9 faults with 3 frames to 10 faults with 4 frames. However, across our synthetic workload simulations, we did not observe the anomaly; faults decreased monotonically as frames increased.

## 9. Limitations
1. **Heuristic Calibration:** The manual U and CV thresholds were slightly misaligned with the actual workload statistics. For instance, LFU was never selected for high-locality workloads despite being the best-performing fixed online policy in the tested high-locality configurations.
2. **Simulation Overhead:** Time measurements reflect Python interpreter costs rather than kernel-level execution or hardware MMU support.
3. **Workload Scope:** We tested specific synthetic access patterns, whereas real-world traces often exhibit more complex phase behavior.

## 10. Contributions
- **Yash Pradhan (24BCE0702):** Implemented FIFO, LRU, Optimal; created their unit tests; designed the workload generator logic.
- **Anjini Pandey (24BCE0714):** Implemented Clock, LFU, Adaptive engine; developed causal unit tests; executed batch runs; wrote statistical aggregator and plotting pipeline.

## 11. Conclusion
Our adaptive engine successfully tracked memory-reference phases and handled state transitions causally without flushing physical frames. However, because the U < 0.35 locality condition is checked before the LFU condition, the adaptive policy predominantly defaulted to LRU on strongly local windows. The observed CV of about 0.97 was also below the LFU threshold of 1.0. Consequently, LFU remained the superior fixed policy for skewed access patterns. We conclude that while adaptive page replacement can effectively switch logic on the fly, its practical advantage is entirely dependent on precise, workload-specific threshold calibration.

## 12. Repository and Reproducibility
**GitHub Repository:** [https://github.com/yoswinner/Adaptive-Page-Replacement-Case-Study-3](https://github.com/yoswinner/Adaptive-Page-Replacement-Case-Study-3)

This project was designed, implemented, tested, and evaluated as part of our coursework, and all reported numerical results were generated directly from the project's experimental implementation.

## 13. References
1. Silberschatz, A., Galvin, P. B., Gagne, G. *Operating System Concepts*, 10th ed., Wiley, 2018.
2. Belady, L. A., Nelson, R. A., Shedler, G. S. "An anomaly in space-time characteristics of certain programs running in a paging machine," *CACM*, 1969.
3. Denning, P. J. "The working set model for program behavior," *CACM*, 1968.
