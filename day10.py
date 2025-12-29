import re
from collections import deque

def min_presses_for_machine(diagram_str, button_lists):
    """
    diagram_str: like ".##." (no brackets)
    button_lists: list of lists of indices, e.g. [[3], [1,3], [2], ...]
    """
    n = len(diagram_str)

    # target bitmask: bit i = 1 if diagram[i] == '#'
    target = 0
    for i, ch in enumerate(diagram_str):
        if ch == '#':
            target |= (1 << i)

    # precompute each button as a bitmask
    btn_masks = []
    for idxs in button_lists:
        m = 0
        for i in idxs:
            m ^= (1 << i)
        btn_masks.append(m)

    # BFS from 0 to target
    start = 0
    if start == target:
        return 0

    dist = {start: 0}
    q = deque([start])

    while q:
        state = q.popleft()
        d = dist[state]
        for bm in btn_masks:
            ns = state ^ bm
            if ns not in dist:
                dist[ns] = d + 1
                if ns == target:
                    return d + 1
                q.append(ns)

    # If unreachable (shouldn't happen unless buttons can't span target)
    return None


def fewest_total_presses(filename):
    total = 0

    with open(filename, "r", newline="") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip():
                continue

            # diagram in [ ... ]
            m = re.search(r"\[([.#]+)\]", line)
            if not m:
                raise ValueError(f"Missing diagram in line: {line!r}")
            diagram = m.group(1)

            # all button schematics in ( ... )
            parens = re.findall(r"\(([^)]*)\)", line)

            # ignore the { ... } block by keeping only the (...) that look like index lists
            buttons = []
            for p in parens:
                p = p.strip()
                if not p:
                    continue
                # parse comma-separated ints
                idxs = [int(x.strip()) for x in p.split(",") if x.strip() != ""]
                buttons.append(idxs)

            presses = min_presses_for_machine(diagram, buttons)
            if presses is None:
                raise ValueError(f"Machine is unreachable: {line!r}")
            total += presses

    return total


# Example usage:
print(fewest_total_presses("day10input.txt"))
