from py2neo import Graph
from collections import deque
import time


def landmark_labeling_shortest_path(graph, source_node_id, target_node_id, landmarks):
    # 计算预处理过程时间
    start_time = time.time()

    # 计算地标节点之间的最短路径并存储
    landmark_paths = {}
    for i in range(len(landmarks)):
        landmark_i = landmarks[i]
        landmark_paths[landmark_i] = {}
        for j in range(i + 1, len(landmarks)):
            landmark_j = landmarks[j]
            landmark_paths[landmark_j] = {}
            paths = find_shortest_path(graph, landmark_i, landmark_j)
            landmark_paths[landmark_i][landmark_j] = paths
            if paths:
                reverse_paths = []
                for path in paths:
                    reverse_path = path[::-1]
                    reverse_paths.append(reverse_path)
            else:
                reverse_paths = None
            landmark_paths[landmark_j][landmark_i] = reverse_paths

    # 计算初始节点到各个地标节点的最短路径并存储
    source_paths = {}
    for landmark in landmarks:
        paths = find_shortest_path(graph, source_node_id, landmark)
        source_paths[landmark] = paths

    # 计算目标节点到各个地标节点的最短路径并存储
    target_paths = {}
    for landmark in landmarks:
        paths = find_shortest_path(graph, target_node_id, landmark)
        target_paths[landmark] = paths

    end_time = time.time()

    preprocessing_time = end_time - start_time

    print("预处理时间:", preprocessing_time, "秒")

    # 计算估计最短路径时间
    start_time = time.time()

    # 使用预处理的最短路径估计两个节点之间的最短路径
    shortest_paths = estimate_shortest_path(source_node_id, target_node_id, landmarks,
                                            landmark_paths, source_paths, target_paths)

    end_time = time.time()

    find_path_time = end_time - start_time
    print("查找路径时间:", find_path_time, "秒")

    return shortest_paths


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



def estimate_shortest_path(source_node_id, target_node_id, landmarks,
                           landmark_paths, source_paths, target_paths):
    # 计算初始节点到目标节点的最短路径
    shortest_paths = []
    min_dist = float('inf')

    for landmark in landmarks:
        start_paths = source_paths[landmark]
        end_paths = target_paths[landmark]

        if start_paths is None or end_paths is None:
            continue

        dist = len(start_paths[0]) + len(end_paths[0]) - 1
        if dist < min_dist:
            min_dist = dist
            for start_path in start_paths:
                for end_path in end_paths:
                    shortest_path = start_path + end_path[::-1][1:]
                    shortest_paths.append(shortest_path)

    if shortest_paths:
        return shortest_paths

    return None


graph = Graph("http://localhost:7474", auth=("neo4j", "QAZqaz1238546"))

landmarks = [1524, 3342, 4572]

source_node_id = 2640
target_node_id = 3438

# 计时开始
start_time = time.time()

shortest_paths = landmark_labeling_shortest_path(graph, source_node_id, target_node_id, landmarks)

# 计时结束
end_time = time.time()

if shortest_paths:
    print("landmarks:")
    print(landmarks)
    print("Shortest path found:")
    for shortest_path in shortest_paths:
        shortest_path = [str(i) for i in shortest_path]
        print(" -> ".join(shortest_path))
    print("Path length:", len(shortest_path) - 1)
else:
    print("landmarks:")
    print(landmarks)
    print("No path found.")

# 计算总时间
elapsed_time = end_time - start_time

print("总共计算时间:", elapsed_time, "秒")
