def count_adjacent_rolls(grid, r, c):
    rows, cols = len(grid), len(grid[0])
    cnt = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < rows and 0 <= cc < cols and grid[rr][cc] == '@':
                cnt += 1
    return cnt


def total_removable_rolls_from_file(filename, threshold=4):
    # load grid
    with open(filename, "r") as f:
        grid = [list(line.rstrip("\n")) for line in f if line.strip()]

    rows, cols = len(grid), len(grid[0])
    removed_total = 0

    while True:
        # find all currently-accessible rolls (based on current grid)
        to_remove = []
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == '@':
                    # count neighbors using the current grid
                    # (count_adjacent_rolls expects list[str], so join rows temporarily)
                    pass

        # efficient neighbor count directly on list[list[str]]
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != '@':
                    continue
                cnt = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < rows and 0 <= cc < cols and grid[rr][cc] == '@':
                            cnt += 1
                if cnt < threshold:
                    to_remove.append((r, c))

        if not to_remove:
            break

        # remove them all at once (one "turn")
        for r, c in to_remove:
            grid[r][c] = '.'

        removed_total += len(to_remove)

    return removed_total

print(total_removable_rolls_from_file("day4input.txt"))