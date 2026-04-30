from __future__ import annotations

from dataclasses import dataclass

Grid = list[list[int]]  # 9x9, 0 means empty


def deep_copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def peers_of(r: int, c: int) -> set[tuple[int, int]]:
    peers: set[tuple[int, int]] = set()
    # Row & col
    for k in range(9):
        if k != c:
            peers.add((r, k))
        if k != r:
            peers.add((k, c))
    # Box
    br = (r // 3) * 3
    bc = (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if (rr, cc) != (r, c):
                peers.add((rr, cc))
    return peers


def is_valid_placement(grid: Grid, r: int, c: int, val: int) -> bool:
    if not (1 <= val <= 9):
        return False
    # Row
    if any(grid[r][cc] == val for cc in range(9) if cc != c):
        return False
    # Column
    if any(grid[rr][c] == val for rr in range(9) if rr != r):
        return False
    # Box
    br = (r // 3) * 3
    bc = (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if (rr, cc) != (r, c) and grid[rr][cc] == val:
                return False
    return True


def is_grid_valid(grid: Grid) -> bool:
    # Checks that all filled entries respect constraints.
    for r in range(9):
        for c in range(9):
            val = grid[r][c]
            if val == 0:
                continue
            if not is_valid_placement(grid, r, c, val):
                return False
    return True


def is_solved(grid: Grid) -> bool:
    return all(all(cell in range(1, 10) for cell in row) for row in grid) and is_grid_valid(grid)


@dataclass(frozen=True)
class SolveResult:
    solved: bool
    solution: Grid | None
    nodes_expanded: int


def _init_domains(grid: Grid) -> dict[tuple[int, int], set[int]]:
    domains: dict[tuple[int, int], set[int]] = {}
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                domains[(r, c)] = {grid[r][c]}
            else:
                domains[(r, c)] = {v for v in range(1, 10) if is_valid_placement(grid, r, c, v)}
    return domains


def _select_unassigned_var_mrv(grid: Grid, domains: dict[tuple[int, int], set[int]]) -> tuple[int, int] | None:
    best: tuple[int, int] | None = None
    best_size = 10
    for (r, c), dom in domains.items():
        if grid[r][c] != 0:
            continue
        size = len(dom)
        if size < best_size:
            best_size = size
            best = (r, c)
            if best_size == 1:
                break
    return best


def _forward_check(
    grid: Grid,
    domains: dict[tuple[int, int], set[int]],
    r: int,
    c: int,
    val: int,
) -> list[tuple[tuple[int, int], int]] | None:
    """
    Remove `val` from domains of peers of (r,c). Return a trail (var, removed_val)
    so we can undo on backtrack. Return None if any domain becomes empty.
    """
    trail: list[tuple[tuple[int, int], int]] = []
    for (rr, cc) in peers_of(r, c):
        if grid[rr][cc] != 0:
            continue
        dom = domains[(rr, cc)]
        if val in dom:
            dom.remove(val)
            trail.append(((rr, cc), val))
            if not dom:
                # dead end
                for (var, removed) in trail:
                    domains[var].add(removed)
                return None
    return trail


def _order_values_lcv(dom: set[int], grid: Grid, r: int, c: int) -> list[int]:
    # Least Constraining Value: prefer values that eliminate fewer options in peers.
    def impact(v: int) -> int:
        score = 0
        for (rr, cc) in peers_of(r, c):
            if grid[rr][cc] == 0 and is_valid_placement(grid, rr, cc, v):
                score += 1
        return score

    return sorted(dom, key=impact, reverse=True)


def solve_csp(initial_grid: Grid, *, node_limit: int = 2_000_000) -> SolveResult:
    """
    Backtracking CSP solver with:
    - MRV variable ordering
    - LCV value ordering (lightweight)
    - Forward-checking
    """
    grid = deep_copy_grid(initial_grid)
    if not is_grid_valid(grid):
        return SolveResult(solved=False, solution=None, nodes_expanded=0)

    domains = _init_domains(grid)
    nodes = 0

    def backtrack() -> bool:
        nonlocal nodes
        if nodes >= node_limit:
            return False
        var = _select_unassigned_var_mrv(grid, domains)
        if var is None:
            return True
        r, c = var
        dom = domains[(r, c)]
        if not dom:
            return False
        for val in _order_values_lcv(set(dom), grid, r, c):
            if not is_valid_placement(grid, r, c, val):
                continue
            nodes += 1
            # assign
            grid[r][c] = val
            old_dom = domains[(r, c)]
            domains[(r, c)] = {val}
            trail = _forward_check(grid, domains, r, c, val)
            if trail is not None and backtrack():
                return True
            # undo
            if trail is not None:
                for (var2, removed) in trail:
                    domains[var2].add(removed)
            domains[(r, c)] = old_dom
            grid[r][c] = 0
        return False

    ok = backtrack()
    return SolveResult(solved=ok and is_solved(grid), solution=deep_copy_grid(grid) if ok else None, nodes_expanded=nodes)

