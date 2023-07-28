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


def generate_plt(title: str, dataset: dict):
    len_dataset_dict = dict({f'{key}': len(value) for key, value in dataset.items()})
    max_length = len_dataset_dict.get(max(len_dataset_dict))
    # print(len_dataset_dict)
    print(max_length)
    for i in dataset.keys():
        print(dataset[i])
        dataset[i] += [np.nan] * (max_length - len(dataset[i]))

    for i in dataset.keys():
        print(dataset[i])
        exit()


    axis_x = []
    fig, ax = plt.subplots(figsize=(12, 6))




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
                        encoding, compressor, cpu_used_percent_list, mem_used_percent_list = data_row
                        # print(encoding, compressor, cpu_used_percent_list, mem_used_percent_list)
                        item = f'{encoding}-{compressor}'
                        item_cpu_data_dict[item] = cpu_used_percent_list
                        print(mem_used_percent_list)
                        # print(list(mem_used_percent_list))
                        # for i in list(mem_used_percent_list):
                        #     print(i)
                        #     # print(str(i).split(','))
                        exit()
                        item_mem_data_dict[item] = [str(i).split(',')[-1] for i in mem_used_percent_list]
                    # print(item_cpu_data_dict.keys())

                    # 5. 传走啦
                    title = f'{datatype_}-{csv_}'
                    generate_plt(title, item_mem_data_dict)
                    exit()
                    generate_plt(title, item_cpu_data_dict)


if __name__ == '__main__':
    query_processor = QueryProcessor()
    query_processor.process_query()


