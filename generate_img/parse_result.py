# coding=utf-8
import matplotlib.pyplot as plt
import configparser
from _datetime import datetime
import json
import numpy as np
from generate_img import common
from generate_img import demo_plt_bar


cf = configparser.ConfigParser()
cf.read('config.ini')
# output_result_log_file = cf.get('common', 'output_result_log_file')
output_result_log_file = 'example/all.csv'


def title_tuple_to_string(titles):
    title_string_list = []
    for title in titles:
        string_title = '\n'.join(list(title))
        title_string_list.append(string_title)
    return title_string_list


def main():
    # 解析 result_csv
    # key = (datatype, column, row)
    # value = (encoding, compressor, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)
    result_dict = common.parse_result(output_result_log_file)

    for one_group_result_dict_key in result_dict.keys():  # 一组结果

        one_group_result = result_dict[one_group_result_dict_key]
        # 转置
        one_group_result_switch_dict = common.one_group_result_switch_column(one_group_result)
        # key: 'title', 'start_time', 'end_time', 'import_elapsed_time', 'query_elapsed_time', 'data_size', 'compression_rate', 'tsfile_count'

        # 横坐标行
        title_tuple = list(one_group_result_switch_dict['title'])
        title = title_tuple_to_string(title_tuple)  # 将title 从list的tuple 改为 list的string
        # 包含的几种需要生成图片的数据dict的key
        list_key = list(one_group_result_switch_dict.keys())
        list_key.remove('title')
        list_key.remove('start_time')
        list_key.remove('end_time')

        # 遍历
        for para in list_key:
            data = list(map(float, one_group_result_switch_dict[para]))  # string的数据转float
            demo_plt_bar.generate_bar_one_column(title, data)


if __name__ == '__main__':
    main()
