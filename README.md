# CS3 – Adaptive Page Replacement Policy Simulation
## Course: BCSE303L – Operating Systems (Fall Semester 2026-27)

### Academic Batch:
1. **24BCE0702 – Yash Pradhan**
2. **24BCE0714 – Anjini Pandey**

---

## 1. Project Overview & Research Question

**Research Question:**  
> *"Can an adaptive page-replacement policy select an appropriate strategy according to observed memory-reference locality?"*

Modern operating system workloads alternate between localized iterative computations, large-scale streaming memory scans, and random accesses. Conventional fixed page-replacement policies (such as FIFO, LRU, Clock, or LFU) excel under specific access distributions but exhibit systemic performance degradations when access patterns shift. 

This project implements an **online, strictly causal Adaptive Page Replacement algorithm** that dynamically detects memory-reference locality within a sliding observation window ($W$) and switches between specialized replacement heuristics without future lookahead. The policy is evaluated against five classic baselines across synthetic workloads and varying physical memory frame capacities.

---

## 2. Implemented Algorithms

| Algorithm | Implementation File | Key Operational Mechanics |
| :--- | :--- | :--- |
| **FIFO** | [`src/fifo.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/fifo.py) | Strict queue-based eviction order; evicts the oldest resident page. |
| **LRU** | [`src/lru.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/lru.py) | Uses an `OrderedDict` for $O(1)$ recency promotion and least-recent eviction. |
| **Optimal (MIN)** | [`src/optimal.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/optimal.py) | Belady's theoretical offline lookahead (evicts page whose next access is farthest). Serves as an unachievable benchmark lower bound. |
| **Clock (Second-Chance)** | [`src/clock.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/clock.py) | Circular frame buffer with reference bits. Clears bits on sweep and evicts the first page with bit 0. |
| **LFU** | [`src/lfu.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/lfu.py) | Tracks reference counts of resident pages; deterministic FIFO arrival-order tie-breaker. |
| **Adaptive** | [`src/adaptive.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/adaptive.py) | Causal sliding-window locality classifier ($U, CV_f$); non-destructive state handover. |

---

## 3. Adaptive Architecture & State Handover

### Causal Locality Metrics
The Adaptive engine inspects the preceding $W$ references ($W=50$ or $100$):
1. **Unique-Page Ratio ($U$)**:
   $$U = \frac{\text{len(unique pages in } W)}{W}$$
2. **Frequency Skew ($CV_f$)**:
   $$CV_f = \frac{\sigma_f}{\mu_f}$$
   where $\mu_f$ and $\sigma_f$ are the mean and standard deviation of page frequencies within $W$.

### Switching Rules
- **$U < 0.35$ (High Locality)**: Strong temporal reuse $\to$ selects **LRU**.
- **$U \ge 0.85$ (Streaming / High Diversity)**: Linear scan $\to$ selects **Clock** to prevent cache pollution.
- **$CV_f \ge 1.0$ and $U < 0.70$ (Frequency Skew)**: Skewed access with moderate diversity $\to$ selects **LFU**.
- **Default**: Balances toward **LRU**.

### Non-Destructive State Handover
When switching policies (e.g., LRU $\to$ LFU or Clock $\to$ LRU), physical frames are **never** cold-restarted:
- The resident page set is preserved intact.
- If transitioning to **LRU**, recency order is reconstructed based on the last observed occurrences in the window.
- If transitioning to **LFU**, frequencies are initialized from observed window frequencies.
- If transitioning to **Clock**, reference bits are set to 1 and the hand pointer is preserved.

---

## 4. Directory Structure

