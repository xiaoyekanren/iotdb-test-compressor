# coding=utf-8
import matplotlib.pyplot as plt
import configparser
from _datetime import datetime
import json
import numpy as np
from generate_img import common
from generate_img import plt_bar


cf = configparser.ConfigParser()
cf.read('config.ini')
# output_result_log_file = cf.get('common', 'output_result_log_file')
output_result_log_file = 'example/all.csv'


def main():
    # 解析 result_csv
    # key = (datatype, column, row)
    # value = (encoding, compressor, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)
    result_dict = common.parse_result(output_result_log_file)

    for one_group_result_dict_key in result_dict.keys():  # 一组结果
        # 拿到这个dict里的list
        one_group_result = result_dict[one_group_result_dict_key]
        # 转置
        one_group_result_switch_dict = common.one_group_result_switch_column(one_group_result)
        # key: 'item_name', 'start_time', 'end_time', 'import_elapsed_time', 'query_elapsed_time', 'data_size', 'compression_rate', 'tsfile_count'
        # 横坐标行
        item_name_tuple = list(one_group_result_switch_dict['item_name'])
        item_name = common.item_name_tuple_to_string(item_name_tuple)  # item_name 从list的tuple 改为 list的string
        # 包含的几种需要生成图片的数据dict的key
        list_key = list(one_group_result_switch_dict.keys())
        list_key.remove('item_name')
        list_key.remove('start_time')
        list_key.remove('end_time')
        list_key.remove('tsfile_count')  # 这个基本都一样，就不画图了

        # 遍历
        for para in list_key:
            # string的数据转float
            data = list(map(float, one_group_result_switch_dict[para]))
            # 拼接title，类型-列-行
            title = '-'.join(one_group_result_dict_key) + '-' + para  # 拼接标题， 类型-列-行-指标
            # 数据缩小小数位，标题增加指标后缀
            data, title = common.optimize_para(para, data, title)
            # 出图
            plt_bar.generate_bar_one_column(item_name, data, title)  # x轴，y轴，标题


if __name__ == '__main__':
    main()
