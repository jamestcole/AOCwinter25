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


def accessible_rolls(filename, threshold=4):
    # Read entire grid first
    with open(filename, "r") as f:
        grid = [line.rstrip("\n") for line in f if line.strip()]

    total = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == '@' and count_adjacent_rolls(grid, r, c) < threshold:
                total += 1

    return total

print(accessible_rolls("day4input.txt"))