def max_joltage(bank: str) -> int:
    bank = bank.strip()
    best_right = -1
    best_val = -1

    for ch in reversed(bank):
        d = ord(ch) - 48  # faster int(ch)
        if best_right != -1:
            candidate = 10 * d + best_right
            if candidate > best_val:
                best_val = candidate
        if d > best_right:
            best_right = d

    return best_val  # assumes bank has at least 2 digits


def total_max_joltage(filename: str) -> int:
    total = 0
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += max_joltage(line)
    return total


# example usage
print(total_max_joltage("day3input.txt"))
