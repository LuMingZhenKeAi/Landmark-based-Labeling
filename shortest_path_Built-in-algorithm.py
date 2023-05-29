from py2neo import Graph
import time
import random


def shortest_path_bfs(graph, start_node_id, end_node_id):
    result = graph.run("""
        MATCH (start), (end)
        WHERE ID(start) = $startNodeId AND ID(end) = $endNodeId
        CALL algo.shortestPath.stream(start, end, 'node_id')
        YIELD nodeId, cost
        RETURN algo.getNodeById(nodeId) AS node, cost
        """, startNodeId=start_node_id, endNodeId=end_node_id)

    path = []
    total_cost = 0
    for record in result:
        node = record["node"]
        path.append(str(node["node_id"]))
        total_cost = record["cost"]

    return path, total_cost


# Neo4j数据库连接信息
uri = "http://localhost:7474"  # 修改为你的数据库URI
username = "neo4j"  # 修改为你的数据库用户名
password = "QAZqaz1238546"  # 修改为你的数据库密码

# 创建数据库连接
graph = Graph(uri, auth=(username, password))

# 计时开始
start_time = time.time()

# 随机生成100个节点对并计算最短路径
list_range = range(0, 7624)
for i in range(100):
    node_pair = random.sample(list_range, 2)
    path, cost = shortest_path_bfs(graph, node_pair[0], node_pair[1])
    # 打印结果
    if path:
        print("最短路径:", " -> ".join(path))
        print("路径长度:", cost)
    else:
        print("未找到路径")

# 计时结束
end_time = time.time()

# 计算总时间
elapsed_time = end_time - start_time

print("总共计算时间:", elapsed_time, "秒")