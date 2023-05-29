# 打开A文本文件以及B文本文件
with open("D:/codes/Python/GraduationProject/dataset/lastfm_asia/edge.csv", "r") as file_a, open("D:/codes/Python/GraduationProject/dataset/lastfm_asia/edges.csv", "a") as file_b:
    # 逐行读取A文本文件的内容
    for line in file_a:
        # 去除行末尾的换行符
        line = line.strip()

        # 按空格分割行中的数字
        numbers = line.split(",")

        # 确保行中至少有两个数字
        if len(numbers) >= 2:
            # 将两个数字中间添加逗号
            new_line = numbers[0] + "," + numbers[1] + "," + "DIRECTED"

            # 将新行写入B文本文件
            file_b.write(new_line + "\n")
