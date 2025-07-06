from collections import defaultdict, deque

def Toposort(graph_dict):
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    # Collect all nodes
    for node, parents in graph_dict.items():
        in_degree[node] = 0  # Ensure all nodes are included

    # Build graph and in-degree map
    for node, parents in graph_dict.items():
        for parent in parents:
            if parent:
                graph[parent].append(node)
                in_degree[node] += 1

    queue = deque([name for name, deg in in_degree.items() if deg == 0])
    sorted_nodes = []

    while queue:
        current = queue.popleft()
        sorted_nodes.append(current)
        for child in graph[current]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(sorted_nodes) != len(in_degree):
        raise ValueError("Cycle detected in dependencies!")

    return sorted_nodes

def BuildReverseGraph(graph_dict):
    reverse_graph = defaultdict(list)

    for node, parents in graph_dict.items():
        for parent in parents:
            if parent:
                reverse_graph[parent].append(node)

    return reverse_graph

def GetAllDescendants(start, reverse_graph):
    descendants = set()
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for child in reverse_graph.get(current, []):
            if child not in descendants:
                descendants.add(child)
                queue.append(child)

    return descendants