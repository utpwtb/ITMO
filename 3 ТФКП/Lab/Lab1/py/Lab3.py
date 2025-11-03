import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')


def sierpinski_carpet(h, w, iterations=6):
    """
    生成谢尔宾斯基地毯
    参数:
    h: 图像高度
    w: 图像宽度
    iterations: 迭代次数
    """
    # 创建初始网格，1表示保留，0表示移除
    carpet = np.ones((h, w), dtype=int)

    def remove_squares(arr, level, x, y, size):
        """递归移除中间的正方形"""
        if level == 0:
            return

        # 计算子正方形的大小
        sub_size = size // 3

        # 移除中间的正方形
        start_x = x + sub_size
        start_y = y + sub_size
        arr[start_y:start_y + sub_size, start_x:start_x + sub_size] = 0

        # 对周围的8个子正方形递归处理
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    continue  # 跳过中间已经移除的正方形
                remove_squares(arr, level - 1,
                               x + i * sub_size,
                               y + j * sub_size,
                               sub_size)

    # 从整个画布开始递归
    size = min(h, w)
    remove_squares(carpet, iterations, 0, 0, size)

    return carpet


# 生成并显示谢尔宾斯基地毯
plt.figure(figsize=(10, 10))
carpet = sierpinski_carpet(3000, 3000, iterations=7)
plt.imshow(carpet, cmap='binary', origin='lower')
plt.axis('off')
plt.show()