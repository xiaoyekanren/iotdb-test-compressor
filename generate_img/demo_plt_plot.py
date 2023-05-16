# coding=utf-8
import matplotlib.pyplot as plt


def return_data():
    # data = {'process_used_mem': {
    #     'timestamp': [1, 3, 5, 7, 9, 11],
    #     'value': [11, 33, 55, 77, 99, 111],
    #     # 'value2': [22, 44, 66, 88, 111, 155, 77],
    # }}

    data = {'process_used_mem': {
        'timestamp': [1682696000, 1682717600, 1682739200, 1682760800, 1682782400, 1682804000],
        'value': [12487490216, 9493839928, 9856614400, 1037616640, 6699586504, 11465323520]
    }}

    return data


def main():
    data = dict(return_data())

    for metric_name in data:
        # 数据
        timestamp = data[metric_name]['timestamp']
        values = data[metric_name]['value']
        # 画图
        plt.plot(
            timestamp,  # 第一个是横轴
            values,  # 第二个是纵轴
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
                xytext=(x, y)  # 标注文本坐标
            )

        # 设置图例和标题
        plt.legend()  # 图例就是左上角显示的区块
        plt.title(metric_name)

        # 显示图像
        plt.show()
        # plt.savefig('abc.png')


if __name__ == '__main__':
    main()
