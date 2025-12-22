def max_joltage(bank: str, k: int = 12) -> int:
    """
    Pick exactly k digits from bank (in order; cannot rearrange) to form the
    largest possible k-digit joltage number.
    """
    s = bank.strip()
    if len(s) < k:
        raise ValueError(f"Bank has only {len(s)} digits, need {k}")

    # Greedy: build the answer digit-by-digit.
    # At each step, pick the largest digit you can while still leaving
    # enough digits to complete length k.
    out = []
    start = 0
    n = len(s)

    for pos in range(k):
        remaining_to_pick = k - pos
        # last index (inclusive) we can choose from for this position
        # while still leaving enough digits after it
        end = n - remaining_to_pick

        best_digit = -1
        best_idx = start

        for i in range(start, end + 1):
            d = ord(s[i]) - 48
            if d > best_digit:
                best_digit = d
                best_idx = i
                if best_digit == 9:  # can't beat 9
                    break

        out.append(chr(best_digit + 48))
        start = best_idx + 1

    return int("".join(out))

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