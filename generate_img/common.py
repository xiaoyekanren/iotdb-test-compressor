# coding=utf-8
import configparser

# 不知道用不用得到


def parse_result(output_result_log_file):
    result_dict = {}

    with open(output_result_log_file) as result_file:
        result_content = result_file.readlines()  # 读取

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
        # encoding, compressor, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count
        column_dict['item_name'].append((data[0:2]))
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


def print_result_max_value(x, y, title):
    # 用于输出结果的最大值
    if 'data_size' in str('-'.join(title.split('-')[1:]), ):  # 不打印data_size相关内容
        return
    print(
        str(title).split('-')[0],  # 数据类型 TEXT
        '-'.join(title.split('-')[1:]),  # 列-行-指标，5-1000w-query_elapsed_time/s
        str(x[y.index(max(y))]).replace('\n', '-').replace('UNCOMPSD', 'UNCOMPRESSED'),
        # 编码-压缩，DICTIONARY-UNCOMPRESSED
        str(max(y)),  # 值
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


def optimize_para(para, data,title):
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



