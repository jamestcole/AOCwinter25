from bisect import bisect_right

def read_database(filename):
    with open(filename, "r") as f:
        lines = [line.strip() for line in f]

    i = 0
    ranges = []
    while i < len(lines) and lines[i] != "":
        a, b = map(int, lines[i].split("-"))
        ranges.append((a, b))
        i += 1

    # skip blank line(s)
    while i < len(lines) and lines[i] == "":
        i += 1

    ids = [int(x) for x in lines[i:] if x != ""]
    return ranges, ids


def merge_ranges(ranges):
    if not ranges:
        return []
    ranges.sort()
    merged = [list(ranges[0])]
    for a, b in ranges[1:]:
        last_a, last_b = merged[-1]
        if a <= last_b + 1:          # overlap OR directly adjacent
            merged[-1][1] = max(last_b, b)
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged]


def is_fresh(merged_ranges, x):
    # Find rightmost range with start <= x
    starts = [a for a, _ in merged_ranges]
    idx = bisect_right(starts, x) - 1
    if idx < 0:
        return False
    a, b = merged_ranges[idx]
    return a <= x <= b


def count_fresh_ids(filename):
    ranges, ids = read_database(filename)
    merged = merge_ranges(ranges)
    return sum(1 for x in ids if is_fresh(merged, x))


# example usage:
print(count_fresh_ids("day5input.txt"))
