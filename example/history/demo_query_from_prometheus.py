# coding=utf-8
from prometheus_api_client import PrometheusConnect
import configparser
import datetime
from datetime import datetime
import generate_bar_from_csv
import os

cf = configparser.ConfigParser()
cf.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config.ini'))

prometheus_host = cf.get('generate_img', 'prometheus_host')
prometheus_port = cf.get('generate_img', 'prometheus_port')
query_step = cf.get('generate_img', 'query_step')
# output_result_csv_name = cf.get('results', 'output_result_csv_name')
output_result_csv_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../example/all.csv')


def demo():
    # 创建连接
    pc = PrometheusConnect(url=f'http://{prometheus_host}:{prometheus_port}', disable_ssl=True)

    # 检查prometheus是否存活
    if not pc.check_prometheus_connection():
        print('error: prometheus %s连接失败')
        exit()

    start_time = 0
    end_time = 0

    query = 'process_used_mem{cluster="defaultCluster", instance="172.20.31.16:9091", job="datanode16", name="process", nodeId="1", nodeType="DATANODE"}'

    results = pc.custom_query_range(
        query=query, start_time=datetime.fromtimestamp(start_time),
        end_time=datetime.fromtimestamp(end_time),
        step=query_step
    )  # python的时间戳默认是按秒的，result输出的毫秒，这个地方要/1000，list（json）
    print(f'results={results}')

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


def get_job_about_test_host(datatype):
    # 这个地方可以获取job，或者是instance，只是instance还要拼端口
    if datatype == 'BOOLEAN':
        return 'datanode'
    elif datatype == 'INT32':
        return 'datanode15'
    elif datatype == 'INT64':
        return 'datanode16'
    elif datatype == 'DOUBLE':
        return 'datanode17'
    elif datatype == 'FLOAT':
        return 'datanode18'
    elif datatype == 'TEXT':
        return 'datanode24'


def rewrite_timestamp(results):
    # 重写从prometheus查询的数据的时间戳，时间戳无意义，重写成index
    results = list(results)
    new_list = []
    for index, value in enumerate(results):
        value = list(value)
        new_list.append([index, value[-1]])
    return new_list


def get_data(start_time, end_time, datatype):
    start_time, end_time = int(start_time / 1000), int(end_time / 1000)
    list_result = []
    # process_cpu_load{nodeType='DATANODE'}
    para_list = ['process_used_mem', 'process_cpu_load']
    # 创建连接
    pc = PrometheusConnect(url=f'http://{prometheus_host}:{prometheus_port}', disable_ssl=True)
    for para in para_list:
        query = '%s{name="process", nodeType="DATANODE", job="%s"}' % (para, get_job_about_test_host(datatype))
        # print(query, datetime.fromtimestamp(start_time), datetime.fromtimestamp(end_time))
        results = pc.custom_query_range(
            query=query,
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            step=query_step,
        )
        if results:
            results = results[0].get('values')  # 只拿value的全部值[[timestamp1,value1],[timestamp2,value2],[timestamp3,value3]]
            results = rewrite_timestamp(results)  # 时间戳无意义，将时间戳全部使用index重写
        else:
            results = 'NONE'
            print(query, start_time, end_time,'is NONE', sep=' ')
        # print(f'{para}: {results}')
        list_result.append(results)
    return list_result


def query_from_prometheus(start_time_list, end_time_list, plot_lable, title, item_name):
    if str(title).split('-')[-1] != '1000w':  # 只打印1000W行的记录，其他的值太少，打印无意义
        return

    start_time_list, end_time_list = list(map(int, start_time_list)), list(map(int, end_time_list))  # list-string， 转为list-int
    datatype = str(title).split('-')[0]  # 标题列，用来确定主机，很关键

    print(title, datatype, item_name, sep='-')

    mem_data_lists = []
    cpu_data_lists = []
    for index, value in enumerate(plot_lable):  # enumerate是python的内置函数，输出: index,value

        mem_data_list, cpu_data_list = get_data(start_time_list[index], end_time_list[index], datatype)

        mem_data_lists.append(mem_data_list)
        cpu_data_lists.append(cpu_data_list)

    print(mem_data_lists, cpu_data_lists)


def main():
    # 解析 result_csv
    # key = (datatype, column, row)
    # value = (encoding, compressor, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)
    result_dict = generate_bar_from_csv.parse_result(output_result_csv_name)

    for one_group_result_dict_key in result_dict.keys():  # 一组结果
        # 拿到这个dict里的list
        one_group_result = result_dict[one_group_result_dict_key]

        # 拿到标题
        title = '-'.join(one_group_result_dict_key)

        # 转置，key: 'item_name', 'start_time', 'end_time', 'import_elapsed_time', 'query_elapsed_time', 'data_size', 'compression_rate', 'tsfile_count'
        one_group_result_switch_dict = generate_bar_from_csv.one_group_result_switch_column(one_group_result)

        # 横坐标行
        item_name_tuple = list(one_group_result_switch_dict['item_name'])
        item_name = generate_bar_from_csv.item_name_tuple_to_string(item_name_tuple)  # item_name 从list的tuple 改为 list的string

        # 未完成
        # 读取prometheus
        start_time_list, end_time_list, plot_lable = one_group_result_switch_dict['start_time'], one_group_result_switch_dict['end_time'], item_name  #
        query_from_prometheus(start_time_list, end_time_list, plot_lable, title, item_name)
        # list_mem, list_cpu = data_lists
        # print(list_mem, list_cpu)


if __name__ == '__main__':
    main()

