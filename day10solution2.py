import sys
from collections import deque
from itertools import zip_longest
from fractions import Fraction

# ----------------------------
# Parsing
# ----------------------------

def parse_machine_line(line: str):
    """
    Parses one line like:
    [#.##.] (0,2) (1,3) {3,5,4,7}

    Returns:
      pattern: str (inside [])
      buttons: list[list[int]]
      target: list[int]  (inside {})
    """
    line = line.strip()
    if not line:
        return None

    lb = line.find("[")
    rb = line.find("]", lb + 1)
    if lb == -1 or rb == -1:
        raise ValueError(f"Bad machine line (missing [...]): {line}")
    pattern = line[lb + 1 : rb]

    # all (...) groups
    buttons = []
    i = rb + 1
    while True:
        l = line.find("(", i)
        if l == -1:
            break
        r = line.find(")", l + 1)
        if r == -1:
            raise ValueError(f"Bad machine line (missing ')'): {line}")
        inside = line[l + 1 : r].strip()
        if inside:
            buttons.append([int(x.strip()) for x in inside.split(",") if x.strip()])
        else:
            buttons.append([])
        i = r + 1

    # {...} group
    l = line.find("{")
    r = line.find("}", l + 1) if l != -1 else -1
    if l == -1 or r == -1:
        raise ValueError(f"Bad machine line (missing {{...}}): {line}")
    inside = line[l + 1 : r].strip()
    target = [int(x.strip()) for x in inside.split(",") if x.strip()]

    return pattern, buttons, target


def load_machines(filename: str):
    """
    Reads your input file: one machine per line, like your previous scripts.
    """
    machines = []
    with open(filename, "r", newline="") as f:
        for line_no, line in enumerate(f, 1):
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip():
                continue
            parsed = parse_machine_line(line)
            if parsed is None:
                continue
            machines.append(parsed)
    return machines


# ----------------------------
# Part 1: Fewest presses to match indicator pattern (toggle mod 2)
# ----------------------------

def min_presses_lights(pattern: str, buttons: list[list[int]]) -> int | None:
    """
    Solve over GF(2) with BFS on bitmasks (works when number of lights is modest).
    Returns minimum number of presses, or None if impossible.

    Each button press toggles listed lights (XOR).
    """
    n = len(pattern)
    target = 0
    for i, ch in enumerate(pattern):
        if ch == "#":
            target |= (1 << i)

    masks = []
    for b in buttons:
        mask = 0
        for idx in b:
            if 0 <= idx < n:
                mask ^= (1 << idx)
        masks.append(mask)

    # BFS from 0 to target
    dist = {0: 0}
    q = deque([0])
    while q:
        state = q.popleft()
        d = dist[state]
        if state == target:
            return d
        for bm in masks:
            nxt = state ^ bm
            if nxt not in dist:
                dist[nxt] = d + 1
                q.append(nxt)
    return None


def total_min_presses_lights(filename: str) -> int:
    machines = load_machines(filename)
    total = 0
    for i, (pattern, buttons, _target) in enumerate(machines, 1):
        ans = min_presses_lights(pattern, buttons)
        if ans is None:
            raise ValueError(f"Machine {i} (lights) is impossible.")
        total += ans
    return total


# ----------------------------
# Part 2: Fewest presses to reach joltage target (nonnegative integers)
# ----------------------------

