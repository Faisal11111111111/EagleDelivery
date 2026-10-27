# Part C experiment plan

This question and prediction were written before running the learning experiment.

**Question:** How does the exploration rate affect learning and final delivery
performance on the custom map's S-W task?

**Prediction:** Epsilon 0.05 should use fewer unnecessary actions once it finds a
good route. Epsilon 0.5 should explore more, but its extra random actions should
make training deliveries longer. Epsilon 0.2 may give a useful balance. After
2,000 episodes, all three settings may learn the same shortest route when
evaluated with exploration turned off.

**Changed factor:** Constant training epsilon = 0.05, 0.2, or 0.5.

**Kept fixed:** The custom map, S-W task, alpha 0.3, gamma 0.95, slip 0,
2,000 training episodes per seed, 100 evaluation episodes per seed, and a
200-action limit. Use seeds 0, 1, and 2 for every setting, with a fresh Q-table
for each run. Evaluation freezes learning and uses epsilon 0.

**Measures:** Training success and mean return in 100-episode blocks; steps,
return, and success rate in the first and last 100 training episodes; final
evaluation success, successful-delivery steps, and return for each seed.
Keep all failed and truncated episodes in the raw results.

**Map design:** 11 rows by 17 columns, with a blocked border and each of S, L,
H, D, P, W exactly once. Coordinates are zero-based (row, column). The main loop
has corners (3,1), (3,15), (7,15), (7,1). The branch from (3,7) through (4,7)
ends at D = (5,7). Additional dead ends lie at (9,1) and (9,15). The wall at
(1,8) prevents a straight top-row delivery. The upper crossing through row 3
offers a shorter route than the lower crossing through row 7. All entrances
are connected.
