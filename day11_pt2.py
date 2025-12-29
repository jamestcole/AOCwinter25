from collections import deque

def parse_graph_from_file(filename):
    graph = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            left, right = line.split(":")
            node = left.strip()
            outs = right.strip().split() if right.strip() else []
            graph[node] = outs
    return graph

def count_paths_svr_to_out_visiting_dac_fft_dp(
    graph, start="svr", end="out", must=("dac", "fft"), *, progress=True
):
    """
    DP counting for a DAG.
    Counts paths from start->end that visit all nodes in `must` (here dac & fft).
    Fast because it does NOT enumerate individual paths.

    NOTE: This assumes the reachable subgraph from `start` is acyclic.
    """
    must = set(must)

    # --- restrict to nodes reachable from start (so topo + DP stays small) ---
    reachable = set()
    q = deque([start])
    reachable.add(start)
    while q:
        u = q.popleft()
        for v in graph.get(u, []):
            if v not in reachable:
                reachable.add(v)
                q.append(v)

    # Build induced adjacency + indegree for topo sort
    adj = {u: [v for v in graph.get(u, []) if v in reachable] for u in reachable}
    indeg = {u: 0 for u in reachable}
    for u in reachable:
        for v in adj[u]:
            indeg[v] += 1

    # Kahn topo
    topo = []
    dq = deque([u for u in reachable if indeg[u] == 0])
    while dq:
        u = dq.popleft()
        topo.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                dq.append(v)

    if len(topo) != len(reachable):
        raise ValueError(
            "Cycle detected in the reachable graph from start; "
            "this DP method requires a DAG (or you'd need SCC handling)."
        )

    # Map must-set to 2-bit mask: bit0=dac, bit1=fft (generalized to exactly these two)
    # If you ever change must, extend this mapping.
    req0, req1 = tuple(must)
    def add_mask(node, mask):
        if node == req0:
            mask |= 1
        if node == req1:
            mask |= 2
        return mask

    start_mask = 0
    start_mask = add_mask(start, start_mask)

    # dp[node][mask] = number of ways to reach `node` with given visited-mask
    dp = {u: [0, 0, 0, 0] for u in reachable}
    dp[start][start_mask] = 1

    # Process in topo order
    processed = 0
    for u in topo:
        processed += 1
        if progress and processed % 100 == 0:
            current_total = sum(dp[end]) if end in dp else 0
            print(f"processed {processed}/{len(topo)} nodes, current_end_total={current_total}")

        for mask in range(4):
            ways = dp[u][mask]
            if ways == 0:
                continue
            for v in adj[u]:
                nm = add_mask(v, mask)
                dp[v][nm] += ways

    # Need to have visited both => mask == 3
    return dp[end][3] if end in dp else 0


# ---- run on file ----
filename = "day11.txt"
graph = parse_graph_from_file(filename)
print(count_paths_svr_to_out_visiting_dac_fft_dp(graph, progress=True))
