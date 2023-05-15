# coding=utf-8
from prometheus_api_client import PrometheusConnect
import matplotlib.pyplot as plt
import configparser
from _datetime import datetime
import json

cf = configparser.ConfigParser()
cf.read('config.ini')
# output_result_log_file = cf.get('common', 'output_result_log_file')
output_result_log_file = 'example/all.csv'
prometheus_host = cf.get('generate_img', 'prometheus_host')
prometheus_port = cf.get('generate_img', 'prometheus_port')
query_step = cf.get('generate_img', 'query_step')


def parse_result():
    result_dict = {}

    with open(output_result_log_file) as result_file:
        result_content = result_file.readlines()

        for one_result in result_content:
            if not one_result or one_result == '\n' or one_result.split(',')[1] == 'datatype':  # 跳过 空、空行、标题行
                continue

            datatype, encoding, compressor, column, row, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count = one_result.rstrip('\n').split(',')[1:]  # 去掉第一列的 'result'
            key = (datatype, column, row)
            value = (encoding, compressor, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)

            if key not in result_dict.keys():
                result_dict[key] = [value]
                continue
            result_dict[key].append(value)

    return result_dict


def generate_result_from_prometheus():
    pass


def generate_result_from_csv(result_dict):
    for case in result_dict.keys():


        exit()


def main():
    # 创建连接
    pc = PrometheusConnect(url=f'http://{prometheus_host}:{prometheus_port}', disable_ssl=True)

    # 检查prometheus是否存活
    if not pc.check_prometheus_connection():
        print('error: prometheus %s连接失败')
        exit()

    # 解析 result_csv
    result_dict = parse_result()

    for i in result_dict.keys():
        print(i)
        for k in result_dict[i]:
            print(k)
        print('\n\n')

    # datatype, encoding, compressor, column, row, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count

    generate_result_from_csv(result_dict)

    # 大循环
    for result in result_list:
        datatype, encoding, compressor, column, row, start_time, end_time, import_elapsed_time = result

        start_time = start_time / 1000
        end_time = end_time / 1000

        query = 'process_used_mem{cluster="defaultCluster", instance="172.20.31.16:9091", job="datanode16", name="process", nodeId="1", nodeType="DATANODE"}'


        results = pc.custom_query_range(
            query=query, start_time=datetime.fromtimestamp(start_time / 1000),
            end_time=datetime.fromtimestamp(end_time / 1000),
            step=query_step
        )  # python的时间戳默认是按秒的，result输出的毫秒，这个地方要/1000，list（json）
        print(f'results={results}')
        exit()

    # 解析结果
    data = {}
    for result in results:
        metric_name = result['metric']['__name__']
        # print(f'metric_name="{metric_name}"')
        if metric_name not in data:
            data[metric_name] = {'timestamp': [], 'value': []}
        for value in result['values']:
            data[metric_name]['timestamp'].append(value[0])
            data[metric_name]['value'].append(int(value[1]))
    print(f'data={data}')


if __name__ == '__main__':
    main()
