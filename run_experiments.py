"""Reproduce all required search, training, and evaluation results."""
import argparse
import csv
from pathlib import Path
import subprocess
import sys

import agents
from campus import CampusMap


def run_command(arguments, log_path):
    result = subprocess.run([sys.executable] + arguments, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            check=True)
    log_path.write_text(result.stdout, encoding="utf-8")
    print(result.stdout, end="")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="results",
                        help="Use a new directory when repeating the experiment.")
    args = parser.parse_args()
    root = Path(args.output)
    if root.exists() and any(root.rglob("*.csv")):
        parser.error("Results already exist. Choose a new --output directory.")
    root.mkdir(parents=True, exist_ok=True)
    search_rows = []
    routes = []
    for map_name in ("emu_campus", "emu_detour", "my_campus"):
        campus = CampusMap("maps/" + map_name + ".txt")
        tasks = [("S", "W")] if map_name == "my_campus" else [
            ("S", "W"), ("L", "D"), ("H", "P")]
        for first, last in tasks:
            start, goal = campus.location(first), campus.location(last)
            row = {"map": map_name, "task": first + "-" + last}
            for name, algorithm in (("bfs", agents.bfs), ("astar", agents.astar)):
                result = algorithm(campus, start, goal)
                length = len(result.path) - 1 if result.path is not None else "NA"
                row[name + "_length"] = length
                row[name + "_expanded"] = result.expanded
                routes.append("{} {} {}: length={}, expanded={}\n{}\nPath: {}\n".format(
                    map_name, row["task"], name, length, result.expanded,
                    campus.render(path=result.path), result.path))
            search_rows.append(row)
    with (root / "search_comparison.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["map", "task", "bfs_length",
            "astar_length", "bfs_expanded", "astar_expanded"])
        writer.writeheader()
        writer.writerows(search_rows)
    (root / "search_routes.txt").write_text("\n".join(routes), encoding="utf-8")

    conditions = [
        ("baseline_SW", "emu_campus", "S", "W", 0.2),
        ("baseline_LD", "emu_campus", "L", "D", 0.2),
        ("baseline_HP", "emu_campus", "H", "P", 0.2),
        ("custom_e005", "my_campus", "S", "W", 0.05),
        ("custom_e020", "my_campus", "S", "W", 0.2),
        ("custom_e050", "my_campus", "S", "W", 0.5),
    ]
    for name, map_name, start, goal, epsilon in conditions:
        folder = root / name
        folder.mkdir()
        command = ["run_project.py", "train", "--map", "maps/" + map_name + ".txt",
                   "--start", start, "--goal", goal, "--epsilon", str(epsilon),
                   "--alpha", "0.3", "--gamma", "0.95", "--slip", "0",
                   "--episodes", "2000", "--eval-episodes", "100",
                   "--max-steps", "200", "--seeds", "0", "1", "2",
                   "--output", str(folder)]
        (folder / "command.txt").write_text("python " + " ".join(command) + "\n")
        run_command(command, folder / "run_log.txt")
        run_command(["summarize_results.py", str(folder)], folder / "summary.txt")


if __name__ == "__main__":
    main()