```text
CS3-Adaptive-Page-Replacement/
├── config/
│   └── config.json                  # Experiment parameters, thresholds, and seeds
├── src/
│   ├── common.py                    # Common data structures and PageReplacementResult
│   ├── fifo.py                      # First-In, First-Out implementation
│   ├── lru.py                       # Least Recently Used implementation
│   ├── optimal.py                   # Belady's Optimal implementation
│   ├── clock.py                     # Clock / Second-Chance implementation
│   ├── lfu.py                       # Least Frequently Used implementation
│   └── adaptive.py                  # Online causal Adaptive engine
├── workload/
│   ├── workload_generator.py        # Workload synthesizer (Seed=42)
│   └── traces/                      # Exported reproducible JSON traces
├── experiments/
│   ├── run_validation.py            # Textbook baseline validation runner
│   ├── run_experiments.py           # Full matrix benchmark runner (1,260 runs)
│   └── analyze_results.py           # Statistical analysis and plot generator
├── tests/
│   ├── test_fifo.py                 # FIFO unit tests
│   ├── test_lru.py                  # LRU unit tests
│   ├── test_optimal.py              # Optimal unit tests
│   ├── test_clock.py                # Clock unit tests
│   ├── test_lfu.py                  # LFU unit tests
│   └── test_adaptive.py             # Adaptive unit tests & invariant checks
├── results/
│   ├── validation_results.csv       # Textbook validation outputs
│   ├── raw_results.csv              # 1,260 individual experimental runs
│   ├── summary_results.csv          # 252 aggregated condition summaries
│   └── belady_anomaly.csv           # Belady's Anomaly empirical test results
├── plots/                           # Report-ready publication figures (PNG)
│   ├── faults_vs_algorithm.png
│   ├── hit_ratio_vs_algorithm.png
│   ├── execution_time_vs_algorithm.png
│   ├── faults_vs_workload_size.png
│   ├── hit_ratio_vs_workload_size.png
│   ├── adaptive_vs_fixed_policies.png
│   ├── adaptive_behavior_by_workload.png
│   ├── frame_capacity_effect.png
│   └── adaptive_window_effect.png
├── report/
│   ├── validation_table.csv         # Formatted validation table
│   ├── experimental_setup.txt       # Host hardware & environment telemetry
│   ├── result_summary.txt           # Statistical summary and findings
│   └── report_outline.md            # Complete 8-page academic report outline
├── CONTRIBUTIONS.md                 # Individual student responsibilities
├── README.md                        # Project documentation and guide
└── requirements.txt                 # Dependencies (matplotlib, numpy)
```

---

## 5. Installation & Requirements

Python 3.10+ is recommended. Install required visualization libraries:

```bash
pip install -r requirements.txt
```

---

## 6. How to Reproduce All Experiments

All steps are automated and fully reproducible from the project root (`CS3-Adaptive-Page-Replacement/`):

### Step 1: Run Unit Tests
Verifies all 28 test cases across edge cases, invariants, and causal bounds:
```bash
python -m unittest discover -s tests -v
```

### Step 2: Run Textbook Baseline Validation
Executes the textbook string `[7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]` with capacity 3:
```bash
python experiments/run_validation.py
```
*Expected Ground Truth:* FIFO = 15 faults, LRU = 12 faults, Optimal = 9 faults.

### Step 3: Generate Workload Traces
Generates 12 deterministic workload traces (Seed = 42):
```bash
python workload/workload_generator.py
```

### Step 4: Execute Full Benchmark Matrix
Runs 1,260 runs (4 workloads $\times$ 3 sizes $\times$ 3 capacities $\times$ 7 algorithms $\times$ 5 timing repetitions) and logs host specs:
```bash
python experiments/run_experiments.py
```

### Step 5: Generate Statistical Analysis & Plots
Parses the raw CSVs, calculates summary statistics, and generates 9 publication plots:
```bash
python experiments/analyze_results.py
```

---

## 7. Textbook Validation Summary

| Algorithm | Faults | Hits | Hit Ratio | Expected Baseline | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **FIFO** | 15 | 5 | 25.00% | 15 | **PASS** |
| **LRU** | 12 | 8 | 40.00% | 12 | **PASS** |
| **Optimal** | 9 | 11 | 55.00% | 9 | **PASS** |
| **Clock** | 14 | 6 | 30.00% | *Documented* | **PASS** |
| **LFU** | 13 | 7 | 35.00% | *Documented* | **PASS** |

---

## 8. Summary of Experimental Findings

1. **Locality Responsiveness**: In High-Locality workloads, Adaptive autonomously classified $U < 0.35$ and converged to LRU, matching LRU's hit ratio (~30.8% at $N=5,000, C=5$) without prior knowledge.
2. **Thrashing Diagnostics**: In looping workloads with working set size $L=6$, physical frame capacities $C \le 5$ suffered complete thrashing (0.0% hit ratio). When capacity expanded to $C \ge 6$, hit ratio jumped to 99.4%, confirming working set model predictions.
3. **Belady's Anomaly**: Verified on the classic 12-reference string (9 faults on 3 frames vs 10 faults on 4 frames in FIFO).
4. **Computational Feasibility**: Adaptive introduces a modest statistical calculation overhead (~20 ms for 20,000 accesses), running within real-time limits without oracle lookahead.
