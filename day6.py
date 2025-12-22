import re
from math import prod

def split_into_blocks(lines):
    # IMPORTANT: do NOT strip() here; keep leading spaces.
    lines = [line.rstrip("\n").rstrip("\r") for line in lines]

    width = max(len(s) for s in lines)
    grid = [s.ljust(width) for s in lines]
    rows = len(grid)

    # Columns that are spaces in every row are separators between problems
    sep = [all(grid[r][c] == " " for r in range(rows)) for c in range(width)]

    blocks = []
    c = 0
    while c < width:
        # skip separator columns
        while c < width and sep[c]:
            c += 1
        if c >= width:
            break

        start = c
        while c < width and not sep[c]:
            c += 1
        end = c
        blocks.append((start, end))

    return grid, blocks


def worksheet_total(filename):
    with open(filename, "r", newline="") as f:
        # keep all lines (including leading spaces)
        lines = [line.rstrip("\n").rstrip("\r") for line in f]

    # drop completely empty lines at end (optional)
    while lines and lines[-1] == "":
        lines.pop()
    if not lines:
        return 0

    grid, blocks = split_into_blocks(lines)

    op_row = grid[-1]
    num_rows = grid[:-1]

    total = 0
    for start, end in blocks:
        # operator in this block
        m = re.search(r"[+*]", op_row[start:end])
        if not m:
            continue
        op = m.group(0)

        # one number per row inside this block (alignment ignored)
        nums = []
        for row in num_rows:
            found = re.findall(r"\d+", row[start:end])
            if found:
                nums.append(int(found[0]))

        if op == "+":
            total += sum(nums)
        else:
            total += prod(nums)

    return total


# Example usage:
print(worksheet_total("day6input.txt"))
