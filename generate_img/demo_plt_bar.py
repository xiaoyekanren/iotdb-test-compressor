import matplotlib.pyplot as plt
import numpy as np


# 生成柱形图的demo
def demo():
    # 准备数据
    data = np.array([[3, 5, 2], [4, 6, 3], [5, 4, 1]])
    # 设置x轴标签
    labels = ["A", "B", "C"]
    # 设置颜色
    colors = ["r", "g", "b"]
    # 设置柱子宽度
    width = 0.2
    # 画图
    for i in range(data.shape[1]):
        plt.bar(np.arange(data.shape[0]) + i * width, data[:, i], width=width, color=colors[i], label=f"Column {i+1}")
    # 设置图例
    plt.legend()
    # 设置x轴刻度
    plt.xticks(np.arange(data.shape[0]) + width, labels)
    # 显示图形
    plt.show()


def generate_bar_one_column(title, data):
    # 数据
    x = title  # x轴
    y = data  # y轴

    # 获取某些值
    max_idx = y.index(max(y))  # 最大值
    if max_idx == 0:
        return
    print(max_idx)
    min_idx = y.index(min(y))  # 最小值

    # 绘制柱形图
    fig, ax = plt.subplots(figsize=(12, 6))  # 图片长12，高6
    plt.xticks(fontsize=8 * 0.8)  # x轴字体为默认字体8号的0.8倍
    ax.set_ylim([0, int((max_idx+ 1) * 1.2)])  # 设置Y轴范围
    ax.spines['top'].set_visible(False)  # 不显示上边框
    ax.spines['right'].set_visible(False)  # 不显示右边框
    # 所有的边框相关配置放到ax.bar上面
    ax.bar(x, y, alpha=0.9)  # 柱形图，透明度为0.9

    # 标记数值
    for i, v in enumerate(y):  # enumerate是python的内置函数，输出: index,value
        ax.text(
            i,  # x轴坐标
            v + 0.2,  # y轴坐标稍微向上一点
            str(v), ha='center'  # 居中显示
        )

    # 突出显示最大值
    ax.bar(x[max_idx], y[max_idx], color='red')
    # 突出显示最小值
    ax.bar(x[min_idx], y[min_idx], color='green')

    # 显示
    plt.show()


if __name__ == '__main__':
    demo()
