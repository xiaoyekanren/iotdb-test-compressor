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


def item_name_tuple_to_string(titles):
    title_string_list = []
    for title in titles:
        string_title = '\n'.join(list(title))
        if 'UNCOMPRESSED' in title:
            string_title = string_title.replace('UNCOMPRESSED', 'UNCOMPSD')
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
        # key: 'item_name', 'start_time', 'end_time', 'import_elapsed_time', 'query_elapsed_time', 'data_size', 'compression_rate', 'tsfile_count'

        # 横坐标行
        item_name_tuple = list(one_group_result_switch_dict['item_name'])
        item_name = item_name_tuple_to_string(item_name_tuple)  # item_name 从list的tuple 改为 list的string
        # 包含的几种需要生成图片的数据dict的key
        list_key = list(one_group_result_switch_dict.keys())
        list_key.remove('item_name')
        list_key.remove('start_time')
        list_key.remove('end_time')
        list_key.remove('tsfile_count')  # 这个基本都一样，就不画图了

        # 遍历
        for para in list_key:

            data = list(map(float, one_group_result_switch_dict[para]))  # string的数据转float

            title = '-'.join(one_group_result_dict_key) + '-' + para  # 拼接标题， 类型-列-行-指标

            # 对指定指标进行优化
            if para == 'data_size':  # 数据大小改为MB，标题增加MB
                new_data = []
                for value in data:
                    new_data.append(round(value / 1024, 2))
                data = new_data
                title = title + '/MB'
            if para == 'compression_rate':  # 小数点后保留3位
                new_data = []
                for value in data:
                    new_data.append(round(value, 3))
                data = new_data
            if para == 'import_elapsed_time' or para == 'query_elapsed_time':
                title = title + '/s'

            demo_plt_bar.generate_bar_one_column(item_name, data, title)  # x轴，y轴，标题，


if __name__ == '__main__':
    main()
