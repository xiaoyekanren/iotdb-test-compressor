# coding=utf-8
from prometheus_api_client import PrometheusConnect
import matplotlib.pyplot as plt
import configparser
from _datetime import datetime
import json

cf = configparser.ConfigParser()
cf.read('../config.ini')
# output_result_log_file = cf.get('common', 'output_result_log_file')
output_result_log_file = '../example/all.csv'

prometheus_host = cf.get('generate_img', 'prometheus_host')
prometheus_port = cf.get('generate_img', 'prometheus_port')


def parse_result():
    result_list = []
    with open(output_result_log_file) as result_file:
        result_content = result_file.readlines()
        for one_result in result_content:
            if not one_result or one_result == '\n':
                continue
            datatype, encoding, compressor, column, row, start_time, end_time, import_elapsed_time = one_result.split(',')[1:9]
            result_list.append((datatype, encoding, compressor, column, row, start_time, end_time, import_elapsed_time))
    return result_list


def return_query_content():
    pass


def main():
    # # 创建连接
    # pc = PrometheusConnect(url=f'http://{prometheus_host}:{prometheus_port}', disable_ssl=True)
    #
    # # 检查prometheus是否存活
    # if not pc.check_prometheus_connection():
    #     print('error: prometheus %s连接失败')
    #     exit()
    #
    # # 解析 result_csv
    # # result_list = parse_result()
    #
    # # 判断查询范围
    #
    # query = 'process_used_mem{cluster="defaultCluster", instance="172.20.31.16:9091", job="datanode16", name="process", nodeId="1", nodeType="DATANODE"}'
    # start_time = 1682588000000
    # end_time = 1683088000000
    # step = '6h'
    #
    # results = pc.custom_query_range(
    #     query=query, start_time=datetime.fromtimestamp(start_time / 1000),
    #     end_time=datetime.fromtimestamp(end_time / 1000),
    #     step=step
    # )  # python的时间戳默认是按秒的，result输出的毫秒，这个地方要/1000，list（json）
    # print(f'results={results}')

    # 解析结果
    # data = {}
    # for result in results:
    #     metric_name = result['metric']['__name__']
    #     # print(f'metric_name="{metric_name}"')
    #     if metric_name not in data:
    #         data[metric_name] = {'timestamp': [], 'value': []}
    #     for value in result['values']:
    #         data[metric_name]['timestamp'].append(value[0])
    #         data[metric_name]['value'].append(int(value[1]))
    # print(f'data={data}')
    data = {'process_used_mem': {'timestamp': [1682696000, 1682717600, 1682739200, 1682760800, 1682782400, 1682804000],
                                 'value': [12487490216, 9493839928, 9856614400, 1037616640, 6699586504, 11465323520]}}
    # data = {'process_used_mem': {'timestamp': [1, 3, 5, 7, 9, 11],
    #                              'value': [11, 33, 55, 77, 99, 111]}}

    # 绘制折线图
    for metric_name in data:
        plt.plot(
            data[metric_name]['timestamp'],  # 第一个是横轴
            data[metric_name]['value'],  # 第二个是纵轴
            color="green", linewidth=1.0, linestyle="-",
            label=metric_name  # 左上角的图例
        )
        plt.annotate(
            str(data[metric_name]['value']),  # 标注内容
            xy=(data[metric_name]['timestamp'], data[metric_name]['value']),  # 标注点坐标
            xytext=(data[metric_name]['timestamp'] + 1, data[metric_name]['value'] + 1)  # 标注文本坐标
        )

    # 设置图例和标题
    plt.legend()  # 图例就是左上角显示的区块
    plt.title('test')

    # 显示图像
    plt.show()


def main123():
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]

    plt.plot(x, y)

    for i, j in zip(x, y):
        plt.annotate(str(j), xy=(i, j), xytext=(i + 0.1, j + 0.5))
    plt.show()


if __name__ == '__main__':
    main()
