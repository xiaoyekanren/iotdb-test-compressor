# coding=utf-8
import configparser
import os
import sqlite3
import matplotlib.pyplot as plt
import numpy as np


def query(db_path, sql):
    print('info: connect %s' % db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f'info: exec "{sql}" ')
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


def return_query_results(sqlite_path, columns: list, table: str, conditions: dict):
    """
    @param sqlite_path: sqlite文件
    @param columns: 查询的列，select ***
    @param table: 查询的表，from ***
    @param conditions: 查询的条件，where ***
    @return:
    """
    columns_str = ','.join([str(i) for i in columns])
    conditions_str = ' and '.join(f"{key} = '{value}'" for key, value in conditions.items())
    sql = f"""select {columns_str} from {table} where {conditions_str}"""
    sql_results = query(sqlite_path, sql)
    if len(columns) == 1:
        sql_results_format = [i[0] for i in sql_results]
        return sql_results_format
    else:
        return sql_results


def return_distinct_value_from_list(list_: list):
    """
    @return: list 唯一值
    """
    return list(set(list_))


def return_mem_percent_from_sql_results(mem_used_percent_list: str):
    format_mem_list = str(mem_used_percent_list).lstrip('[').rstrip(']').replace(' ', '')  # 去掉空格，[]
    format_mem_list_2 = format_mem_list.strip('(),')  # 去掉开头、结尾的 左括号、右括号、逗号
    format_mem_list_3 = format_mem_list_2.split('),(')  # 按照),(拆分
    format_mem_list_4 = [str(i).split(',') for i in format_mem_list_3]  # 每组值拆分成2个
    format_mem_list_5 = [(float(a), float(b)) for a, b in format_mem_list_4]  # 将拆分的2个值转换为float类型
    return format_mem_list_5


def return_cpu_percent_from_sql_results(cpu_used_percent_list: str):
    cpu_used_percent_list = cpu_used_percent_list.lstrip('[').rstrip(']').replace(' ','')  # 去掉空格，[]
    cpu_used_percent_list_2 = cpu_used_percent_list.split(',')  # 按照逗号分隔
    cpu_used_percent_list_3 = [float(i) for i in cpu_used_percent_list_2]  # 将每个值转换为float
    return cpu_used_percent_list_3


def generate_plt(title: str, dataset: dict):
    len_dataset_dict = dict({f'{key}': len(list(value)) for key, value in dataset.items()})  # 拼一个字典，title: len(title)
    print(len_dataset_dict)  # 每项对应的采集项的总量
    max_length = len_dataset_dict.get(max(len_dataset_dict, key=len_dataset_dict.get))  # 返回最大的value对应的key
    print(max_length)  # 最大采集项的值
    for i in dataset.keys():  # 将全部项用最大值填充，0
        fill = [0] * (max_length - len(dataset[i]))  # 要填充的空
        dataset[i] += fill

    fig, ax = plt.subplots(figsize=(48, 24))
    axis_x = [i for i in range(max_length)]
    print(axis_x)

    for i in dataset.keys():
        print(dataset.get(i))
        ax.plot(axis_x, dataset.get(i), label=i)

    # 隐藏上边框和右边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 显示图例
    # plt.legend(loc='upper right')  # 图例在右侧显示
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)  # 图例浮于线上

    # 保存照片
    plt.title(title)
    plt.savefig('abc')


class QueryProcessor:
    def __init__(self):
        self.cf = configparser.ConfigParser()
        self.cf.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.ini'))
        self.sqlite_path = '../example/results/results.db'
        self.mark = 'iotdb_master_cb3eca69b1_20230712'
        self.operates = ['import', 'query']

    def process_query(self):
        # 1. 先确定类型
        datatype_list = return_distinct_value_from_list(
            return_query_results(
                self.sqlite_path,
                ['datatype'],
                'system_monitor',
                {'mark': self.mark}
            )
        )  # 返回datatype列的唯一值

        # 2. 确定对应类型的csv文件
        for datatype_ in datatype_list:
            csv_list = return_distinct_value_from_list(
                return_query_results(
                    self.sqlite_path,
                    ['csv_file_name'],
                    'system_monitor',
                    {'mark': self.mark, 'datatype': datatype_}
                )
            )  # 取csv_file_name列的唯一值

            # 3. 取数据
            for csv_ in csv_list:  # csv
                for operate_ in self.operates:  # import or query

                    results_data_set = return_query_results(
                        self.sqlite_path,
                        ['encoding', 'compressor', 'cpu_used_percent_list', 'mem_used_percent_list'],
                        'system_monitor',
                        {'mark': self.mark, 'datatype': datatype_, 'csv_file_name': csv_, 'operate': operate_}
                    )

                    # 4. 准备画图的数据
                    item_cpu_data_dict, item_mem_data_dict = {}, {}
                    for data_row in results_data_set:
                        encoding, compressor, cpu_used_percent_list, mem_used_percent_list = data_row  # 注意，两个list从sql取出来之后实际是str，要转换格式
                        # print(encoding, compressor, cpu_used_percent_list, mem_used_percent_list,sep='\n')
                        item = f'{encoding}-{compressor}'
                        item_cpu_data_dict[item] = return_cpu_percent_from_sql_results(cpu_used_percent_list)  # cpu

                        format_mem_used_percent_list = return_mem_percent_from_sql_results(mem_used_percent_list)  # 将str转换为[(a,b),(c,d)]，直接使用list转话的话，会识别成单个字符
                        item_mem_data_dict[item] = [b for (a, b) in format_mem_used_percent_list]  # 只取b，即内存百分比

                    # 5. 传走啦
                    title = f'{datatype_}-{csv_}'
                    if not 'BOOLEAN' in title:
                        continue
                    generate_plt(title, item_mem_data_dict)
                    exit()
                    generate_plt(title, item_cpu_data_dict)
                    exit()


if __name__ == '__main__':
    query_processor = QueryProcessor()
    query_processor.process_query()


