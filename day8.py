from collections import Counter

class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        return True


def multiply_top3_after_k_connections(filename, k=1000):
    # 1) read points
    pts = []
    with open(filename, "r", newline="") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 3:
                raise ValueError(f"Bad line (expected X,Y,Z): {line!r}")
            x, y, z = map(int, parts)  # handles spaces too
            pts.append((x, y, z))

    n = len(pts)
    if n < 3:
        raise ValueError(f"Parsed only {n} points from {filename}. Need at least 3.")

    dsu = DSU(n)

    # 2) all pair distances (squared)
    edges = []
    for i in range(n):
        xi, yi, zi = pts[i]
        for j in range(i + 1, n):
            xj, yj, zj = pts[j]
            dx = xi - xj
            dy = yi - yj
            dz = zi - zj
            dist2 = dx*dx + dy*dy + dz*dz
            edges.append((dist2, i, j))

    edges.sort(key=lambda t: t[0])

    # 3) attempt first k connections (or all edges if fewer exist)
    for _, i, j in edges[:min(k, len(edges))]:
        dsu.union(i, j)

    # 4) component sizes
    roots = [dsu.find(i) for i in range(n)]
    counts = Counter(roots)
    sizes = sorted(counts.values(), reverse=True)

    print("Parsed points:", n)
    print("Number of circuits:", len(sizes))
    print("Top 10 circuit sizes:", sizes[:10])

    if len(sizes) < 3:
        raise ValueError(f"Only {len(sizes)} circuits exist; cannot multiply top 3.")

    return sizes[0] * sizes[1] * sizes[2]


# example usage:
print(multiply_top3_after_k_connections("day8input.txt", k=1000))
