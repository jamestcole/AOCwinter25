from collections import deque

def read_red_tiles(filename):
    reds = []
    with open(filename, "r", newline="") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            x, y = map(int, line.split(","))
            reds.append((x, y))
    return reds


def max_rectangle_area_red_green_fast(filename):
    reds = read_red_tiles(filename)
    n = len(reds)
    if n < 2:
        return 0

    # --- Build orthogonal segments from the cyclic list ---
    segs = []
    xs = set()
    ys = set()

    for i in range(n):
        x1, y1 = reds[i]
        x2, y2 = reds[(i + 1) % n]
        if x1 != x2 and y1 != y2:
            raise ValueError("Adjacent red tiles must share x or y")

        # We work in continuous coords where a tile at integer (x,y) is the unit square:
        # [x, x+1) x [y, y+1). So rectangle over tiles [xlo..xhi] becomes [xlo, xhi+1).
        # Add both coordinate and coordinate+1 to represent tile boundaries.
        xs.add(x1); xs.add(x1 + 1); xs.add(x2); xs.add(x2 + 1)
        ys.add(y1); ys.add(y1 + 1); ys.add(y2); ys.add(y2 + 1)

        segs.append((x1, y1, x2, y2))

    # Add padding so "outside" definitely exists
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    xs.add(minx - 1); xs.add(maxx + 1)
    ys.add(miny - 1); ys.add(maxy + 1)

    xs = sorted(xs)
    ys = sorted(ys)

    x_to_i = {x: i for i, x in enumerate(xs)}
    y_to_j = {y: j for j, y in enumerate(ys)}

    # Cell grid is between coordinate lines:
    # cell (i,j) covers [xs[i], xs[i+1]) x [ys[j], ys[j+1])
    W = len(xs) - 1
    H = len(ys) - 1

    # Walls: block movement between neighboring cells across polygon boundary
    # vertical_walls[i][j] = wall between cell (i-1,j) and (i,j) along x=xs[i]
    vertical_walls = [[False] * H for _ in range(W + 1)]
    # horizontal_walls[i][j] = wall between cell (i,j-1) and (i,j) along y=ys[j]
    horizontal_walls = [[False] * (H + 1) for _ in range(W)]

    def add_vertical_wall(x, ylo, yhi):
        # wall along x constant, for y in [ylo, yhi)
        xi = x_to_i[x]
        j0 = y_to_j[ylo]
        j1 = y_to_j[yhi]
        for j in range(min(j0, j1), max(j0, j1)):
            vertical_walls[xi][j] = True

    def add_horizontal_wall(y, xlo, xhi):
        yi = y_to_j[y]
        i0 = x_to_i[xlo]
        i1 = x_to_i[xhi]
        for i in range(min(i0, i1), max(i0, i1)):
            horizontal_walls[i][yi] = True

    # Build boundary walls from segments (in continuous coords along tile edges)
    for x1, y1, x2, y2 in segs:
        if x1 == x2:
            # vertical segment goes along the shared tile edge x = x1 or x1+1 depending on direction.
            # For unit tile model, connecting tile centers by green tiles means filling tile squares;
            # the loop boundary in continuous space lies on integer grid lines.
            # We can use x = x1 (left edge) OR x1+1 (right edge) consistently by using x1.
            x = x1
            ylo = min(y1, y2)
            yhi = max(y1, y2) + 1
            add_vertical_wall(x, ylo, yhi)
        else:
            y = y1
            xlo = min(x1, x2)
            xhi = max(x1, x2) + 1
            add_horizontal_wall(y, xlo, xhi)

    # --- Flood fill outside on the compressed cell grid ---
    outside = [[False] * W for _ in range(H)]
    q = deque()

    # start from all border cells
    for i in range(W):
        q.append((0, i))
        q.append((H - 1, i))
    for j in range(H):
        q.append((j, 0))
        q.append((j, W - 1))

    def can_move(j, i, nj, ni):
        # move between adjacent cells, check if a wall blocks it
        if not (0 <= ni < W and 0 <= nj < H):
            return False
        if abs(ni - i) + abs(nj - j) != 1:
            return False

        if ni == i + 1:   # right
            return not vertical_walls[i + 1][j]
        if ni == i - 1:   # left
            return not vertical_walls[i][j]
        if nj == j + 1:   # down
            return not horizontal_walls[i][j + 1]
        if nj == j - 1:   # up
            return not horizontal_walls[i][j]
        return False

    while q:
        j, i = q.popleft()
        if not (0 <= i < W and 0 <= j < H):
            continue
        if outside[j][i]:
            continue
        outside[j][i] = True
        for dj, di in ((1,0), (-1,0), (0,1), (0,-1)):
            nj, ni = j + dj, i + di
            if 0 <= ni < W and 0 <= nj < H and not outside[nj][ni] and can_move(j, i, nj, ni):
                q.append((nj, ni))

    # allowed cells are those NOT outside (inside region). Boundary is included automatically by walls.
    # Build weighted allowed-area grid for prefix sums.
    allowed_weight = [[0] * W for _ in range(H)]
    for j in range(H):
        dy = ys[j + 1] - ys[j]
        for i in range(W):
            dx = xs[i + 1] - xs[i]
            if not outside[j][i]:
                allowed_weight[j][i] = dx * dy

    # 2D prefix sum over allowed_weight
    ps = [[0] * (W + 1) for _ in range(H + 1)]
    for j in range(H):
        row_sum = 0
        for i in range(W):
            row_sum += allowed_weight[j][i]
            ps[j + 1][i + 1] = ps[j][i + 1] + row_sum

    def rect_allowed_area(xlo, xhi_inclusive, ylo, yhi_inclusive):
        # rectangle of tiles inclusive -> continuous box [xlo, xhi+1) x [ylo, yhi+1)
        ax0 = xlo
        ax1 = xhi_inclusive + 1
        ay0 = ylo
        ay1 = yhi_inclusive + 1

        # find indices in xs/ys (they should exist because we included coord and coord+1)
        i0 = x_to_i[ax0]
        i1 = x_to_i[ax1]
        j0 = y_to_j[ay0]
        j1 = y_to_j[ay1]

        return ps[j1][i1] - ps[j0][i1] - ps[j1][i0] + ps[j0][i0]

    # --- Try all pairs of red corners ---
    best = 0
    for a in range(n):
        x1, y1 = reds[a]
        for b in range(a + 1, n):
            x2, y2 = reds[b]
            xlo, xhi = (x1, x2) if x1 <= x2 else (x2, x1)
            ylo, yhi = (y1, y2) if y1 <= y2 else (y2, y1)

            area = (xhi - xlo + 1) * (yhi - ylo + 1)
            if area <= best:
                continue

            # O(1) check: rectangle is valid iff allowed area equals rectangle area
            if rect_allowed_area(xlo, xhi, ylo, yhi) == area:
                best = area

    return best


# usage:
# print(max_rectangle_area_red_green_fast("day9input.txt"))

# example usage:
print(max_rectangle_area_red_green_fast("day9input.txt"))