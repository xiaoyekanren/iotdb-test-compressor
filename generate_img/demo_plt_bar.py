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


def generate_bar_one_column(x, y, title):
    """
    :param x: 横坐标轴，一般放标题
    :param y: 纵坐标轴，一般放数据
    :param title: 标题
    :return: None
    """

    # 获取某些值
    max_idx = y.index(max(y))  # 最大值的index
    min_idx = y.index(min(y))  # 最小值的index
    mark_offset = (max(y) + min(y)) / 2 * 0.1  # 标记数值的偏移量，为（最大数据+最小数据）/2 * 0.1
    y_max_value_range = int(max(y) * 1.3)  # y轴的刻度最大值，也就是最大数的1。3倍
    if 5 < y_max_value_range < 10:  # 避免title被图上的数值遮挡
        y_max_value_range = 10
    if 0 < y_max_value_range < 5:  # 避免title被图上的数值遮挡
        y_max_value_range = 5

    # 打印数据
    # print(title)
    # print(f'x: {x}')
    # print(f'y: {y}')
    # print(max(y))
    # print('\n')

    # 绘制柱形图
    fig, ax = plt.subplots(figsize=(len(x) * 0.6, 6))  # 图片长为x轴总数据量的0.6倍，高6
    plt.xticks(fontsize=8 * 0.8)  # x轴字体为默认字体(8号)的0.8倍
    ax.set_ylim([0, y_max_value_range])  # 设置Y轴范围
    ax.spines['top'].set_visible(False)  # 不显示上边框
    ax.spines['right'].set_visible(False)  # 不显示右边框
    plt.title(str(title), loc='center')  # 设置标题，居中
    # 所有的边框相关配置放到ax.bar上面
    ax.bar(x, y, alpha=0.9, width=0.3)  # 柱形图，透明度为0.9

    # 标记数值
    for i, v in enumerate(y):  # enumerate是python的内置函数，输出: index,value
        ax.text(
            i,  # 标记的x轴坐标
            v + mark_offset,  # 标记的y轴坐标
            str(v), ha='center'  # 居中显示
        )
    # 突出显示最大值
    ax.bar(x[max_idx], y[max_idx], color='red', width=0.3)
    # 突出显示最小值
    ax.bar(x[min_idx], y[min_idx], color='green', width=0.3)

    # 输出，二选一
    plt.show()  # 显示
    # plt.savefig(str(title).replace('/', '-'))  # 保存

    # 关闭
    plt.close()


if __name__ == '__main__':
    demo()
