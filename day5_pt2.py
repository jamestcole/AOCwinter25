def read_ranges_only(filename):
    ranges = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line == "":   # stop at the blank line
                break
            a, b = map(int, line.split("-"))
            ranges.append((a, b))
    return ranges


def merge_ranges(ranges):
    if not ranges:
        return []
    ranges.sort()
    merged = [list(ranges[0])]
    for a, b in ranges[1:]:
        last_a, last_b = merged[-1]
        if a <= last_b + 1:          # overlap or touch
            merged[-1][1] = max(last_b, b)
        else:
            merged.append([a, b])
    return [(a, b) for a, b in merged]


def count_total_fresh_ids(filename):
    ranges = read_ranges_only(filename)
    merged = merge_ranges(ranges)
    return sum((b - a + 1) for a, b in merged)


# example usage:
print(count_total_fresh_ids("day5input.txt"))
