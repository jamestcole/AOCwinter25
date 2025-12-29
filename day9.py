def max_rectangle_area_from_file(filename):
    pts = []
    with open(filename, "r", newline="") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            x, y = map(int, line.split(","))
            pts.append((x, y))

    n = len(pts)
    best = 0

    for i in range(n):
        x1, y1 = pts[i]
        for j in range(i + 1, n):
            x2, y2 = pts[j]
            area = (abs(x1 - x2) + 1) * (abs(y1 - y2) + 1)
            if area > best:
                best = area

    return best


# example usage:
print(max_rectangle_area_from_file("day9input.txt"))
