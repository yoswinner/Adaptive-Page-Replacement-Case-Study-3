# CS3 – Adaptive Page Replacement

**Course:** BCSE303L – Operating Systems · **Semester:** Fall Semester 2026-27

**Students:**
- 24BCE0702 – Yash Pradhan
- 24BCE0714 – Anjini Pandey

---

## 1. Introduction

With demand paging, a process can run while only some of its pages are in physical frames. When a page that is not resident is referenced, a **page fault** happens. If every frame is already full, the OS has to choose a resident page to evict. A fault costs a secondary-storage access, which is several orders of magnitude slower than a memory access, so the replacement policy has a direct effect on performance.

Classic policies each build in one assumption about future references. FIFO assumes old pages are no longer needed, LRU assumes recency predicts reuse, LFU assumes popularity predicts reuse, and Clock is a cheap approximation of LRU. Real programs move between phases (tight loops, scans, irregular access), so no single assumption holds all the time. This case study builds and measures an **online, causal adaptive policy**. It observes recent references and switches among fixed policies, and we compare it with five baselines under controlled, reproducible workloads.

## 2. Problem Statement and Objectives

**Research question:** *Can an adaptive page-replacement policy select an appropriate strategy according to observed memory-reference locality, using only past references?*

**Objectives**
1. Implement FIFO, LRU, Optimal (Belady's MIN), Clock (second chance) and LFU, and validate them on the standard textbook reference string.
2. Design an adaptive policy that uses only observed history (no future references, no hindsight, no use of Optimal) and keeps the resident frames when it switches policy.
3. Generate four reproducible workloads (seed 42): high-locality, sequential, uniform random and looping.
4. Measure page faults, hit ratio and execution time over N ∈ {1000, 5000, 20000}, frames ∈ {3, 5, 8} and window W ∈ {50, 100}, with 5 repetitions per configuration.
5. Report the trade-offs honestly, including the cases where the adaptive policy brings no benefit.

## 3. Page Replacement Algorithms

Every simulator returns faults, hits, hit ratio = hits / N and the execution time measured with `time.perf_counter()`.

| Policy | Victim on a fault with full frames | Implementation (`src/`) |
|---|---|---|
| **FIFO** | The page that has been resident longest, whatever its use | `deque` queue + `set`; O(1) |
| **LRU** | The page whose last reference is oldest | `OrderedDict`; a hit calls `move_to_end`; O(1) |
| **Optimal** | The page whose next use is farthest in the future (or never) | Per-page queues of future positions; **offline benchmark only** |
| **Clock** | Circular buffer with a reference bit per frame. The hand clears bits that are 1 and evicts the first frame whose bit is 0 | A hit sets the bit and does not move the hand; on a fill or replacement the hand advances |
| **LFU** | The resident page with the lowest reference count; ties go to the earliest-loaded page (FIFO tie-break) | Count starts at 1 when a page is loaded and is discarded on eviction |

Optimal needs the whole future reference string. It cannot be implemented in a real OS and we use it only as a lower bound on faults. The audit confirmed that no online policy had fewer faults than Optimal in any of the 252 configurations.

## 4. Adaptive Page Replacement Mechanism

`src/adaptive.py` (`AdaptiveEngine`) processes one reference at a time through `reference(page, step)`. It never has access to the rest of the reference string.

**Rolling window.** A `deque(maxlen=W)` holds the last W references that have already happened. The current reference is appended only after any policy decision for that step, so each decision depends only on references 0 … t−1.

**Unique-page ratio.** U = (distinct pages in the window) / (window length). A low U means a few pages are reused heavily (strong temporal locality). A U close to 1 means almost every reference is to a new page, which is how a scan looks.

**Frequency / skew.** For the pages in the window with counts f₁…f_k, CV = σ_f / μ_f (population standard deviation divided by the mean). A high CV means a few pages take most of the references (skewed popularity). A low CV means the references are spread evenly.

**Policy switching.** Decisions are made only once the window is full, and then at every step where step mod max(10, ⌊W/2⌋) = 0, which is every 25 references for W=50 and every 50 for W=100:

| Condition (evaluated in order) | Selected policy | Rationale |
|---|---|---|
| U < 0.35 | LRU | strong temporal locality |
| U ≥ 0.85 | Clock | scan-like, high diversity |
| CV ≥ 1.0 and U < 0.70 | LFU | skewed popularity, moderate diversity |
| otherwise | LRU | default (also the initial policy) |

FIFO handover code is present, but no rule ever selects FIFO.

**State handover.** A switch never flushes memory. The resident set stays exactly as it is, and only the new policy's metadata is rebuilt from the resident set and the window:
- **→ LRU:** resident pages are ordered by their last position in the window. Pages that are not in the window are placed as least recent.
- **→ LFU:** each resident page's count is set to its window count, with a minimum of 1.
- **→ Clock:** every resident page gets reference bit 1 and the hand is reset to 0.
- **→ FIFO:** the queue is rebuilt from the resident set.

So a switch causes no extra faults by itself. Only later eviction decisions change.

**Causality verification.** (i) Code inspection: `adaptive.py` does not import or call Optimal, and it reads no reference beyond the current one. (ii) A future-perturbation test: we replaced every reference after step k with unrelated pages, and the fault count, active policy and resident set at every step before k stayed identical. This held in 120 audit cases (4 workloads × 2 window sizes × 3 frame counts × 5 values of k) and is now a permanent unit test (`test_causality_future_independence`).

## 5. Workload Generation

`workload/workload_generator.py` uses `random.Random(42)`. The traces are saved in `workload/traces/` and the audit confirmed they match the generator exactly.

| Workload | Construction | Locality character |
|---|---|---|
| high_locality | 50 pages; 80 % of references to 10 hot pages, 20 % to 40 cold pages | Stable skewed hot set (larger than every frame count tested) |
| sequential | Cyclic scan over 50 pages; each reference has a 2 % chance of jumping to a random page | Scan; reuse distance ≈ 50 |
| random | Uniform over 50 pages | Weak locality |
| looping | 0,1,2,3,4,5 repeated (loop size 6) | Fixed working set of 6 |

## 6. Experimental Setup and Textbook Validation

**Host** (as recorded in `report/experimental_setup.txt`): Intel Core Ultra 7 155H (16 cores / 22 threads), 15.46 GiB RAM, Windows 11 Home Single Language 64-bit (build 10.0.26200 when the matrix was run), CPython 3.13.4, matplotlib 3.11.2 and numpy 2.5.3 (used only for plots). The simulators use only the Python standard library.

**Matrix:** 4 workloads × 3 N × 3 frame counts × 7 policies = **252 configurations**, each repeated **5 times**, giving **1,260 runs**, all with seed 42. Fault counts are deterministic and were identical in all 5 repetitions. The repetitions give timing statistics (mean, sample std, min, max). The audit confirmed that faults + hits = N and hit_ratio = hits/N in every row, that there are no missing or duplicate configurations, and that every summary timing statistic matches the raw data exactly. Re-simulating all 252 configurations with the current code reproduced every fault count in the CSV.

**Textbook validation:** reference string 7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1 with 3 frames (`report/validation_table.csv`).

| Policy | Faults | Hits | Hit ratio | Expected | Status |
|---|---|---|---|---|---|
| FIFO | 15 | 5 | 25 % | 15 (textbook) | PASS |
| LRU | 12 | 8 | 40 % | 12 (textbook) | PASS |
| Optimal | 9 | 11 | 55 % | 9 (textbook) | PASS |
| Clock | 14 | 6 | 30 % | 14 (hand trace, our documented semantics) | PASS |
| LFU | 13 | 7 | 35 % | 13 (hand trace, FIFO tie-break) | PASS |

Textbooks give no single Clock or LFU answer because results depend on hand and tie-break conventions. We traced both by hand under our documented rules.

**Belady's anomaly (FIFO, `results/belady_anomaly.csv`):** the string 1,2,3,4,1,2,5,1,2,3,4,5 gives **9 faults with 3 frames and 10 faults with 4 frames**, which reproduces the anomaly. On the four N=1000 synthetic traces with 3 to 8 frames, FIFO faults never increased when frames were added.

## 7. Results

**Table 1 – Mean hit ratio (%) over the 9 (N, frames) settings of each workload**

| Workload | FIFO | LRU | Clock | LFU | Adaptive W50 | Adaptive W100 | Optimal |
|---|---|---|---|---|---|---|---|
| high_locality | 31.54 | 32.81 | 32.12 | **40.80** | 32.82 | 32.81 | 55.92 |
| sequential | 0.98 | 0.98 | 0.98 | **7.25** | 0.99 | 0.98 | 12.23 |
| random | 10.62 | **10.77** | 10.68 | 10.19 | **10.77** | **10.77** | 32.03 |
| looping | 33.25 | 33.25 | 33.25 | 33.25 | 33.25 | 33.25 | 73.17 |
| **All 36** | 19.10 | 19.45 | 19.26 | **22.87** | 19.46 | 19.45 | 43.34 |

**Table 2 – Hit ratio (%) at N = 5000, frames = 5 (data behind Fig. 1)**

| Workload | FIFO | LRU | Clock | LFU | Adaptive W50 | Adaptive W100 | Optimal |
|---|---|---|---|---|---|---|---|
| high_locality | 30.10 | 30.84 | 30.12 | **38.34** | 30.84 | 30.84 | 56.66 |
| sequential | 0.72 | 0.76 | 0.72 | **7.00** | 0.76 | 0.76 | 11.38 |
| random | 9.90 | **9.96** | 9.90 | 9.62 | **9.96** | **9.96** | 31.82 |
| looping | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 79.92 |

![Fig. 1 – Adaptive (W=50) vs fixed policies, N=5000, 5 frames](../plots/adaptive_vs_fixed_policies.png)

**7.1 Per-workload observations**
- **High locality:** LFU had the most hits of any online policy in all 9 settings. At N=5000 its hit ratio rose from 22.78 % to 38.34 % to 60.82 % as frames went from 3 to 5 to 8, compared with 18.60 / 30.84 / 48.68 % for LRU and 39.68 / 56.66 / 72.52 % for Optimal (Fig. 2).
- **Sequential:** FIFO, LRU, Clock and both Adaptive variants stay at or below 2.60 % in every setting. LFU reaches 13.74 % at N=5000 with 8 frames.
- **Random:** all online policies are within about 1 percentage point of each other (for example 9.62–9.96 % at N=5000, 5 frames). Optimal reaches roughly three times that.
- **Looping:** with 3 or 5 frames, which is fewer than the 6 pages in the loop, every online policy scores **0 % hits** (thrashing). Optimal still scores 39.96 % (3 frames) and 79.92 % (5 frames) at N=5000. With 8 frames every policy has only the 6 compulsory faults (≥ 99.40 % hits).
- **Workload size:** hit ratios barely change with N. For example, LRU on high_locality with 5 frames gives 31.30 / 30.84 / 30.94 % for N = 1000 / 5000 / 20000. Fault counts grow roughly linearly with N.
- **Best online policy per configuration:** LFU alone had the fewest faults in 20 of 36 configurations (all 9 high-locality, 8 of 9 sequential and 3 of 9 random). In the other 10 configurations it tied (9 looping configurations plus sequential N=1000, 3 frames, where all online policies tie). Apart from these all-way ties, LRU, FIFO and Clock had the fewest faults only in random configurations.

![Fig. 2 – Effect of frame capacity (high locality, N=5000)](../plots/frame_capacity_effect.png)

**7.2 Adaptive behaviour**

**Table 3 – Policy switches per run (identical for 3, 5 and 8 frames)**

| Window | high_locality | sequential | random | looping |
|---|---|---|---|---|
| W=50 (N = 1k / 5k / 20k) | 0 / 0 / 2 | 12 / 75 / 312 | 0 / 0 / 0 | 0 / 0 / 0 |
| W=100 (all N) | 0 | 0 | 0 | 0 |

- **Adaptive_W50 vs LRU:** the same fault count in 30 of 36 configurations and fewer faults in 6 (high_locality and sequential at N=20000; reductions of 1–6 faults, at most 0.03 % of references). It never had more faults than LRU.
- **Adaptive_W100 vs LRU:** the same fault count in **all 36** configurations, because it never switched.
- Switch counts do not depend on the number of frames. This is expected, because the decision uses only the reference history and not the memory state.

**Table 4 – Locality metrics seen at the decision points (N=5000; min / mean / max)**

| Workload | W | U | CV | Rule outcomes |
|---|---|---|---|---|
| high_locality | 50 | 0.26 / 0.37 / 0.50 | 0.49 / 0.73 / 0.97 | LRU (all 198) |
| high_locality | 100 | 0.18 / 0.26 / 0.31 | 0.79 / 0.94 / 1.10 | LRU (U<0.35, all 98) |
| sequential | 50 | 0.50 / 0.88 / 1.00 | 0.00 / 0.19 / 0.45 | Clock 123, LRU 75 |
| sequential | 100 | 0.37 / 0.50 / 0.50 | 0.00 / 0.29 / 0.59 | LRU (all 98) |
| random | 50 / 100 | 0.50–0.72 / 0.39–0.47 | 0.35–0.68 / 0.39–0.67 | LRU (default) |
| looping | 50 / 100 | 0.12 / 0.06 | 0.06 / 0.03 | LRU (U<0.35) |

At N=20000 with W=50, high_locality crossed the LFU rule once (CV reached 1.06). That one episode accounts for its 2 switches (LRU→LFU→LRU).

![Fig. 3 – Adaptive switches and hit ratio by workload (W=50, N=5000, 5 frames)](../plots/adaptive_behavior_by_workload.png)

**7.3 Execution time** (mean over the 5 repetitions, then averaged across configurations; pure-Python simulation time)

| N | FIFO | LRU | Optimal | Clock | LFU | Adaptive W50 | Adaptive W100 |
|---|---|---|---|---|---|---|---|
| 1,000 | 0.27 ms | 0.48 ms | 1.00 ms | 1.12 ms | 1.99 ms | 2.29 ms | 1.79 ms |
| 5,000 | 1.30 ms | 2.02 ms | 4.60 ms | 5.30 ms | 8.87 ms | 10.81 ms | 9.03 ms |
| 20,000 | 5.61 ms | 8.02 ms | 18.65 ms | 21.23 ms | 36.58 ms | 43.82 ms | 37.55 ms |

On average over all 36 configurations, Adaptive_W50 took **5.4×** and Adaptive_W100 **4.6×** the time of LRU. Repetition noise was small. For high_locality at N=20000 with 8 frames (Fig. 4), Adaptive_W50 took 30.01 ± 1.20 ms and LRU 4.35 ± 0.69 ms.

![Fig. 4 – Execution time, high locality, N=20000, 8 frames (mean ± std, 5 repetitions)](../plots/execution_time_vs_algorithm.png)

## 8. Discussion

**The adaptive policy is causal and stable, but in these experiments it mostly behaved like LRU.** Its switching rules were tuned for LRU as the default. On our workloads the observed (U, CV) values almost never reached the LFU region (Table 4). For high_locality at N=5000, CV never reached 1.0 with W=50 (maximum 0.97), and with W=100 U stayed below 0.35, so the LRU rule fired first. So the controller stayed on LRU even though LFU was the best online policy for this workload by about 8 percentage points (Table 1). The measurements answer the research question only partly. The mechanism does detect locality changes correctly, because it picks Clock during scan windows (U ≥ 0.85) and LRU for tight loops. But the strategy it selects is not always the best one available.

**Switching to Clock on scans did not help much.** On a scan whose reuse distance (≈ 50) is longer than the number of frames, LRU, FIFO and Clock all evict a page before it comes back, so they behave almost identically (0.72–0.76 % hits at N=5000, 5 frames). The 75–312 switches therefore gained at most 6 faults. LFU does better on this workload because pages that collect a count above 1 (after the random jumps) stay resident and get hit again on each scan cycle. This scan resistance comes from frequency, not recency.

**Effect of window size.** A larger window gives smoother metrics and fewer evaluations, but also less sensitivity. With only 50 distinct pages, a 100-reference window can never show U above 0.50, so W=100 could never detect a scan and never switched. W=50 reacted to scans but switched often (312 switches at N=20000). Neither window size changed the hit ratio meaningfully compared with LRU.

**Trade-offs.** The handover design worked as intended. Switching never flushed frames, and Adaptive_W50 never had more faults than LRU. The cost was runtime: computing window statistics, rebuilding metadata, and the linear reference-bit update in the Clock emulation made the adaptive policy the slowest online policy in our Python implementation (4.6–5.4× LRU). In a real kernel, LRU itself is approximated with reference bits, so these Python timings show relative bookkeeping cost and not kernel overhead.

**Other observations.** Looping with fewer frames than the loop size makes every recency- or frequency-based online policy thrash completely, while Optimal does not. This matches the working-set view: memory below the working set gives catastrophic fault rates. Belady's anomaly appeared only on the constructed classic string, not on our synthetic traces, which is consistent with it being possible but uncommon.

## 9. Limitations

- **Synthetic workloads:** these are small, stationary traces over 50 pages (6 for looping) with no phase changes inside a trace. A workload that alternates between locality and scan phases, where switching should pay off most, was not included.
- **Hand-set thresholds:** 0.35, 0.85, 1.0 and 0.70 were not tuned or learned. Table 4 suggests that with W=50 a lower CV threshold for LFU would have selected it on high_locality, but we did not test this, so we make no claim about it.
- **FIFO never chosen:** FIFO is never a target of the rules, and the candidate set does not include scan-resistant policies such as ARC or MRU.
- **Timing scope:** times are single-process Python timings on one laptop, measured with `perf_counter` and 5 repetitions. They include interpreter overhead, and the absolute numbers are not representative of kernel costs.
- **Simplified handover:** LFU counts and LRU order are rebuilt only from the window, so information older than W is lost at each switch.
- **Simulation scope:** page-level only, with no modelling of TLBs, dirty-page write-back or I/O latency.

## 10. Individual Contributions

| Student | Contributions |
|---|---|
| **24BCE0702 – Yash Pradhan** | FIFO, LRU and Optimal implementations; the reproducible workload generator (four patterns, seed 42); unit tests for FIFO, LRU and Optimal; checking Optimal as the lower bound |
| **24BCE0714 – Anjini Pandey** | Clock and LFU implementations; adaptive engine design (U and CV metrics, switching rules, state handover) and its unit tests; experiment runner, Belady experiment, analysis and plotting pipeline; report outline and result summary |

Details are in `CONTRIBUTIONS.md`.

## 11. Conclusion

We implemented and validated five classic replacement policies (FIFO 15, LRU 12 and Optimal 9 faults on the textbook string) and a strictly causal adaptive policy that switches among LRU, LFU and Clock using a rolling-window unique-page ratio and a frequency coefficient of variation. The policy keeps the resident frames when it switches. Across 252 configurations (1,260 runs) the adaptive policy was never worse than LRU in faults. It recognised scan phases with W=50, but it improved on LRU by at most 6 faults, and with W=100 it was identical to LRU. LFU was the strongest online policy on both skewed and scan workloads, and Optimal showed a large remaining gap (43.34 % vs 22.87 % mean hit ratio). The adaptive policy also cost 4.6–5.4× LRU's simulation time. **Adaptivity alone is not enough. The decision thresholds have to match the locality metrics the workloads actually produce, and switching is only worth it when the candidate policies behave differently on the detected pattern.** Next steps are threshold calibration, phase-changing workloads and adding scan-resistant candidates.

## 12. References

1. A. Silberschatz, P. B. Galvin, G. Gagne, *Operating System Concepts*, 10th ed., Wiley, 2018 (Ch. 10, Virtual Memory).
2. L. A. Belady, "A study of replacement algorithms for a virtual-storage computer," *IBM Systems Journal*, 5(2), 78–101, 1966.
3. L. A. Belady, R. A. Nelson, G. S. Shedler, "An anomaly in space-time characteristics of certain programs running in a paging machine," *Communications of the ACM*, 12(6), 349–353, 1969.
4. P. J. Denning, "The working set model for program behavior," *Communications of the ACM*, 11(5), 323–333, 1968.
5. F. J. Corbató, "A paging experiment with the Multics system," MIT Project MAC Report MAC-M-384, 1968.
6. N. Megiddo, D. S. Modha, "ARC: A self-tuning, low overhead replacement cache," *Proc. USENIX FAST*, 2003.
7. A. S. Tanenbaum, H. Bos, *Modern Operating Systems*, 4th ed., Pearson, 2015.
8. R. H. Arpaci-Dusseau, A. C. Arpaci-Dusseau, *Operating Systems: Three Easy Pieces*, Arpaci-Dusseau Books, 2018.
