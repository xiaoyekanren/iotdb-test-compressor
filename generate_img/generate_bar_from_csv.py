# coding=utf-8
import configparser
import os
import matplotlib.pyplot as plt

cf = configparser.ConfigParser()
cf.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.ini'))


def return_csv_abspath():
    result_dir = cf.get('results', 'result_dir')
    if not os.path.isdir(result_dir):  # 如果找打不到，就设置为默认
        result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../example/results')
    output_result_csv_name = os.path.abspath(os.path.join(result_dir, cf.get('results', 'output_result_csv_name')))
    return output_result_csv_name


def return_img_output_dir():
    img_output_dir = cf.get('generate_img', 'img_output_dir')
    if not img_output_dir:
        img_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../example/img_bar')
    if not os.path.exists(img_output_dir):
        print(f'info: 检测到结果存放文件夹不存在，自动创建{img_output_dir}.')
        os.makedirs(img_output_dir)
    return img_output_dir


def parse_result(output_result_csv_name):
    result_dict = {}

    with open(output_result_csv_name) as result_file:
        result_content = result_file.readlines()  # 读取

        for one_result in result_content:
            if not one_result or one_result == '\n':  # 跳过空、空行
                continue
            elif one_result.split(',')[1] == 'mark' and one_result.split(',')[2] == 'datatype':  # 跳过标题行
                continue
            one_result_list = (one_result.rstrip('\n')).split(',')
            mark, datatype, encoding, compressor, csv_file_basename, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count = one_result_list[1:]  # 去掉第一列的 'result'
            key = (mark, datatype, csv_file_basename)
            value = (encoding, compressor, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)

            if key not in result_dict.keys():
                result_dict[key] = [value]
                continue
            result_dict[key].append(value)

    return result_dict


def one_group_result_switch_column(datas):
    """
    :param datas: 一组数据
    :return: 转置
    """
    # 原数据
    # ('BOOLEAN', '1', '10w')
    # ('PLAIN', 'UNCOMPRESSED', '1682588586982', '1682588596120', '2.789', '3.577', '119399', '17.13623', '1')
    # ('PLAIN', 'SNAPPY', '1682591600318', '1682591609247', '2.698', '3.544', '11908', '171.82138', '1')
    # 转换成如下
    # start_time
    # ['1682588586982', '1682591600318', '1682594360734', '1682596871048', '1682599539307', '1682602168723',
    #  '1682604822206', '1682607669310', '1682610269860', '1682612672519', '1682615133974', '1682617543806']
    # end_time
    # ['1682588596120', '1682591609247', '1682594369633', '1682596880058', '1682599548510', '1682602177675',
    #  '1682604831285', '1682607678370', '1682610278912', '1682612681327', '1682615143069', '1682617552642']
    # import_elapsed_time
    # ['2.789', '2.698', '2.944', '2.908', '3.009', '2.67', '2.814', '2.939', '2.83', '2.833', '2.931', '2.836']

    column_dict = {'item_name': [], 'start_time': [], 'end_time': [], 'import_elapsed_time': [], 'query_elapsed_time': [], 'data_size': [], 'compression_rate': [], 'tsfile_count': []}
    for data in datas:
        # print(data)
        # value = (encoding, compressor, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)
        column_dict['item_name'].append((data[0:2]))  # encoding, compressor
        column_dict['start_time'].append(data[2])
        column_dict['end_time'].append(data[3])
        column_dict['import_elapsed_time'].append(data[4])
        column_dict['query_elapsed_time'].append(data[5])
        column_dict['data_size'].append(data[6])
        column_dict['compression_rate'].append(data[7])
        column_dict['tsfile_count'].append(data[8])
    # for key in column_dict.keys():
    #     print(key, column_dict[key], sep='\n')
    return column_dict


def print_result_mxx_value(item_name, data, bar_title):
    title = (bar_title.replace('\n', '-'))  # 去换行符，替换压缩的简写成完成版

    # 用于输出结果的最xx值
    if 'data_size' in title:  # 不打印data_size相关内容,实际上datasize这个图是多余的，可以考虑后面删除
        return
    if 'query' in title or 'import' in title:  # 查询导入是给最小值
        mxx_value = min(data)
        mxx_value_item = str(item_name[data.index(mxx_value)]).replace('\n', '-')
    else:  # 其他给最大值，压缩
        mxx_value = max(data)
        mxx_value_item = str(item_name[data.index(mxx_value)]).replace('\n', '-')

    print(
        title.split('-')[0],  # 数据类型 DOUBLE, INT32, INT64, DOUBLE, FLOAT, TEXT
        '-'.join(title.split('-')[1:]),  # 列-行-指标，5-1000w-query_elapsed_time/s
        mxx_value_item.replace('UNCOMPSD', 'UNCOMPRESSED'),  # 值的 编码+压缩 DICTIONARY-UNCOMPRESSED
        mxx_value,  # 值
        '\n',
        sep='\n'
    )


def item_name_tuple_to_string(titles):
    title_string_list = []
    for title in titles:
        string_title = '\n'.join(list(title))
        if 'UNCOMPRESSED' in title:
            string_title = string_title.replace('UNCOMPRESSED', 'UNCOMPSD')
        title_string_list.append(string_title)
    return title_string_list


def optimize_para(para, data, title):
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

    return data, title


