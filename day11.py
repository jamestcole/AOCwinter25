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

def all_paths_you_to_out(graph, start="you", end="out"):
    paths = []
    path = [start]
    visiting = {start}

    def dfs(u):
        if u == end:
            paths.append(path.copy())
            return
        for v in graph.get(u, []):
            if v in visiting:
                continue
            visiting.add(v)
            path.append(v)
            dfs(v)
            path.pop()
            visiting.remove(v)

    dfs(start)
    return paths


# ---- run on file ----
filename = "day11.txt"   # change to your .txt filename
graph = parse_graph_from_file(filename)

paths = all_paths_you_to_out(graph)

for p in paths:
    print(" -> ".join(p))

print("total paths:", len(paths))
