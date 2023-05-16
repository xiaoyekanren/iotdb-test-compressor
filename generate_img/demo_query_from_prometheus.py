# coding=utf-8
from prometheus_api_client import PrometheusConnect
import configparser
import datetime
from datetime import datetime

cf = configparser.ConfigParser()
prometheus_host = cf.get('generate_img', 'prometheus_host')
prometheus_port = cf.get('generate_img', 'prometheus_port')
query_step = cf.get('generate_img', 'query_step')


def main():
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


if __name__ == '__main__':
    main()
