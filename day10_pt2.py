import re
import heapq
import sympy as sp


def min_presses_joltage_fast(target, buttons, *, progress=False):
    m = len(target)
    k = len(buttons)

    max_aff = max((len(b) for b in buttons), default=0)
    if max_aff == 0:
        return 0 if all(t == 0 for t in target) else None

    # Build A (m x k) with 0/1 entries
    A = sp.Matrix([[1 if i in buttons[j] else 0 for j in range(k)] for i in range(m)])
    b = sp.Matrix(target)

    # RREF of augmented matrix [A | b]
    M = A.row_join(b)
    rref, pivots = M.rref()

    # inconsistency check
    for r in range(m):
        if all(rref[r, c] == 0 for c in range(k)) and rref[r, k] != 0:
            return None

    pivots = list(pivots)
    free_cols = [c for c in range(k) if c not in pivots]

    # Unique solution
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

    # symbols for free variables
    free_syms = sp.symbols(" ".join(f"t{c}" for c in free_cols), integer=True)
    if len(free_cols) == 1:
        free_syms = (free_syms,)

    # Build expressions
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

    # Convert to affine rational form
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

    # Objective affine form
    obj_const = sum(affine_const)
    obj_coeff = [sum(affine_coeffs[j][i] for j in range(k)) for i in range(len(free_cols))]

    # -------- Plateau shortcut: only ONE free var affects objective --------
    nonzero = [i for i, c in enumerate(obj_coeff) if c != 0]
    L = sum(target)

    print(f"  free_cols={free_cols}, obj_coeff={obj_coeff}, L={L}")

    def eval_x(vals):
        # vals is a tuple of ints (len = len(free_cols))
        x = [0] * k
        for j in range(k):
            v = affine_const[j]
            for i in range(len(free_cols)):
                v += affine_coeffs[j][i] * vals[i]
            if v.denominator != 1 or v < 0:
                return None
            x[j] = int(v)
        return x

    def zigzag(limit):
        # yields 0, 1, -1, 2, -2, ... up to abs(v) <= limit
        yield 0
        for d in range(1, limit + 1):
            yield d
            yield -d

    if len(free_cols) >= 2 and len(nonzero) == 1:
        main = nonzero[0]
        c_main = obj_coeff[main]

        # iterate main var in objective order
        # if c_main > 0, smaller main gives smaller objective; if < 0, larger main is smaller
        main_vals = range(-L, L + 1) if c_main > 0 else range(L, -L - 1, -1)
        plateau_checks = 0
        # For each main, try to quickly find any (other vars) that makes all x >= 0 integers.
        for mv in main_vals:
            base = [0] * len(free_cols)
            base[main] = mv

            for v1 in zigzag(L):
                plateau_checks += 1
                if progress and plateau_checks % 200_000 == 0:
                    print(f"  plateau checks={plateau_checks:,}, main={mv}, v1={v1}")
            # Search other free vars near 0 first (huge win vs scanning the whole square)
            others = [i for i in range(len(free_cols)) if i != main]

            if len(others) == 1:
                # 1D: just try zigzag
                for v1 in zigzag(L):
                    vals = base[:]
                    vals[others[0]] = v1
                    x = eval_x(tuple(vals))
                    if x is not None and A * sp.Matrix(x) == b:
                        return sum(x)

            elif len(others) == 2:
                i1, i2 = others

                # For fixed (mv, v1), compute allowed interval for v2 from v >= 0 constraints
                # then try a few integer candidates in that interval near 0.
                for v1 in zigzag(L):
                    lo = sp.Rational(-10**30)
                    hi = sp.Rational(10**30)

                    for j in range(k):
                        # v = c + a_main*mv + a1*v1 + a2*v2
                        c = affine_const[j]
                        c += affine_coeffs[j][main] * mv
                        c += affine_coeffs[j][i1] * v1
                        a2 = affine_coeffs[j][i2]

                        # constraint: c + a2*v2 >= 0
                        if a2 == 0:
                            if c < 0:
                                lo, hi = sp.Rational(1), sp.Rational(0)  # empty
                                break
                            continue

                        bound = (-c) / a2
                        if a2 > 0:
                            # v2 >= bound
                            if bound > lo:
                                lo = bound
                        else:
                            # v2 <= bound
                            if bound < hi:
                                hi = bound

                    if lo > hi:
                        continue

                    # integer v2 must be within [-L, L] too
                    lo_i = max(-L, int(sp.ceiling(lo)))
                    hi_i = min(L, int(sp.floor(hi)))
                    if lo_i > hi_i:
                        continue

                    # try v2 values near 0 first within [lo_i, hi_i]
                    # (this is usually enough to find a solution quickly)
                    candidates = []
                    if lo_i <= 0 <= hi_i:
                        candidates.append(0)
                    for d in range(1, 50):  # small local search; increase if needed
                        if 0 - d >= lo_i:
                            candidates.append(-d)
                        if 0 + d <= hi_i:
                            candidates.append(d)

                    # if interval doesn't include 0, try edges and a few points
                    if not candidates:
                        candidates = [lo_i, hi_i]
                        mid = (lo_i + hi_i) // 2
                        candidates += [mid, mid - 1, mid + 1]

                    for v2 in candidates:
                        vals = base[:]
                        vals[i1] = v1
                        vals[i2] = v2
                        x = eval_x(tuple(vals))
                        if x is not None and A * sp.Matrix(x) == b:
                            return sum(x)

        # no solution found in window
        return None

    # -------- Default: Best-first search (heapq) --------
    def priority(vals):
        primary = obj_const + sum(obj_coeff[i] * vals[i] for i in range(len(vals)))
        size = sum(abs(v) for v in vals)
    
        # NEW: include a tiny size penalty in the primary key
        # Use Rational so ordering stays stable; 1/100000 is small enough not to change the true optimum ordering.
        primary2 = primary + sp.Rational(size, 100000)
    
        return (
            int(primary2) if primary2.denominator == 1 else float(primary2),
            size
        )

    start = tuple(0 for _ in range(len(free_cols)))
    seen = {start}
    pq = [(priority(start), start)]
    expansions = 0

    while pq:
        _, vals = heapq.heappop(pq)
        expansions += 1
        if progress and expansions % 200000 == 0:
            print(f"  expanded {expansions:,} states, vals={vals}")

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



def fewest_total_joltage_presses_fast(filename, *, progress=False):
    total = 0
    machine_num = 1

    with open(filename, "r", newline="") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip():
                continue

            # buttons: all (...) blocks
            parens = re.findall(r"\(([^)]*)\)", line)
            buttons = []
            for p in parens:
                p = p.strip()
                if p:
                    buttons.append([int(x.strip()) for x in p.split(",") if x.strip()])

            # target: {...}
            m = re.search(r"\{([^}]*)\}", line)
            target = tuple(int(x.strip()) for x in m.group(1).split(",") if x.strip())

            print(f"[machine {machine_num}] counters={len(target)} buttons={len(buttons)} max_target={max(target)}")
            presses = min_presses_joltage_fast(target, buttons, progress=progress)
            print(f"  DEBUG presses returned: {presses!r}")
            if presses is None:
                raise ValueError(f"Machine {machine_num} is impossible.")
            print(f"[machine {machine_num}] min presses = {presses}\n")

            total += presses
            machine_num += 1

    print(f"TOTAL = {total}")
    return total


# run:
print(fewest_total_joltage_presses_fast("day10input.txt", progress=True))
