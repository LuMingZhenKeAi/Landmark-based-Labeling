from py2neo import Graph
from collections import deque
import time


def find_shortest_path(graph, start_id, end_id):
    visited = set()
    queue = deque([(start_id, [])])
    path_length = set()
    path_queue = deque([(0, [])])
    result_list = []
    min_length = float('inf')

    while queue:
        node_id, path = queue.popleft()
        if node_id == end_id:
            # 找到了一条路径
            path_length.add(len(path + [end_id]))
            path_queue.append((len(path + [end_id]), path + [end_id]))

        if len(path) + 1 > min_length:
            continue

        if node_id in visited:
            continue

        visited.add(node_id)
        cypher_query = f"MATCH (n)-[]->(m) WHERE ID(n) = {node_id} RETURN ID(m)"
        result = graph.run(cypher_query)
        for record in result:
            next_node_id = record["ID(m)"]
            queue.append((next_node_id, path + [node_id]))

    if path_length:
        min_length = min(path_length)
        for rela in path_queue:
            if rela[0] == min_length:
                result_list.append(rela[1])
        return result_list

    return None



# 连接到Neo4j数据库
graph = Graph("http://localhost:7474", auth=("neo4j", "QAZqaz1238546"))

# 设置起始节点和目标节点的ID
start_id = 9
end_id = 6094

# 计时开始
start_time = time.time()

# 查找最短路径
shortest_paths = find_shortest_path(graph, start_id, end_id)

# 计时结束
end_time = time.time()

if shortest_paths:
    print("Shortest path found:")
    for shortest_path in shortest_paths:
        shortest_path = [str(i) for i in shortest_path]
        print(" -> ".join(shortest_path))
    print("Path length:", len(shortest_path) - 1)
else:
    print("No path found.")

# 计算总时间
elapsed_time = end_time - start_time

print("总共计算时间:", elapsed_time, "秒")
