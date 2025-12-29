import sys
import time
import math
import numbers
import itertools
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from itertools import zip_longest
from fractions import Fraction

###

def pm(mat, title=""):
    if title:
        print(title)
    for row in mat:
        print(" ".join(map(lambda x: f"{x}", row)))
    print(flush=True)


def reduce_matrix(mat):
    log = False

    n = min(len(mat), len(mat[0]))

    cur_row = 0
    # for col in range(n):
    col = -1
    while cur_row < len(mat):
        col += 1
        if col >= len(mat[0]):
            break

        # Swap in first non-zero row
        found1 = False
        for r in range(cur_row, len(mat)):
            if mat[r][col] == 0:
                continue

            found1 = True
            if r == cur_row:
                break

            tmp = mat[r]
            mat[r] = mat[cur_row]
            mat[cur_row] = tmp

            log and pm(mat, f"{cur_row=} {col=} swapped")
            break

        if not found1:
            continue

        # Make the value 1
        if mat[cur_row][col] != 1:
            ratio = Fraction(1, mat[cur_row][col])
            for c in range(col, len(mat[cur_row])):
                mat[cur_row][c] *= ratio
            log and pm(mat, f"{cur_row=} {col=} normalized")

        # Reduce all other rows
        zeroed = False
        for row in mat[cur_row +1:]:
            if row[col] == 0:
                continue
            zeroed = True
            for c in range(len(row) - 1, col - 1, -1):
                row[c] -= mat[cur_row][c] * Fraction(row[col], mat[cur_row][col])
        if zeroed:
            log and pm(mat, f"{cur_row=} {col=} zero'd out rest")

        cur_row += 1


def reduce_limits(vals, params):
    log = False

    limit_updated = True
    limits = [
        [0, math.inf] if p is None else [p, p]
        for p in params
    ]

    while limit_updated:
        limit_updated = False

        for val in vals:
            log and print("val:", val)

            for i, p in enumerate(params):
                log and print(f"param {i}: {p} | {val[i]}")
                if p is not None or val[i] == 0:
                    continue

                gtsum = [-val[-1], -val[-1]]
                for j, q in enumerate(params):
                    if j == i or val[j] == 0:
                        continue

                    if q is not None:
                        gtsum = [g - q * val[j] for g in gtsum]
                    else:
                        pl = sorted([val[j] * limits[j][k] for k in range(2)])
                        gtsum = [g - m for (g, m) in zip(gtsum, pl)]

                gtsum = sorted([g / val[i] for g in gtsum])
                if val[i] > 0:
                    if limits[i][0] < gtsum[0]:
                        limits[i][0] = math.ceil(gtsum[0])
                        limit_updated = True
                else:
                    if limits[i][1] > gtsum[1]:
                        limits[i][1] = math.floor(gtsum[1])
                        limit_updated = True

                log and print("limits", limits)

        all_set = True
        for limit in limits:
            if any(l is math.inf for l in limit):
                all_set = False
                break

    log and print("final limits", limits)
    return limits


def solve_val_constraints(vals, total_val, params=None):
    dims = len(vals[0])
    log = False
    checks = []

    log and print("params", params, all(p is not None for p in params) if params else None)
    if params is None:
        params = [None] * (dims -1)
    else:
        params = list(params)

    if all(p is not None for p in params):
        lcm = 1
        total = 0
        for val in vals:
            v = val[-1] + sum(a * b for (a, b) in zip(params, val))
            log and print("val check", v, val)
            assert v >= 0, f"val check failed {val}"
            assert Fraction(v).denominator == 1, f"All vals must be integers {v}"
            total += v

        return total

    # Repeatedly check limits and update bounds
    limits = reduce_limits(vals, params)

    for k, limit in enumerate(limits):
        if limit[1] is not None and limit[0] > limit[1]:
            assert False, "Impossible limits found"

    log and print()
    log and print("limits", limits, params)
    candidates = [x for x in enumerate(limits) if params[x[0]] is None]

    # Prefer parameters that are "safe" to search:
    # 1) finite width bounds
    finite = [x for x in candidates if x[1][1] is not math.inf and x[1][0] is not -math.inf]
    if finite:
        explore = min(finite, key=lambda x: x[1][1] - x[1][0])
    else:
        # 2) avoid choosing a negatively-weighted param with +inf upper bound
        safe = [x for x in candidates if not (total_val[x[0]] < 0 and x[1][1] is math.inf)]
        if safe:
            explore = min(safe, key=lambda x: (x[1][1] if x[1][1] is not None else math.inf) - x[1][0])
        else:
            # fallback: original behavior
            explore = min(candidates, key=lambda x: (x[1][1] or math.inf) - x[1][0])

    log and print(f"Walking limit: {explore}")

    increment = Fraction(1, math.lcm(*[
        Fraction(g).denominator for g in explore[1] if g is not math.inf and g is not -math.inf
    ]))
    log and print("increment", increment)

    min_total = None

    if total_val[explore[0]] >= 0:
        guess = explore[1][0]
        unbounded = explore[1][1] is math.inf
        while (min_total is None and unbounded) or (not unbounded and guess <= explore[1][1]):
            params[explore[0]] = guess
            try:
                result = solve_val_constraints(vals, total_val, params)
                if min_total is None or min_total > result:
                    min_total = result
            except Exception as e:
                log and print(e)
            guess += increment
    else:
        assert explore[1][1] is not math.inf, "Starting from an infinite limit"
        unbounded = explore[1][0] is -math.inf
        guess = explore[1][1]
        while (min_total is None and unbounded) or (not unbounded and guess >= explore[1][0]):
            params[explore[0]] = guess
            try:
                result = solve_val_constraints(vals, total_val, params)
                if min_total is None or min_total > result:
                    min_total = result
            except Exception as e:
                log and print(e)
            guess -= increment

    if min_total is not None:
        return min_total
    assert False, "No guess worked"


