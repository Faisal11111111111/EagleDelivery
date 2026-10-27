# Eagle Delivery

Faisal Abusara - COSC 461, Project 1

This project simulates a delivery robot on an Eastern Michigan University campus
map. It compares A* with the provided BFS baseline, learns routes with tabular
Q-learning, and tests how exploration affects learning on a custom map.

## Requirements

Python 3.9 or newer. The simulator, algorithms, tests, and experiment runner use
only the Python standard library. To recreate the graphs and PDF report:

```bash
python -m pip install -r requirements.txt
```

Run commands from this project's folder. On systems that use `python3`, replace
`python` with `python3` in the commands below.

## Main files

- `agents.py`: completed Manhattan distance, A*, epsilon-greedy selection,
  and Q-learning update; the provided BFS is unchanged.
- `campus.py`, `run_project.py`, `summarize_results.py`: original simulator,
  training/evaluation runner, and summary utility.
- `maps/emu_campus.txt`, `maps/emu_detour.txt`: supplied maps.
- `maps/my_campus.txt`: custom 11-by-17 map with loops and dead-end branches.
- `tests/`: the supplied environment and student tests.
- `examples/interaction_demo.py`: the supplied interaction demonstration.
- `run_experiments.py`: reproduces every required search and learning run.
- `plot_results.py`: creates comparison CSVs and graphs from saved results.
- `make_report.py`: rebuilds the three-page PDF using the submitted results.
- `experiment_plan.md`: Part C question, prediction, controls, and map description.
- `results/`: raw training and evaluation CSVs, summaries, commands, and logs.
- `plots/`: training graphs and a drawing of the custom map.
- `EagleDelivery_Report.pdf`: the three-page project report.

## Check the code

```bash
python -m unittest discover -v
python run_project.py show
python run_project.py search --algorithm bfs --start S --goal W
python run_project.py search --algorithm astar --start S --goal W
python run_project.py search --algorithm astar --map maps/emu_detour.txt --start L --goal D
python run_project.py search --algorithm astar --map maps/my_campus.txt --start S --goal W
```

All 14 supplied tests pass. A* preserves the supplied neighbor order, uses
insertion-order heap ties, accepts strict cost improvements, skips stale queue
entries, and counts a node only when generating its successors. The goal itself
is not counted. The Q-learning functions do not use search or RL libraries.

## Required experiments

Each task/condition uses independent seeds **0, 1, 2**, a fresh Q-table per seed,
**2,000 training episodes**, **100 evaluation episodes**, and at most **200
actions** per episode. Other defaults are alpha **0.3**, gamma **0.95**, constant
epsilon **0.2**, and slip **0.0**. Evaluation freezes learning and sets epsilon to
zero. Hitting a wall still costs one action. A successful delivery of length L
has return 40 - L.

The completed results are included, so there is no need to rerun training to
read the report. To repeat all comparisons and all 18 training runs, use a new
output directory:

```bash
python run_experiments.py --output results_rerun
python plot_results.py --results results_rerun --output plots_rerun
```

Never overwrite an existing run folder. The supplied runner and the experiment
script reject folders that already contain result CSVs.

The baseline commands used for the submitted results were equivalent to:

```bash
python run_project.py train --map maps/emu_campus.txt --start S --goal W --output results/baseline_SW
python run_project.py train --map maps/emu_campus.txt --start L --goal D --output results/baseline_LD
python run_project.py train --map maps/emu_campus.txt --start H --goal P --output results/baseline_HP
python summarize_results.py results/baseline_SW
python summarize_results.py results/baseline_LD
python summarize_results.py results/baseline_HP
```

### Part C: exploration rate

Question: How does the exploration rate affect learning and final S-W delivery
performance on the custom map? The prediction was recorded in
`experiment_plan.md` before running training.

Only training epsilon changed: **0.05, 0.2, 0.5**. All other settings stayed the
same. Each setting used seeds 0, 1, and 2 with fresh Q-tables. The submitted
commands were equivalent to:

```bash
python run_project.py train --map maps/my_campus.txt --epsilon 0.05 --output results/custom_e005
python run_project.py train --map maps/my_campus.txt --epsilon 0.2 --output results/custom_e020
python run_project.py train --map maps/my_campus.txt --epsilon 0.5 --output results/custom_e050
python summarize_results.py results/custom_e005
python summarize_results.py results/custom_e020
python summarize_results.py results/custom_e050
```

The map has a loop with zero-based corners (3,1), (3,15), (7,15), (7,1).
The branch from (3,7) ends at D = (5,7). There are also dead ends at (9,1) and
(9,15). The shortest S-W route takes 18 actions; a lower route through row 7
takes 26. All six entrances are connected and appear exactly once.

## Results

| Map | Task | BFS length | A* length | BFS expanded | A* expanded |
| --- | --- | ---: | ---: | ---: | ---: |
| Baseline | S-W | 18 | 18 | 67 | 22 |
| Baseline | L-D | 22 | 22 | 79 | 62 |
| Baseline | H-P | 16 | 16 | 41 | 16 |
| Detour | S-W | 26 | 26 | 70 | 51 |
| Detour | L-D | 22 | 22 | 65 | 60 |
| Detour | H-P | 16 | 16 | 41 | 16 |
| Custom | S-W | 18 | 18 | 53 | 32 |

All baseline and custom evaluations succeeded and matched the shortest route
length for their task. This is 1,800 evaluation episodes from 18 independently
trained tables. Late custom-map training averaged 19.00, 22.79, and 35.35 steps
for epsilon 0.05, 0.2, and 0.5, respectively. All three settings then achieved
18-step deliveries during evaluation. These results apply to the tested maps,
settings, and seeds; they do not show that low exploration is always best.

Each run folder includes `training_seed0.csv` through `training_seed2.csv`,
`evaluation_seed0.csv` through `evaluation_seed2.csv`, `summary.csv`, and
`learning_curve.csv`. It also contains the actual command and output logs.
Failed/truncated episodes are retained. `summary.csv` records settings and
per-seed evaluation results. Learning curves average non-overlapping blocks of
100 training episodes across the three seeds.

Top-level comparison files include:

- `results/search_comparison.csv` and `results/search_routes.txt`
- `results/evaluation_comparison.csv`
- `results/training_windows.csv` and `results/training_windows_by_seed.csv`

Recreate the figures and report from the submitted data:

```bash
python plot_results.py
python make_report.py
```

## Submission

Keep the code, all three maps, raw CSVs, summaries, figures, this README, and the
PDF report in a public GitHub repository named exactly `EagleDelivery`. Submit
the repository link to Canvas under **Project 1: Eagle Delivery**.
