# coding=utf-8
import matplotlib.pyplot as plt


def return_data():
    data = {'process_used_mem': {
        'timestamp': [1, 3, 5, 7, 9, 11],
        'value': [11, 33, 55, 77, 99, 111],
        'value2': [22, 44, 66, 88, 111, 155, 77],
        # 'value3': [15, 38, 46, 66, 19]
    }}

    # data = {'process_used_mem': {
    #     'timestamp': [1682696000, 1682717600, 1682739200, 1682760800, 1682782400, 1682804000],
    #     'value': [12487490216, 9493839928, 9856614400, 1037616640, 6699586504, 11465323520]
    # }}

    return data


def demo(data):

    for metric_name in data:
        # 数据
        timestamp = data[metric_name]['timestamp']
        values = data[metric_name]['value']
        values2 = data[metric_name]['value2']
        # values3 = data[metric_name]['value3']

        mark_offset = (max(values) + min(values)) / 2 * 0.1  # 标记数值的偏移量，为（最大数据+最小数据）/2 * 0.1

        # 画图
        plt.plot(
            timestamp,  # 第一个是横轴
            values,  # 第二个是纵轴
            values2,
            # values3,
            marker='o',  # 突出显示点
            color="green",  # 线条颜色
            linewidth=1.0,  # 线宽
            linestyle="-",  # 线类型
            label='value',  # 左上角的图例
        )
        # 标注，但是有错误
        for i in range(len(timestamp)):
            x = timestamp[i]
            y = values[i]

            plt.annotate(
                y,  # 标注内容
                xy=(x, y),  # 标注点坐标
                xytext=(x, y + mark_offset,),  # 标注文本坐标
                ha='center',  # 居中对齐
            )

        # 设置图例和标题
        plt.legend()  # 图例就是左上角显示的区块
        plt.title(metric_name)

        # 显示图像
        plt.show()
        # plt.savefig('abc.png')
        plt.close()


def main():
    import matplotlib.pyplot as plt
    import datetime

    # 生成假数据
    x = [1, 2, 3, 4, 5]
    y1 = [2, 3, 1, 4, 2]
    y2 = [3, 1, 2, 2, 4]
    y3 = [1, 2, 3, 1, 3]
    y4 = [4, 3, 2, 1, 2]
    y5 = [1, 4, 1, 3, 4]

    # 设置图片大小为12x6
    fig, ax = plt.subplots(figsize=(12, 6))

    # 画出5条折线
    ax.plot(x, y1, label='Line 1')
    ax.plot(x, y2, label='Line 2')
    ax.plot(x, y3, label='Line 3')
    ax.plot(x, y4, label='Line 4')
    ax.plot(x, y5, label='Line 5')

    # 在每个点上方标记数值
    for i in range(len(x)):
        ax.text(x[i], y1[i] + 0.1, y1[i], ha='center')
        ax.text(x[i], y2[i] + 0.1, y2[i], ha='center')
        ax.text(x[i], y3[i] + 0.1, y3[i], ha='center')
        ax.text(x[i], y4[i] + 0.1, y4[i], ha='center')
        ax.text(x[i], y5[i] + 0.1, y5[i], ha='center')

    # 找出最大值并标记为红色
    ymax = max(max(y1), max(y2), max(y3), max(y4), max(y5))
    xmax = x[y1.index(ymax)]
    ax.text(xmax, ymax + 0.2, ymax, ha='center', color='red')

    # 设置Y轴范围
    ax.set_ylim([0, 5])

    # 隐藏上边框和右边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 设置x轴字号为标准的0.8倍
    plt.xticks(fontsize=8)

    # 设置图片标题为当天日期
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    plt.title(now)

    # 显示图例和保存图片
    plt.legend()
    plt.savefig('line_chart.png')
    plt.show()


if __name__ == '__main__':
    # demo(dict(return_data()))
    main()