def min_presses_joltage(target: list[int], buttons: list[list[int]]) -> int | None:
    """
    Solve Ax = target with x >= 0 integers, minimizing sum(x).

    Uses exact rational linear algebra:
    - Compute RREF to get affine family x = c + Σ t_i v_i
    - Best-first search (heap) over integer t_i inside a bounded window

    NOTE: This is the same general approach as earlier, but now wired to file input.
    """
    import heapq
    import sympy as sp

    m = len(target)
    k = len(buttons)

    A = sp.Matrix([[1 if i in buttons[j] else 0 for j in range(k)] for i in range(m)])
    b = sp.Matrix(target)

    M = A.row_join(b)
    rref, pivots = M.rref()

    # inconsistency check
    for r in range(m):
        if all(rref[r, c] == 0 for c in range(k)) and rref[r, k] != 0:
            return None

    pivots = list(pivots)
    free_cols = [c for c in range(k) if c not in pivots]

    # unique solution
    if not free_cols:
        x = [0] * k
        for row, pc in enumerate(pivots):
            v = sp.nsimplify(rref[row, k])
            if not v.is_rational or v.denominator != 1:
                return None
            iv = int(v)
            if iv < 0:
                return None
            x[pc] = iv
        if A * sp.Matrix(x) != b:
            return None
        return sum(x)

    free_syms = sp.symbols(" ".join(f"t{c}" for c in free_cols), integer=True)
    if len(free_cols) == 1:
        free_syms = (free_syms,)

    # build expressions
    expr = {fc: free_syms[i] for i, fc in enumerate(free_cols)}
    for row, pc in enumerate(pivots):
        e = rref[row, k]
        for fc in free_cols:
            coeff = rref[row, fc]
            if coeff != 0:
                e -= coeff * expr[fc]
        expr[pc] = sp.simplify(e)
    for j in range(k):
        if j not in expr:
            expr[j] = sp.Integer(0)

    # affine rational coefficients
    zero_subs = {sym: 0 for sym in free_syms}
    affine_const = [sp.Rational(0) for _ in range(k)]
    affine_coeffs = [[sp.Rational(0) for _ in range(len(free_cols))] for _ in range(k)]

    for j in range(k):
        e = sp.simplify(expr[j])
        c0 = sp.nsimplify(e.subs(zero_subs))
        if not c0.is_rational:
            return None
        affine_const[j] = sp.Rational(c0)

        lin = affine_const[j]
        for i, sym in enumerate(free_syms):
            ci = sp.nsimplify(sp.diff(e, sym))
            if not ci.is_rational:
                return None
            affine_coeffs[j][i] = sp.Rational(ci)
            if ci:
                lin += affine_coeffs[j][i] * sym

        if sp.simplify(e - lin) != 0:
            raise ValueError("Nonlinear parameterization encountered.")

    obj_const = sum(affine_const)
    obj_coeff = [sum(affine_coeffs[j][i] for j in range(k)) for i in range(len(free_cols))]

    # soft penalty in primary priority to avoid boundary-crawl
    PEN_DEN = 100000

    def priority(vals):
        primary = obj_const + sum(obj_coeff[i] * vals[i] for i in range(len(vals)))
        size = sum(abs(v) for v in vals)
        return (primary, size)


    def eval_x(vals):
        x = [0] * k
        for j in range(k):
            v = affine_const[j]
            for i in range(len(free_cols)):
                v += affine_coeffs[j][i] * vals[i]
            if v.denominator != 1 or v < 0:
                return None
            x[j] = int(v)
        return x

    L = sum(target)  # safe window
    start = tuple(0 for _ in range(len(free_cols)))
    seen = {start}
    pq = [(priority(start), start)]

    while pq:
        _, vals = heapq.heappop(pq)
        x = eval_x(vals)
        if x is not None and A * sp.Matrix(x) == b:
            return sum(x)

        for i in range(len(free_cols)):
            for delta in (-1, 1):
                nxt = list(vals)
                nxt[i] += delta
                if nxt[i] < -L or nxt[i] > L:
                    continue
                nxt = tuple(nxt)
                if nxt in seen:
                    continue
                seen.add(nxt)
                heapq.heappush(pq, (priority(nxt), nxt))

    return None


def total_min_presses_joltage(filename: str, *, progress=False) -> int:
    machines = load_machines(filename)
    total = 0
    for i, (_pattern, buttons, target) in enumerate(machines, 1):
        ans = min_presses_joltage(target, buttons)
        if ans is None:
            raise ValueError(f"Machine {i} (joltage) is impossible.")
        total += ans
        if progress and i % 10 == 0:
            print(f"processed {i}/{len(machines)} machines...")
    return total


# ----------------------------
# CLI usage
# ----------------------------

if __name__ == "__main__":
    # Example:
    # python day10_pt2.py day10input.txt joltage
    # python day10_pt2.py day10input.txt lights
    if len(sys.argv) < 3:
        print("Usage: python script.py <inputfile> <lights|joltage>")
        raise SystemExit(2)

    filename = sys.argv[1]
    mode = sys.argv[2].lower()

    if mode == "lights":
        print(total_min_presses_lights(filename))
    elif mode == "joltage":
        print(total_min_presses_joltage(filename, progress=True))
    else:
        raise ValueError("mode must be 'lights' or 'joltage'")
