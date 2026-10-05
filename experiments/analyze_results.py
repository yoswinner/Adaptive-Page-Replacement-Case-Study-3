"""
Results Analysis and Automated Plot Generator.
Course: BCSE303L - Operating Systems
Students:
  1. 24BCE0702 - Yash Pradhan
  2. 24BCE0714 - Anjini Pandey

Reads results/raw_results.csv and results/summary_results.csv to:
1. Perform statistical analysis (mean, std dev, comparisons)
2. Generate all 9 required report-ready plots in plots/
3. Export report/result_summary.txt
"""

import os
import sys
import csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Set aesthetic styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "figure.autolayout": True
})

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
REPORT_DIR = os.path.join(BASE_DIR, "report")

os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

def load_summary_results():
    summary_path = os.path.join(RESULTS_DIR, "summary_results.csv")
    rows = []
    with open(summary_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "workload_type": r["workload_type"],
                "N": int(r["N"]),
                "frame_capacity": int(r["frame_capacity"]),
                "algorithm": r["algorithm"],
                "page_faults": int(r["page_faults"]),
                "page_hits": int(r["page_hits"]),
                "hit_ratio": float(r["hit_ratio"]),
                "mean_time_sec": float(r["mean_execution_time_sec"]),
                "std_time_sec": float(r["std_execution_time_sec"]),
                "min_time_sec": float(r["min_execution_time_sec"]),
                "max_time_sec": float(r["max_execution_time_sec"]),
                "switches_count": int(r["switches_count"]),
                "final_strategy": r["final_strategy"]
            })
    return rows

