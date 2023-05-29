from py2neo import Graph
from collections import deque
import time


def bidirectional_bfs(graph, start_node_id, end_node_id):
    # 创建前向和后向队列，分别用于从起始节点和目标节点开始扩展
    forward_queue = deque([(start_node_id, [start_node_id])])
    backward_queue = deque([(end_node_id, [end_node_id])])

    # 创建前向和后向访问集合，用于跟踪已访问的节点
    forward_visited = set()
    backward_visited = set()

    # 创建记录路径长度集合，记录路径队列和存放最短路径列表
    path_length = {1000000}
    path_queue = deque([(0, [])])
    result_list = []

    # 记录前向队列和后向队列中记录的路径长度的最小值
    forward_queue_min = 1000000
    backward_queue_min = 1000000

    # 在前向和后向队列都不为空时执行循环
    while forward_queue and backward_queue:
        # 从前向队列中获取下一个节点进行扩展
        node_id, path = forward_queue.popleft()
        forward_visited.add(node_id)

        # 检查该节点是否也存在于后向访问集合中
        if node_id in backward_visited:
            # 找到了一条路径
            for rela in backward_queue:
                if rela[0] == node_id:
                    path.pop()
                    path_length.add(len(path + rela[1]))
                    path_queue.append((len(path + rela[1]), path + rela[1]))

        # 剪枝
        min_length = min(path_length)
        for rela in backward_queue:
            if len(rela[1]) < backward_queue_min:
                backward_queue_min = len(rela[1])
        if len(path) + backward_queue_min <= min_length:
            # 扩展当前节点的邻居节点
            neighbors = graph.run(f"MATCH (n)-[]->(m) WHERE ID(n) = {node_id} RETURN ID(m)")
            for neighbor in neighbors:
                neighbor_id = neighbor["ID(m)"]
                if neighbor_id not in forward_visited:
                    forward_queue.append((neighbor_id, path + [neighbor_id]))
                    forward_visited.add(neighbor_id)

        # 从后向队列中获取下一个节点进行扩展
        node_id, path = backward_queue.popleft()
        backward_visited.add(node_id)

        # 检查该节点是否也存在于前向访问集合中
        if node_id in forward_visited:
            # 找到了最短路径
            for rela in forward_queue:
                if rela[0] == node_id:
                    rela[1].pop()
                    path_length.add(len(rela[1] + path))
                    path_queue.append((len(rela[1] + path), rela[1] + path))

        # 剪枝
        min_length = min(path_length)
        for rela in forward_queue:
            if len(rela[1]) < forward_queue_min:
                forward_queue_min = len(rela[1])
        if len(path) + forward_queue_min <= min_length:
            # 扩展当前节点的邻居节点
            neighbors = graph.run(f"MATCH (n)-[]->(m) WHERE ID(m) = {node_id} RETURN ID(n)")
            for neighbor in neighbors:
                neighbor_id = neighbor["ID(n)"]
                if neighbor_id not in backward_visited:
                    backward_queue.append((neighbor_id, [neighbor_id] + path))
                    backward_visited.add(neighbor_id)

    if path_length:
        min_length = min(path_length)
        for rela in path_queue:
            if rela[0] == min_length:
                result_list.append(rela[1])
        return result_list

    # 如果无法找到最短路径，则返回空列表表示路径不存在
    return []


# 建立与Neo4j数据库的连接
graph = Graph("http://localhost:7474", auth=("neo4j", "QAZqaz1238546"))

# 定义起始节点和目标节点的ID
start_node_id = 9
end_node_id = 6094

# 计时开始
start_time = time.time()

# 使用Bidirectional BFS查找最短路径
shortest_paths = bidirectional_bfs(graph, start_node_id, end_node_id)

# 计时结束
end_time = time.time()

if shortest_paths:
    print("最短路径:")
    for shortest_path in shortest_paths:
        shortest_path = [str(i) for i in shortest_path]
        print(" -> ".join(shortest_path))
    print("Path length:", len(shortest_path) - 1)
else:
    print("路径不存在")

# 计算总时间
elapsed_time = end_time - start_time

print("总共计算时间:", elapsed_time, "秒")
