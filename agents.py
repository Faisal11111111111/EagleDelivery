from collections import deque
import heapq
from itertools import count


class SearchResult:
    def __init__(self, path, expanded):
        self.path = path
        self.expanded = expanded


def reconstruct_path(parents, goal):
    path = []
    state = goal
    while state is not None:
        path.append(state)
        state = parents[state]
    path.reverse()
    return path


def bfs(campus, start, goal):
    frontier = deque([start])
    parents = {start: None}
    expanded = 0
    while frontier:
        state = frontier.popleft()
        if state == goal:
            return SearchResult(reconstruct_path(parents, goal), expanded)
        expanded += 1
        for action, successor in campus.neighbors(state):
            if successor not in parents:
                parents[successor] = state
                frontier.append(successor)
    return SearchResult(None, expanded)


def manhattan(state, goal):
    """Return the row distance plus the column distance."""
    return abs(state[0] - goal[0]) + abs(state[1] - goal[1])


def astar(campus, start, goal):
    """Find a shortest route using A* and Manhattan distance."""
    insertion_order = count()
    frontier = [(manhattan(start, goal), next(insertion_order), 0, start)]
    best_g = {start: 0}
    parents = {start: None}
    expanded = 0

    while frontier:
        _, _, g, state = heapq.heappop(frontier)
        # A cheaper route may have replaced this queued entry.
        if g != best_g[state]:
            continue
        if state == goal:
            return SearchResult(reconstruct_path(parents, goal), expanded)

        expanded += 1
        for action, successor in campus.neighbors(state):
            new_g = g + 1
            if new_g < best_g.get(successor, float("inf")):
                best_g[successor] = new_g
                parents[successor] = state
                f = new_g + manhattan(successor, goal)
                heapq.heappush(frontier, (f, next(insertion_order), new_g, successor))

    return SearchResult(None, expanded)


def epsilon_greedy(q_values, state, actions, epsilon, rng):
    """Explore randomly, or choose randomly among the best actions."""
    if rng.random() < epsilon:
        return rng.choice(actions)

    best_value = max(q_values.get((state, action), 0.0) for action in actions)
    best_actions = [action for action in actions
                    if q_values.get((state, action), 0.0) == best_value]
    return rng.choice(best_actions)


def q_learning_update(q_values, state, action, reward, next_state,
                      actions, alpha, gamma, terminal):
    """Update only the state-action value for the observed transition."""
    old_value = q_values.get((state, action), 0.0)
    target = reward
    if not terminal:
        next_best = max(q_values.get((next_state, next_action), 0.0)
                        for next_action in actions)
        target += gamma * next_best
    q_values[(state, action)] = old_value + alpha * (target - old_value)