def generate_plots(rows):
    algorithms = ["Optimal", "LRU", "Adaptive_W50", "Adaptive_W100", "Clock", "LFU", "FIFO"]
    palette = {
        "Optimal": "#2ca02c",
        "LRU": "#1f77b4",
        "Adaptive_W50": "#ff7f0e",
        "Adaptive_W100": "#d62728",
        "Clock": "#9467bd",
        "LFU": "#8c564b",
        "FIFO": "#7f7f7f"
    }

    # -------------------------------------------------------------
    # 1. faults_vs_algorithm.png
    # Average page faults across algorithms for High Locality (N=5000, Capacity=5)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    subset = [r for r in rows if r["workload_type"] == "high_locality" and r["N"] == 5000 and r["frame_capacity"] == 5]
    subset_sorted = sorted(subset, key=lambda x: algorithms.index(x["algorithm"]) if x["algorithm"] in algorithms else 99)
    algos = [r["algorithm"] for r in subset_sorted]
    faults = [r["page_faults"] for r in subset_sorted]
    bars = ax.bar(algos, faults, color=[palette.get(a, "#333333") for a in algos], width=0.55, edgecolor="black", linewidth=0.8)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 30, f"{int(yval)}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylabel("Page Faults")
    ax.set_title("Page Faults vs Algorithm (High Locality, N=5,000, Frames=5)")
    ax.set_ylim(0, max(faults) * 1.15)
    plt.xticks(rotation=20)
    plt.tight_layout()
    p1 = os.path.join(PLOTS_DIR, "faults_vs_algorithm.png")
    plt.savefig(p1, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 2. hit_ratio_vs_algorithm.png
    # Hit Ratio across algorithms for High Locality (N=5000, Capacity=5)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    hit_ratios = [r["hit_ratio"] * 100 for r in subset_sorted]
    bars = ax.bar(algos, hit_ratios, color=[palette.get(a, "#333333") for a in algos], width=0.55, edgecolor="black", linewidth=0.8)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.8, f"{yval:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylabel("Hit Ratio (%)")
    ax.set_title("Hit Ratio vs Algorithm (High Locality, N=5,000, Frames=5)")
    ax.set_ylim(0, max(hit_ratios) * 1.2)
    plt.xticks(rotation=20)
    plt.tight_layout()
    p2 = os.path.join(PLOTS_DIR, "hit_ratio_vs_algorithm.png")
    plt.savefig(p2, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 3. execution_time_vs_algorithm.png
    # Mean execution time with error bars (std dev) for N=20000, Frames=8
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    time_subset = [r for r in rows if r["workload_type"] == "high_locality" and r["N"] == 20000 and r["frame_capacity"] == 8]
    time_subset_sorted = sorted(time_subset, key=lambda x: algorithms.index(x["algorithm"]) if x["algorithm"] in algorithms else 99)
    t_algos = [r["algorithm"] for r in time_subset_sorted]
    t_means = [r["mean_time_sec"] * 1000 for r in time_subset_sorted]  # ms
    t_stds = [r["std_time_sec"] * 1000 for r in time_subset_sorted]
    bars = ax.bar(t_algos, t_means, yerr=t_stds, capsize=5, color=[palette.get(a, "#333333") for a in t_algos], width=0.55, edgecolor="black", linewidth=0.8)
    for bar, sd in zip(bars, t_stds):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + sd + 0.5, f"{yval:.2f}ms", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Execution Time (milliseconds)")
    ax.set_title("Execution Time vs Algorithm (High Locality, N=20,000, Frames=8, mean ± std of 5 reps)")
    ax.set_ylim(0, max(t_means) * 1.25)
    plt.xticks(rotation=20)
    plt.tight_layout()
    p3 = os.path.join(PLOTS_DIR, "execution_time_vs_algorithm.png")
    plt.savefig(p3, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 4. faults_vs_workload_size.png
    # Faults vs Workload Size (N=1000, 5000, 20000) for Capacity=5, High Locality
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sizes = [1000, 5000, 20000]
    for algo in ["Optimal", "LRU", "Adaptive_W50", "Clock", "FIFO"]:
        y_vals = []
        for n in sizes:
            match = next(r for r in rows if r["algorithm"] == algo and r["workload_type"] == "high_locality" and r["N"] == n and r["frame_capacity"] == 5)
            y_vals.append(match["page_faults"])
        ax.plot(sizes, y_vals, marker="o", linewidth=2.2, label=algo, color=palette[algo])
    ax.set_xlabel("Workload Size N (References)")
    ax.set_ylabel("Page Faults")
    ax.set_title("Page Fault Scalability vs Workload Size (High Locality, Frames=5)")
    ax.legend(frameon=True)
    plt.tight_layout()
    p4 = os.path.join(PLOTS_DIR, "faults_vs_workload_size.png")
    plt.savefig(p4, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 5. hit_ratio_vs_workload_size.png
    # Hit Ratio vs Workload Size (N=1000, 5000, 20000) for Capacity=5, High Locality
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for algo in ["Optimal", "LRU", "Adaptive_W50", "Clock", "FIFO"]:
        y_vals = []
        for n in sizes:
            match = next(r for r in rows if r["algorithm"] == algo and r["workload_type"] == "high_locality" and r["N"] == n and r["frame_capacity"] == 5)
            y_vals.append(match["hit_ratio"] * 100)
        ax.plot(sizes, y_vals, marker="s", linewidth=2.2, label=algo, color=palette[algo])
    ax.set_xlabel("Workload Size N (References)")
    ax.set_ylabel("Hit Ratio (%)")
    ax.set_title("Hit Ratio Stability vs Workload Size (High Locality, Frames=5)")
    ax.legend(frameon=True)
    plt.tight_layout()
    p5 = os.path.join(PLOTS_DIR, "hit_ratio_vs_workload_size.png")
    plt.savefig(p5, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 6. adaptive_vs_fixed_policies.png
    # Grouped bar chart comparing Adaptive_W50 vs LRU, Clock, LFU, FIFO across all 4 workloads (N=5000, Frames=5)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 5.5))
    w_types = ["high_locality", "sequential", "random", "looping"]
    w_labels = ["High Locality", "Sequential", "Uniform Random", "Looping"]
    compare_algos = ["LRU", "Clock", "LFU", "Adaptive_W50", "Optimal"]
    x = np.arange(len(w_types))
    width = 0.15

    for i, algo in enumerate(compare_algos):
        vals = []
        for wt in w_types:
            match = next(r for r in rows if r["algorithm"] == algo and r["workload_type"] == wt and r["N"] == 5000 and r["frame_capacity"] == 5)
            vals.append(match["hit_ratio"] * 100)
        ax.bar(x + (i - 2) * width, vals, width, label=algo, color=palette[algo], edgecolor="black", linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(w_labels)
    ax.set_ylabel("Hit Ratio (%)")
    ax.set_title("Adaptive Policy vs Fixed Policies Across Workload Classes (N=5,000, Frames=5)")
    ax.legend(frameon=True)
    plt.tight_layout()
    p6 = os.path.join(PLOTS_DIR, "adaptive_vs_fixed_policies.png")
    plt.savefig(p6, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 7. adaptive_behavior_by_workload.png
    # Policy switches and final strategy selected by Adaptive for N=5000, Frames=5
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    switches = []
    hit_rates = []
    strategies = []
    for wt in w_types:
        match = next(r for r in rows if r["algorithm"] == "Adaptive_W50" and r["workload_type"] == wt and r["N"] == 5000 and r["frame_capacity"] == 5)
        switches.append(match["switches_count"])
        hit_rates.append(match["hit_ratio"] * 100)
        strategies.append(match["final_strategy"])

    ax1.bar(w_labels, switches, color="#ff7f0e", width=0.5, edgecolor="black", linewidth=0.8)
    ax1.set_ylabel("Number of Policy Switches")
    ax1.set_title("Adaptive Strategy Switches (N=5,000, W=50)")
    for i, (cnt, strat) in enumerate(zip(switches, strategies)):
        ax1.text(i, cnt + 0.1, f"{cnt} switches\n(Active: {strat})", ha="center", va="bottom", fontsize=9)
    ax1.set_ylim(0, max(switches) * 1.35 if max(switches) > 0 else 5)

    ax2.bar(w_labels, hit_rates, color="#1f77b4", width=0.5, edgecolor="black", linewidth=0.8)
    ax2.set_ylabel("Hit Ratio (%)")
    ax2.set_title("Adaptive Hit Ratio by Workload (N=5,000, W=50)")
    for i, hr in enumerate(hit_rates):
        ax2.text(i, hr + 1.0, f"{hr:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax2.set_ylim(0, 115)

    plt.tight_layout()
    p7 = os.path.join(PLOTS_DIR, "adaptive_behavior_by_workload.png")
    plt.savefig(p7, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 8. frame_capacity_effect.png
    # Hit Ratio as Frame Capacity increases (3, 5, 8) for High Locality, N=5000
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    caps = [3, 5, 8]
    for algo in ["Optimal", "LRU", "Adaptive_W50", "Clock", "FIFO"]:
        y_vals = []
        for c in caps:
            match = next(r for r in rows if r["algorithm"] == algo and r["workload_type"] == "high_locality" and r["N"] == 5000 and r["frame_capacity"] == c)
            y_vals.append(match["hit_ratio"] * 100)
        ax.plot(caps, y_vals, marker="^", linewidth=2.2, label=algo, color=palette[algo])
    ax.set_xlabel("Physical Frame Capacity")
    ax.set_ylabel("Hit Ratio (%)")
    ax.set_title("Effect of Physical Frame Capacity on Hit Ratio (High Locality, N=5,000)")
    ax.set_xticks(caps)
    ax.legend(frameon=True)
    plt.tight_layout()
    p8 = os.path.join(PLOTS_DIR, "frame_capacity_effect.png")
    plt.savefig(p8, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 9. adaptive_window_effect.png
    # Comparing W=50 vs W=100 on Hit Ratio and Execution Time across workloads (N=5000, Frames=5)
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    w50_hits = []
    w100_hits = []
    w50_times = []
    w100_times = []

    for wt in w_types:
        m50 = next(r for r in rows if r["algorithm"] == "Adaptive_W50" and r["workload_type"] == wt and r["N"] == 5000 and r["frame_capacity"] == 5)
        m100 = next(r for r in rows if r["algorithm"] == "Adaptive_W100" and r["workload_type"] == wt and r["N"] == 5000 and r["frame_capacity"] == 5)
        w50_hits.append(m50["hit_ratio"] * 100)
        w100_hits.append(m100["hit_ratio"] * 100)
        w50_times.append(m50["mean_time_sec"] * 1000)
        w100_times.append(m100["mean_time_sec"] * 1000)

    x = np.arange(len(w_types))
    width = 0.35

    ax1.bar(x - width/2, w50_hits, width, label="Adaptive W=50", color="#ff7f0e", edgecolor="black")
    ax1.bar(x + width/2, w100_hits, width, label="Adaptive W=100", color="#d62728", edgecolor="black")
    ax1.set_xticks(x)
    ax1.set_xticklabels(w_labels, rotation=15)
    ax1.set_ylabel("Hit Ratio (%)")
    ax1.set_title("Hit Ratio Comparison (W=50 vs W=100)")
    ax1.legend()

    ax2.bar(x - width/2, w50_times, width, label="Adaptive W=50", color="#ff7f0e", edgecolor="black")
    ax2.bar(x + width/2, w100_times, width, label="Adaptive W=100", color="#d62728", edgecolor="black")
    ax2.set_xticks(x)
    ax2.set_xticklabels(w_labels, rotation=15)
    ax2.set_ylabel("Execution Time (ms)")
    ax2.set_title("Execution Time Overhead (W=50 vs W=100)")
    ax2.legend()

    plt.tight_layout()
    p9 = os.path.join(PLOTS_DIR, "adaptive_window_effect.png")
    plt.savefig(p9, dpi=300)
    plt.close()

    print("All 9 required plots successfully generated in plots/:")
    for p in [p1, p2, p3, p4, p5, p6, p7, p8, p9]:
        print(f" - {os.path.basename(p)}")

def generate_result_summary(rows):
    """
    Summarizes key statistical metrics and exports report/result_summary.txt
    """
    summary_txt_path = os.path.join(REPORT_DIR, "result_summary.txt")

    # Group by algorithm for aggregate stats
    algo_stats = defaultdict(lambda: {"hits": [], "faults": [], "times": [], "hit_ratios": []})
    for r in rows:
        algo_stats[r["algorithm"]]["hit_ratios"].append(r["hit_ratio"])
        algo_stats[r["algorithm"]]["times"].append(r["mean_time_sec"])

    lines = []
    lines.append("=" * 75)
    lines.append("OPERATING SYSTEMS (BCSE303L) EXPERIMENTAL RESULTS SUMMARY")
    lines.append("Case Study: CS3 - Adaptive Page Replacement")
    lines.append("Students: 24BCE0702 (Yash Pradhan) & 24BCE0714 (Anjini Pandey)")
    lines.append("=" * 75)
    lines.append("\n1. OVERALL ALGORITHM HIT RATIO & TIMING SUMMARY (Across 36 conditions):")
    lines.append(f"{'Algorithm':<15} | {'Mean Hit Ratio':<15} | {'Std Dev':<10} | {'Mean Time (ms)':<15} | {'Time Std (ms)':<15}")
    lines.append("-" * 75)

    for algo in ["Optimal", "LRU", "Adaptive_W50", "Adaptive_W100", "Clock", "LFU", "FIFO"]:
        hrs = algo_stats[algo]["hit_ratios"]
        times = [t * 1000 for t in algo_stats[algo]["times"]]
        mean_hr = np.mean(hrs) * 100
        std_hr = np.std(hrs) * 100
        mean_t = np.mean(times)
        std_t = np.std(times)
        lines.append(f"{algo:<15} | {mean_hr:>13.2f}% | {std_hr:>8.2f}% | {mean_t:>13.3f}ms | {std_t:>13.3f}ms")

    lines.append("\n2. WORKLOAD-SPECIFIC PERFORMANCE (N=5,000, Capacity=5 frames):")
    lines.append(f"{'Workload':<16} | {'LRU Hit%':<10} | {'Clock Hit%':<11} | {'LFU Hit%':<10} | {'Adaptive_W50 Hit%':<18} | {'Optimal Hit%':<12}")
    lines.append("-" * 85)
    for wt in ["high_locality", "sequential", "random", "looping"]:
        m_lru = next(r for r in rows if r["algorithm"] == "LRU" and r["workload_type"] == wt and r["N"] == 5000 and r["frame_capacity"] == 5)
        m_clk = next(r for r in rows if r["algorithm"] == "Clock" and r["workload_type"] == wt and r["N"] == 5000 and r["frame_capacity"] == 5)
        m_lfu = next(r for r in rows if r["algorithm"] == "LFU" and r["workload_type"] == wt and r["N"] == 5000 and r["frame_capacity"] == 5)
        m_adp = next(r for r in rows if r["algorithm"] == "Adaptive_W50" and r["workload_type"] == wt and r["N"] == 5000 and r["frame_capacity"] == 5)
        m_opt = next(r for r in rows if r["algorithm"] == "Optimal" and r["workload_type"] == wt and r["N"] == 5000 and r["frame_capacity"] == 5)
        lines.append(f"{wt:<16} | {m_lru['hit_ratio']*100:>8.2f}% | {m_clk['hit_ratio']*100:>9.2f}% | {m_lfu['hit_ratio']*100:>8.2f}% | {m_adp['hit_ratio']*100:>16.2f}% | {m_opt['hit_ratio']*100:>10.2f}%")

    lines.append("\nNote: 'Std Dev' = population std of hit ratio across the 36 conditions; 'Time Std' = std of the")
    lines.append("per-condition mean times across the 36 conditions (repetition-level std is in summary_results.csv).")

    # ---- Data-derived findings (computed from the CSVs, never hard-coded) ----
    get = lambda a, w, n, c: next(r for r in rows if r["algorithm"] == a and r["workload_type"] == w and r["N"] == n and r["frame_capacity"] == c)
    online = ["FIFO", "LRU", "Clock", "LFU", "Adaptive_W50", "Adaptive_W100"]
    conds = sorted({(r["workload_type"], r["N"], r["frame_capacity"]) for r in rows})
    pct = lambda a, w, n=5000, c=5: get(a, w, n, c)["hit_ratio"] * 100

    lines.append("\n3. KEY FINDINGS (computed from results/summary_results.csv):")
    best_hl = max(online, key=lambda a: pct(a, "high_locality"))
    lines.append(f"- High Locality (N=5000, C=5): best online policy is {best_hl} ({pct(best_hl,'high_locality'):.2f}%); "
                 f"LRU {pct('LRU','high_locality'):.2f}%, Adaptive_W50 {pct('Adaptive_W50','high_locality'):.2f}%, "
                 f"Clock {pct('Clock','high_locality'):.2f}%, FIFO {pct('FIFO','high_locality'):.2f}%, Optimal {pct('Optimal','high_locality'):.2f}%.")
    seq = [pct(a, "sequential") for a in online if a != "LFU"]
    lines.append(f"- Sequential (N=5000, C=5): FIFO/LRU/Clock/Adaptive reach only {min(seq):.2f}%-{max(seq):.2f}%; "
                 f"LFU {pct('LFU','sequential'):.2f}%; Optimal {pct('Optimal','sequential'):.2f}%.")
    rnd = [pct(a, "random") for a in online]
    lines.append(f"- Uniform Random (N=5000, C=5): online policies {min(rnd):.2f}%-{max(rnd):.2f}%; Optimal {pct('Optimal','random'):.2f}%.")
    loop_small = max(get(a, "looping", n, c)["hit_ratio"] for a in online for n in (1000, 5000, 20000) for c in (3, 5)) * 100
    loop_big = min(get(a, "looping", n, 8)["hit_ratio"] for a in online for n in (1000, 5000, 20000)) * 100
    lines.append(f"- Looping (loop size 6): with C=3 and C=5 every online policy scores {loop_small:.2f}% (thrashing); "
                 f"Optimal scores {pct('Optimal','looping',5000,3):.2f}% (C=3) and {pct('Optimal','looping',5000,5):.2f}% (C=5) at N=5000. "
                 f"With C=8 every policy reaches >= {loop_big:.2f}% (only 6 compulsory faults).")
    for a in ("Adaptive_W50", "Adaptive_W100"):
        d = [get("LRU", *k)["page_faults"] - get(a, *k)["page_faults"] for k in conds]
        sw = [get(a, *k)["switches_count"] for k in conds]
        lines.append(f"- {a} vs LRU: identical fault count in {sum(x == 0 for x in d)}/{len(d)} conditions, fewer faults in "
                     f"{sum(x > 0 for x in d)}, more in {sum(x < 0 for x in d)} (max reduction {max(d)} faults); "
                     f"switches per run: min {min(sw)}, max {max(sw)}; {sum(s > 0 for s in sw)}/{len(sw)} runs switched at least once.")
    wins = defaultdict(int)
    for k in conds:
        best = min(get(a, *k)["page_faults"] for a in online)
        for a in online:
            wins[a] += get(a, *k)["page_faults"] == best
    lines.append("- Conditions (of 36) where each online policy has the fewest faults (ties counted for all): "
                 + ", ".join(f"{a}={wins[a]}" for a in online) + ".")
    belady_path = os.path.join(RESULTS_DIR, "belady_anomaly.csv")
    if os.path.exists(belady_path):
        with open(belady_path, "r", encoding="utf-8") as f:
            brows = list(csv.DictReader(f))
        cl = {int(b["frame_capacity"]): int(b["page_faults"]) for b in brows if b["workload"].startswith("Classic")}
        syn_anom = sum(b["anomaly_demonstrated"] == "YES" for b in brows if not b["workload"].startswith("Classic"))
        lines.append(f"- Belady's Anomaly (FIFO): classic string 1,2,3,4,1,2,5,1,2,3,4,5 gives {cl.get(3)} faults with 3 frames "
                     f"and {cl.get(4)} faults with 4 frames. Synthetic N=1000 traces, frames 3-8: {syn_anom} anomalous steps.")
    mt = {a: np.mean([r["mean_time_sec"] for r in rows if r["algorithm"] == a]) * 1000 for a in online + ["Optimal"]}
    lines.append(f"- Runtime (mean over 36 conditions): FIFO {mt['FIFO']:.3f} ms, LRU {mt['LRU']:.3f} ms, Clock {mt['Clock']:.3f} ms, "
                 f"LFU {mt['LFU']:.3f} ms, Adaptive_W50 {mt['Adaptive_W50']:.3f} ms ({mt['Adaptive_W50']/mt['LRU']:.1f}x LRU), "
                 f"Adaptive_W100 {mt['Adaptive_W100']:.3f} ms ({mt['Adaptive_W100']/mt['LRU']:.1f}x LRU). Pure-Python simulation times, not kernel costs.")

    with open(summary_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated result summary at {summary_txt_path}")

if __name__ == "__main__":
    rows = load_summary_results()
    generate_plots(rows)
    generate_result_summary(rows)
