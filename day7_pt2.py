def read_grid(filename):
    with open(filename, "r", newline="") as f:
        return [line.rstrip("\n").rstrip("\r") for line in f if line.strip() != ""]


def count_timelines(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0

    # find S
    s_row = s_col = None
    for r in range(rows):
        c = grid[r].find("S")
        if c != -1:
            s_row, s_col = r, c
            break
    if s_row is None:
        raise ValueError("No 'S' found in grid")

    # particle starts moving downward from just below S
    ways = {s_col: 1}
    exited = 0

    for r in range(s_row + 1, rows):
        if not ways:
            break

        next_ways = {}
        row = grid[r]

        for c, w in ways.items():
            if c < 0 or c >= cols:
                exited += w
                continue

            if row[c] == "^":
                # split: go down-left and down-right
                for nc in (c - 1, c + 1):
                    if 0 <= nc < cols:
                        next_ways[nc] = next_ways.get(nc, 0) + w
                    else:
                        exited += w
            else:
                # continue straight down
                next_ways[c] = next_ways.get(c, 0) + w

        ways = next_ways

    # any timelines still in-grid after the last row exit out the bottom
    exited += sum(ways.values())
    return exited

grid = read_grid("day7input.txt")
print(count_timelines(grid))
