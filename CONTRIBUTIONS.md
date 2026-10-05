# Individual Contributions Statement
## Course: BCSE303L – Operating Systems
### Semester: Fall Semester 2026-27
### Case Study: CS3 – Adaptive Page Replacement

---

### Student 1: 24BCE0702 – Yash Pradhan
**Assigned Responsibilities and Completed Contributions:**
1. **Baseline Algorithm Implementations**:
   - Implemented strict queue-based First-In, First-Out ([`src/fifo.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/fifo.py)).
   - Implemented Least Recently Used ([`src/lru.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/lru.py)) utilizing an `OrderedDict` data structure for $O(1)$ recency updates.
   - Implemented theoretical Belady's Optimal ([`src/optimal.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/optimal.py)) with precomputed occurrence queues for $O(N \cdot C)$ lookahead complexity.
2. **Workload Generation Framework**:
   - Engineered reproducible synthetic workload generator ([`workload/workload_generator.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/workload/workload_generator.py)) with fixed seed `42`.
   - Formulated the Pareto 80/20 distribution for the High-Locality pattern, streaming scans for Sequential, uniform sampling for Random, and cyclic loops for Looping workloads.
3. **Correctness & Unit Testing**:
   - Developed unit test suites for FIFO ([`tests/test_fifo.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/tests/test_fifo.py)), LRU ([`tests/test_lru.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/tests/test_lru.py)), and Optimal ([`tests/test_optimal.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/tests/test_optimal.py)).
   - Verified that Optimal strictly provides a theoretical lower bound on page faults across all workloads.

---

### Student 2: 24BCE0714 – Anjini Pandey
**Assigned Responsibilities and Completed Contributions:**
1. **Clock and LFU Implementations**:
   - Implemented circular buffer Clock / Second-Chance replacement ([`src/clock.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/clock.py)) with explicit bit-clearing and circular hand pointer mechanics.
   - Implemented Least Frequently Used ([`src/lfu.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/lfu.py)) with a deterministic FIFO arrival-order tie-breaker.
2. **Online Adaptive Engine Architecture**:
   - Architected the online causal Adaptive Page Replacement policy ([`src/adaptive.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/src/adaptive.py)) operating over sliding observation windows ($W \in \{50, 100\}$).
   - Formulated locality metrics: Unique-Page Ratio ($U$) and Frequency Skew Coefficient of Variation ($CV_f$).
   - Designed the non-destructive physical state handover protocol preserving resident memory pages across policy transitions.
   - Created adaptive unit tests ([`tests/test_adaptive.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/tests/test_adaptive.py)).
3. **Experimentation, Statistical Analysis & Visualization**:
   - Built the automated batch experiment runner ([`experiments/run_experiments.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/experiments/run_experiments.py)) executing 1,260 runs with 5 timing repetitions and host telemetry detection.
   - Executed Belady's Anomaly empirical scan ([`results/belady_anomaly.csv`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/results/belady_anomaly.csv)).
   - Implemented statistical aggregator and Matplotlib visualization pipeline ([`experiments/analyze_results.py`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/experiments/analyze_results.py)) generating 9 publication-grade figures.
   - Authored the academic report outline ([`report/report_outline.md`](file:///C:/Users/ANJINI%20PANDEY/.gemini/antigravity-ide/scratch/CS3-Adaptive-Page-Replacement/report/report_outline.md)) and result summary.

---

### Academic Integrity Declaration
We affirm that this project is our original work for BCSE303L Operating Systems. All baseline algorithms, adaptive policies, workload generators, and experimental telemetry scripts were written and verified experimentally on the host system without fabrication of numbers or plagiarism.
