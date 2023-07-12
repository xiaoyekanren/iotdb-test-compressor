# coding=utf-8
import configparser
from _datetime import datetime
import json
import os
import common

cf = configparser.ConfigParser()
cf.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.ini'))
# output_result_csv_name = cf.get('results', 'output_result_csv_name')
output_result_csv_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../example/all.csv')


def demo():
    item_name = ['PLAIN\nUNCOMPSD', 'PLAIN\nSNAPPY', 'PLAIN\nLZ4', 'PLAIN\nGZIP', 'PLAIN\nZSTD', 'PLAIN\nLZMA2', 'RLE\nUNCOMPSD', 'RLE\nSNAPPY', 'RLE\nLZ4', 'RLE\nGZIP', 'RLE\nZSTD', 'RLE\nLZMA2']
    data = [2.789, 2.698, 2.944, 2.908, 3.009, 2.67, 2.814, 2.939, 2.83, 2.833, 2.931, 2.836]
    img_name = 'BOOLEAN-1-10w-import_elapsed_time/s'
    common.generate_bar_one_column(item_name, data, img_name)  # x,y,title


def main():
    # 解析 result_csv
    # key = (datatype, column, row)
    # value = (encoding, compressor, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)
    result_dict = common.parse_result(output_result_csv_name)

    for one_group_result_dict_key in result_dict.keys():  # 一组结果
        # 拿到这个dict里的list
        one_group_result = result_dict[one_group_result_dict_key]

        # 拿到标题
        title = '-'.join(one_group_result_dict_key)

        # 转置，key: 'item_name', 'start_time', 'end_time', 'import_elapsed_time', 'query_elapsed_time', 'data_size', 'compression_rate', 'tsfile_count'
        one_group_result_switch_dict = common.one_group_result_switch_column(one_group_result)

        # 横坐标行
        item_name_tuple = list(one_group_result_switch_dict['item_name'])
        item_name = common.item_name_tuple_to_string(item_name_tuple)  # item_name 从list的tuple 改为 list的string

        # 包含的几种需要生成图片的数据dict的key
        list_key = list(one_group_result_switch_dict.keys())
        for i in [  # 无需画图的部分
            'item_name',   # item_name是标题
            'start_time',  # 查询prometheus用的
            'end_time',  # # 查询prometheus用的
            'tsfile_count'  # tsfile_count完全一致
        ]:
            list_key.remove(i)

        # 遍历csv的指标项
        for para in list_key:
            # string的数据转float
            data = list(map(float, one_group_result_switch_dict[para]))
            #  拼接标题， 类型-列-行-指标
            bar_title = title + '-' + para
            # 数据缩小小数位，标题增加指标后缀
            data, bar_title = common.optimize_para(para, data, bar_title)
            # 打印最大/小值
            common.print_result_mxx_value(item_name, data, bar_title)
            # 出图
            # common.generate_bar_one_column(item_name, data, bar_title, operate='save')  # x轴，y轴，标题  operate = show or save


if __name__ == '__main__':
    main()
    # demo()





