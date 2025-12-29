class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n

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
        self.components -= 1
        return True


def last_connection_x_product(filename):
    pts = []
    with open(filename, "r", newline="") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            x, y, z = map(int, line.split(","))
            pts.append((x, y, z))

    n = len(pts)
    if n < 2:
        return 0

    # all pair edges (squared distance)
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

    dsu = DSU(n)
    last_i = last_j = None

    for _, i, j in edges:
        if dsu.union(i, j):
            last_i, last_j = i, j
            if dsu.components == 1:
                break

    x1 = pts[last_i][0]
    x2 = pts[last_j][0]
    return x1 * x2


# example:
print(last_connection_x_product("day8input.txt"))  # should be 25272 for the example
