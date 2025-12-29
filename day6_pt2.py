import re
from math import prod

def split_into_blocks(lines):
    lines = [line.rstrip("\n").rstrip("\r") for line in lines]  # keep leading spaces
    width = max(len(s) for s in lines)
    grid = [s.ljust(width) for s in lines]
    rows = len(grid)

    sep = [all(grid[r][c] == " " for r in range(rows)) for c in range(width)]

    blocks = []
    c = 0
    while c < width:
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


def worksheet_total_rtl_columns(filename):
    with open(filename, "r", newline="") as f:
        lines = [line.rstrip("\n").rstrip("\r") for line in f]

    while lines and lines[-1] == "":
        lines.pop()
    if not lines:
        return 0

    grid, blocks = split_into_blocks(lines)

    op_row = grid[-1]
    digit_rows = grid[:-1]   # rows containing digits/spaces

    total = 0
    for start, end in blocks:
        # operator for this problem
        m = re.search(r"[+*]", op_row[start:end])
        if not m:
            continue
        op = m.group(0)

        # In part 2: numbers are COLUMNS inside the block, read right-to-left.
        nums = []
        for c in range(end - 1, start - 1, -1):
            digits = []
            for r in range(len(digit_rows)):
                ch = digit_rows[r][c]
                if ch.isdigit():
                    digits.append(ch)
            if digits:  # this column contributes a number
                nums.append(int("".join(digits)))

        total += sum(nums) if op == "+" else prod(nums)

    return total


# example usage:
print(worksheet_total_rtl_columns("day6input.txt"))
