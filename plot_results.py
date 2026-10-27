"""Summarize the saved CSVs and recreate the report figures."""
import argparse
import csv
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

import agents
from campus import CampusMap

CONDITIONS = [
    ("baseline_SW", "S-W"), ("baseline_LD", "L-D"), ("baseline_HP", "H-P"),
    ("custom_e005", "epsilon = 0.05"), ("custom_e020", "epsilon = 0.20"),
    ("custom_e050", "epsilon = 0.50"),
]
COLORS = ["#17648d", "#ba551d", "#26816d"]


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(root):
    evaluation, windows, per_seed = [], [], []
    for name, label in CONDITIONS:
        folder = root / name
        summaries = read_csv(folder / "summary.csv")
        row = {"condition": name, "task": summaries[0]["start"] + "-" + summaries[0]["goal"],
               "epsilon": float(summaries[0]["epsilon"]), "seeds": len(summaries),
               "evaluation_episodes": sum(int(s["eval_episodes"]) for s in summaries)}
        for field in ("success_rate", "mean_return", "mean_steps_success"):
            values = [float(s[field]) for s in summaries if s[field] != "NA"]
            row[field] = statistics.mean(values) if values else "NA"
            row[field + "_sd"] = statistics.stdev(values) if len(values) > 1 else 0.0
        evaluation.append(row)

        all_runs = []
        for summary in summaries:
            records = read_csv(folder / ("training_seed" + summary["seed"] + ".csv"))
            all_runs.append(records)
            for window, first, last in (("first100", 0, 100), ("last100", 1900, 2000),
                                         ("all", 0, 2000)):
                selected = records[first:last]
                per_seed.append({"condition": name, "seed": int(summary["seed"]),
                    "window": window, "episodes": len(selected),
                    "success_rate": statistics.mean(int(r["success"]) for r in selected),
                    "mean_steps": statistics.mean(int(r["steps"]) for r in selected),
                    "mean_return": statistics.mean(int(r["return"]) for r in selected),
                    "truncated": sum(int(r["truncated"]) for r in selected)})
        for window, first, last in (("first100", 0, 100), ("last100", 1900, 2000),
                                     ("all", 0, 2000)):
            selected = [r for records in all_runs for r in records[first:last]]
            windows.append({"condition": name, "window": window, "episodes": len(selected),
                "success_rate": statistics.mean(int(r["success"]) for r in selected),
                "mean_steps": statistics.mean(int(r["steps"]) for r in selected),
                "mean_return": statistics.mean(int(r["return"]) for r in selected),
                "truncated": sum(int(r["truncated"]) for r in selected)})
    write_csv(root / "evaluation_comparison.csv", evaluation)
    write_csv(root / "training_windows.csv", windows)
    write_csv(root / "training_windows_by_seed.csv", per_seed)


def learning_plot(root, output, conditions, name):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.6), layout="constrained")
    for (folder, label), color in zip(conditions, COLORS):
        rows = read_csv(root / folder / "learning_curve.csv")
        x = [int(r["episode_end"]) for r in rows]
        for ax, key, scale in zip(axes, ("mean_training_success_rate", "mean_training_return"), (100, 1)):
            y = [float(r[key]) * scale for r in rows]
            ax.plot(x, y, label=label, color=color, linewidth=1.8)
    axes[0].set_ylabel("Successful training episodes (%)")
    axes[0].set_ylim(75, 101.5)
    axes[1].set_ylabel("Mean training return")
    for ax in axes:
        ax.set_xlabel("Training episode (100-episode blocks)")
        ax.set_xlim(0, 2000)
        ax.set_xticks([0, 500, 1000, 1500, 2000])
        ax.grid(axis="y", alpha=0.25)
        ax.spines[["top", "right"]].set_visible(False)
    axes[1].legend(loc="lower right", frameon=False, fontsize=8)
    fig.savefig(output / (name + ".png"), dpi=220)
    plt.close(fig)


def draw_map(output):
    campus = CampusMap("maps/my_campus.txt")
    result = agents.astar(campus, campus.location("S"), campus.location("W"))
    cells = [[0 if value == "#" else 1 for value in row] for row in campus.rows]
    fig, ax = plt.subplots(figsize=(4.5, 2.9), layout="constrained")
    ax.imshow(cells, cmap=ListedColormap(["#293540", "#f4f6f7"]), vmin=0, vmax=1,
              interpolation="nearest")
    ax.plot([s[1] for s in result.path], [s[0] for s in result.path],
            color="#53b6e2", linewidth=2.2, zorder=2)
    for letter, (row, col) in campus.locations.items():
        ax.text(col, row, letter, ha="center", va="center", fontsize=10,
                weight="bold", color="#b34e16" if letter == "D" else "#111111", zorder=3)
    ax.set_xticks(range(0, campus.width, 2))
    ax.set_yticks(range(0, campus.height, 2))
    ax.set_xlabel("Column (zero-based)")
    ax.set_ylabel("Row")
    ax.set_title("Custom campus: blue route = 18 actions", fontsize=10)
    ax.tick_params(labelsize=8)
    fig.savefig(output / "custom_map.png", dpi=220)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="results")
    parser.add_argument("--output", default="plots")
    args = parser.parse_args()
    root, output = Path(args.results), Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5})
    summarize(root)
    learning_plot(root, output, CONDITIONS[:3], "baseline_learning")
    learning_plot(root, output, CONDITIONS[3:], "custom_exploration")
    draw_map(output)
    print("Saved comparison CSVs to", root, "and three figures to", output)


if __name__ == "__main__":
    main()
