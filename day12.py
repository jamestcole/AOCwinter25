from collections import deque

# -----------------------------
# Shape parsing + orientations
# -----------------------------

def parse_input(filename):
    with open(filename, "r") as f:
        lines = [ln.rstrip("\n") for ln in f]

    shapes = {}
    regions = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Shape header like "0:"
        if ":" in line and "x" not in line:
            idx = int(line[:-1])
            i += 1
            grid = []
            while i < len(lines):
                if not lines[i].strip():
                    break
                if "x" in lines[i]:
                    break
                grid.append(lines[i].strip())
                i += 1
            shapes[idx] = grid
            continue

        # Region section starts
        if "x" in line and ":" in line:
            break

        i += 1

    # Regions
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        left, right = line.split(":")
        w_str, h_str = left.strip().split("x")
        W, H = int(w_str), int(h_str)
        counts = [int(x) for x in right.strip().split()]
        regions.append((W, H, counts))

    print(f"Parsed {len(shapes)} shapes, {len(regions)} regions")
    return shapes, regions


def cells_from_grid(grid):
    return [(x, y) for y, row in enumerate(grid) for x, c in enumerate(row) if c == "#"]


def normalize(cells):
    minx = min(x for x, y in cells)
    miny = min(y for x, y in cells)
    return tuple(sorted((x - minx, y - miny) for x, y in cells))


def rotate90(cells):
    return [(y, -x) for x, y in cells]


def flip_x(cells):
    return [(-x, y) for x, y in cells]


def unique_orientations(cells):
    seen = set()
    out = []
    cur = cells
    for _ in range(4):
        for v in (cur, flip_x(cur)):
            n = normalize(v)
            if n not in seen:
                seen.add(n)
                out.append(n)
        cur = rotate90(cur)
    return out


# -----------------------------
# Region tiling solver
# -----------------------------

def bit_index(x, y, W):
    return y * W + x


def placements_for_shape(orient, W, H):
    maxx = max(x for x, y in orient)
    maxy = max(y for x, y in orient)
    out = []
    for oy in range(H - maxy):
        for ox in range(W - maxx):
            mask = 0
            for x, y in orient:
                mask |= 1 << bit_index(ox + x, oy + y, W)
            out.append(mask)
    return out


def can_tile_region(W, H, piece_defs, *, progress=False):
    N = W * H
    full_mask = (1 << N) - 1
    used = [False] * len(piece_defs)
    piece_places = [pls for _, pls in piece_defs]

    calls = 0

    def dfs(occ):
        nonlocal calls
        calls += 1

        if progress and calls % 100_000 == 0:
            filled = bin(occ).count("1")
            print(f"    DFS calls={calls:,}, filled={filled}/{N}")

        if occ == full_mask:
            return True

        empty = (~occ) & full_mask
        cell = (empty & -empty).bit_length() - 1

        for pi in range(len(piece_defs)):
            if used[pi]:
                continue
            for pm in piece_places[pi]:
                if (pm >> cell) & 1 and (pm & occ) == 0:
                    used[pi] = True
                    if dfs(occ | pm):
                        return True
                    used[pi] = False
        return False

    ok = dfs(0)
    if progress:
        print(f"    DFS finished after {calls:,} calls → {'OK' if ok else 'FAIL'}")
    return ok


def region_satisfiable(W, H, counts, shape_orients, *, progress=False):
    piece_defs = []

    for idx, c in enumerate(counts):
        if c <= 0:
            continue
        if idx not in shape_orients:
            return False

        all_places = []
        for orient in shape_orients[idx]:
            all_places.extend(placements_for_shape(orient, W, H))
        all_places = sorted(set(all_places))
        if not all_places:
            return False

        for _ in range(c):
            piece_defs.append((idx, all_places))

    total_cells = sum(bin(p[1][0]).count("1") for p in piece_defs)
    if total_cells > W * H:
        if progress:
            print("    ❌ Area exceeds region")
        return False

    piece_defs.sort(key=lambda t: len(t[1]))
    return can_tile_region(W, H, piece_defs, progress=progress)


# -----------------------------
# Main
# -----------------------------

def count_regions_that_fit_fast(filename):
    shapes, regions = parse_input(filename)

    # Optional safety: verify all shapes are 3x3 (like the example)
    for idx, grid in shapes.items():
        h = len(grid)
        w = len(grid[0]) if h else 0
        if any(len(r) != w for r in grid):
            raise ValueError(f"Shape {idx} has ragged rows")
        if (w, h) != (3, 3):
            raise ValueError(
                f"Shape {idx} is {w}x{h}, not 3x3. "
                "Tell me your max shape size and I'll generalize the slot check."
            )

    ok = 0
    for i, (W, H, counts) in enumerate(regions, 1):
        total_presents = sum(counts)
        slots = (W // 3) * (H // 3)
        fits = total_presents <= slots

        if i <= 5 or i % 50 == 0:
            print(f"Region {i}: {W}x{H} presents={total_presents} slots={slots} -> {'OK' if fits else 'NO'}")

        if fits:
            ok += 1

    print(f"\nTOTAL FITTING REGIONS = {ok}")
    return ok


# ---- run ----
if __name__ == "__main__":
    count_regions_that_fit_fast("day12.txt")
