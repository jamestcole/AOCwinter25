def read_grid(filename):
    with open(filename, "r", newline="") as f:
        return [line.rstrip("\n").rstrip("\r") for line in f if line.rstrip("\n").rstrip("\r") != ""]


def count_splits(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    # find S
    s_row = s_col = None
    for r in range(rows):
        c = grid[r].find("S")
        if c != -1:
            s_row, s_col = r, c
            break
    if s_row is None:
        raise ValueError("No 'S' found in grid")

    active = {s_col}      # active beam columns (at the current row)
    splits = 0

    # beam starts just below S and moves downward
    for r in range(s_row + 1, rows):
        if not active:
            break

        next_active = set()
        row = grid[r]

        for c in active:
            if 0 <= c < cols:
                if row[c] == "^":
                    splits += 1
                    if c - 1 >= 0:
                        next_active.add(c - 1)
                    if c + 1 < cols:
                        next_active.add(c + 1)
                else:
                    next_active.add(c)

        active = next_active

    return splits

grid = read_grid("day7input.txt")
print(count_splits(grid))