def generate_bar_one_column(x, y, title, operate='save'):
    """ 生成柱形图
    :param x: 横坐标轴，一般放标题
    :param y: 纵坐标轴，一般放数据
    :param title: 标题
    :param operate: 操作方式：show，save，none
    :return: None
    """
    img_output_dir = return_img_output_dir()

    # 获取某些值
    max_idx = y.index(max(y))  # 最大值的index
    min_idx = y.index(min(y))  # 最小值的index
    mark_offset = (max(y) + min(y)) / 2 * 0.1  # 标记数值的偏移量，为（最大数据+最小数据）/2 * 0.1
    y_max_value_range = int(max(y) * 1.3)  # y轴的刻度最大值，也就是最大数的1。3倍
    if 5 < y_max_value_range < 10:  # 避免title被图上的数值遮挡
        y_max_value_range = 10
    if 0 < y_max_value_range < 5:  # 避免title被图上的数值遮挡
        y_max_value_range = 5

    # 绘制柱形图
    fig, ax = plt.subplots(figsize=(len(x) * 0.6, 6))  # 图片长为x轴总数据量的0.6倍，高6
    plt.xticks(fontsize=8 * 0.8)  # x轴字体为默认字体(8号)的0.8倍
    ax.set_ylim([0, y_max_value_range])  # 设置Y轴范围
    ax.spines['top'].set_visible(False)  # 不显示上边框
    ax.spines['right'].set_visible(False)  # 不显示右边框
    plt.title(str(title), loc='center')  # 设置标题，居中
    # 所有的边框相关配置放到ax.bar上面
    ax.bar(x, y, alpha=0.9, width=0.3)  # 柱形图，透明度为0.9

    # 在柱形图上标记值
    for i, v in enumerate(y):  # enumerate是python的内置函数，输出: index,value
        ax.text(
            i,  # 标记的x轴坐标
            v + mark_offset,  # 标记的y轴坐标
            str(v), ha='center'  # 居中显示
        )
    # 突出显示最大值
    ax.bar(x[max_idx], y[max_idx], color='red', width=0.3)
    # 突出显示最小值
    ax.bar(x[min_idx], y[min_idx], color='green', width=0.3)

    # 输出，二选一
    if operate == 'show':
        plt.show()  # 显示
    elif operate == 'save':
        plt.savefig(os.path.join(img_output_dir, str(title).replace('/', '-')))  # 保存

    # 关闭
    plt.close()


def demo():
    item_name = ['PLAIN\nUNCOMPSD', 'PLAIN\nSNAPPY', 'PLAIN\nLZ4', 'PLAIN\nGZIP', 'PLAIN\nZSTD', 'PLAIN\nLZMA2', 'RLE\nUNCOMPSD', 'RLE\nSNAPPY', 'RLE\nLZ4', 'RLE\nGZIP', 'RLE\nZSTD', 'RLE\nLZMA2']
    data = [2.789, 2.698, 2.944, 2.908, 3.009, 2.67, 2.814, 2.939, 2.83, 2.833, 2.931, 2.836]
    img_name = 'BOOLEAN-1-10w-import_elapsed_time/s'
    generate_bar_one_column(item_name, data, img_name)  # x,y,title


def main():
    output_result_csv_name = return_csv_abspath()  # 从config.ini里拿csv的路径
    # 解析 result_csv
    # key = (mark, datatype, csv_file_basename)
    # value = (encoding, compressor, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)
    result_dict = parse_result(output_result_csv_name)

    for one_group_result_dict_key in result_dict.keys():  # 一组结果的key
        # 拿到这个dict里的list
        one_group_result = result_dict[one_group_result_dict_key]  # 真·一组结果，(start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)

        # 拿到标题
        # title = '-'.join(one_group_result_dict_key[1:])  # datatype, csv_file_basename
        title = one_group_result_dict_key[1] + '-' + str(one_group_result_dict_key[2]).replace('-', '_').replace('.', '_')

        # 转置，key: 'item_name', 'start_time', 'end_time', 'import_elapsed_time', 'query_elapsed_time', 'data_size', 'compression_rate', 'tsfile_count'
        one_group_result_switch_dict = one_group_result_switch_column(one_group_result)

        # 横坐标行
        item_name_tuple = list(one_group_result_switch_dict['item_name'])
        item_name = item_name_tuple_to_string(item_name_tuple)  # item_name 从list的tuple 改为 list的string

        # 包含的几种需要生成图片的数据dict的key
        list_key = list(one_group_result_switch_dict.keys())
        for i in [  # 无需画图的部分
            'item_name',   # item_name是标题
            'start_time',  # 查询prometheus用的
            'end_time',  # # 查询prometheus用的
            'tsfile_count',  # tsfile_count完全一致
            'data_size',  # 和压缩比冲突，多余
        ]:
            list_key.remove(i)

        # 遍历csv的指标项
        for para in list_key:
            # string的数据转float
            data = list(map(float, one_group_result_switch_dict[para]))
            #  拼接标题， 类型-列-行-指标
            bar_title = title + '-' + para
            # 数据缩小小数位，标题增加指标后缀
            data, bar_title = optimize_para(para, data, bar_title)
            # 打印最大/小值
            print_result_mxx_value(item_name, data, bar_title)
            # 出图
            generate_bar_one_column(item_name, data, bar_title, operate='save')  # x轴，y轴，标题  operate = show or save


if __name__ == '__main__':
    main()
    # demo()