def val_constraints(vals):
    log = False

    dims = len(vals[0])
    log and pm(vals, "vals")
    total_val = [0] * dims
    for d in range(dims):
        total_val[d] = sum(v[d] for v in vals)
    log and print("total", total_val)

    return solve_val_constraints(vals, total_val)


def matrix_solve(machine):
    log = False
    start_time_s = time.time()

    idx, (joltage, combos) = machine
    log and print(machine)
    log and print(f"START {idx}", flush=True)

    matrix = [[] for _ in joltage]

    for i in range(len(joltage)):
        for j, combo in enumerate(combos):
            matrix[i].append(combo[i] if i < len(combo) else 0)
        matrix[i].append(joltage[i])

    log and pm(matrix, "start")
    reduce_matrix(matrix)
    log and pm(matrix, "reduced")

    constraints = sum(any(x != 0 for x in row) for row in matrix)
    variables = len(combos)
    log and print(f"{variables=} {constraints=}", flush=True)
    assert variables >= constraints

    if variables == constraints:
        vals = [0] * variables
        for k in range(variables - 1, -1, -1):
            vals[k] = matrix[k][-1]
            for l in range(k + 1, variables):
                vals[k] -= matrix[k][l] * vals[l]

        log and print("exact")
        log and print(",".join(map(str, vals)))
        log and print(sum(vals))

        dur_s = time.time() - start_time_s
        log and print(f"DONE {idx} ({dur_s})", flush=True)
        return sum(vals)

    dims = (variables - constraints + 1)
    vals = [[0] * dims  for _ in range(variables)]

    param_idx = 0
    row = 0
    for i in range(variables):
        if row < constraints and matrix[row][i] != 0:
            row += 1
        else:
            vals[i][param_idx] = 1
            param_idx += 1
    assert param_idx == dims - 1

    for k in range(constraints - 1, -1, -1):
        col = 0
        while matrix[k][col] == 0:
            col += 1

        vals[col][-1] = matrix[k][-1]
        for l in range(col + 1, variables):
            for m in range(dims):
                 vals[col][m] -= matrix[k][l] * vals[l][m]

    result = val_constraints(vals)

    log and print("result: ", result)
    log and print()

    dur_s = time.time() - start_time_s
    log and print(f"DONE {idx} ({dur_s})", flush=True)
    return result

###


def make_tuple(combo):
    result = [0] * (max(combo) + 1)
    for x in combo:
        result[x] += 1
    return tuple(result)


def make_number(elems):
    num = 0
    for elem in elems:
        num |= (1 << elem)
    return num


def dist(num, state):
    return 0

    x = num ^ state
    count = 0
    while x != 0:
        x &= (x-1)
        count += 1
    return count


def solve(machine):
    # accept either (idx, (state, combos)) OR (idx, state, combos)
    if len(machine) == 2:
        idx, (state, combos) = machine
    else:
        idx, state, combos = machine

    steps = 0
    root = 0
    visited = set()
    fringe = {0: 0}
    costs = {}

    while True:
        start_node = min(fringe.items(), key=lambda x: x[1] + dist(state, x[0]))
        fringe.pop(start_node[0])
        if start_node[0] == state:
            # print(idx, state, combos, start_node)
            return start_node[1]

        for combo in combos:
            next_node = start_node[0] ^ combo
            if next_node not in fringe:
                fringe[next_node] = start_node[1] + 1

    1/0

def main():
    if len(sys.argv) < 2:
        print("Usage: python day10solution.py <inputfile>")
        raise SystemExit(2)

    filename = sys.argv[1]

    machines = []
    machines2 = []

    with open(filename, "r", newline="") as f:
        for row in f:
            row = row.strip()
            if not row:
                continue

            pieces = list(row.split())

            # state as BITMASK INT (exactly like original)
            state = make_number(
                i for (i, c) in enumerate(pieces[0].strip("[]"))
                if c == '#'
            )

            # joltage targets
            joltage = tuple(map(int, pieces[-1].strip("{}").split(",")))

            # buttons as index lists
            combos2 = [
                list(map(int, combo.strip("()").split(",")))
                for combo in pieces[1:-1]
            ]

            # IMPORTANT:
            # combos (for solve / lights) must be BITMASK INTS
            combos = [make_number(combo) for combo in combos2]

            # combos3 (for matrix_solve / joltage) must be TUPLE COUNTS
            combos3 = [make_tuple(combo) for combo in combos2]

            # store EXACTLY like the original main()
            machines.append((state, combos))
            machines2.append((joltage, combos3))

    # EXACTLY like original main() (do NOT call solve(machines))
    with ThreadPoolExecutor() as executor:
        total = sum(executor.map(solve, enumerate(machines)))
        print(total)

        total2 = sum(map(matrix_solve, enumerate(machines2)))
        print(total2)


if __name__ == "__main__":
    main()
