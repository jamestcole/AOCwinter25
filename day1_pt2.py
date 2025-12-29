def count_zero_hits_during_rotation(p, direction, dist, mod=100):
    dist = int(dist)
    p %= mod

    if direction == "R":
        r = (-p) % mod
    else:  # "L"
        r = p % mod

    # r==0 means you'd hit 0 after 100 clicks (not after 0 clicks)
    if r == 0:
        r = mod

    if dist < r:
        return 0
    return 1 + (dist - r) // mod


def password_method_0x434C49434B(filename):
    p = 50
    hits = 0

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            direction = line[0]
            dist = int(line[1:])

            hits += count_zero_hits_during_rotation(p, direction, dist, mod=100)

            # update final position after full rotation
            if direction == "R":
                p = (p + dist) % 100
            else:
                p = (p - dist) % 100

    return hits


print(password_method_0x434C49434B("day1input.txt"))
