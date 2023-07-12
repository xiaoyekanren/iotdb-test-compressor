# coding=utf-8
import os
import subprocess
import time
import common
import configparser

from order import iotdb_operation
from order import exec_linux_order
from order import iotdb_get_data_size
from order import iotdb_stop
from order import iotdb_rm_data

from sql import create_db
from sql import init_table
from sql import insert


cf = configparser.ConfigParser()
# file info
cf.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.ini'))
# mark for cur test
mark = cf.get('parameters', 'mark')
# 测试控制
case_retry_times = int(cf.get('parameters', 'retry_times'))


def check_result_dir():
    result_dir = os.path.abspath(cf.get('results', 'result_dir'))
    if not os.path.exists(result_dir):
        print(f'info: 检测到结果存放文件夹不存在，自动创建{result_dir}.')
        os.makedirs(result_dir)
    return result_dir


def replace_csv_title(timeseries_list, csv):
    """
    这个地方使用sed是因为python的实现方式，会加载整个csv文件，这样性能太差，使用sed则只会修改第一行
    """
    exec_linux_order('sed -i \'1c Time,%s\' %s' % (','.join(timeseries_list), csv), info='替换csv title.')


def get_csv_list(datatype):
    csv_dataset_dir = cf.get('common', 'csv_dataset_dir')  # 数据集路径
    csv_list = []
    csv_dir = os.path.join(csv_dataset_dir, datatype.upper())
    if os.path.isfile(csv_dir):
        print(f'error: {csv_dir} is not a folder.')
        exit()
    else:
        for file in os.listdir(csv_dir):
            abs_file_ = os.path.abspath(os.path.join(csv_dir, file))
            if abs_file_.split('.')[-1] == 'csv':
                csv_list.append(abs_file_)
    match_csv_file = len(csv_list)
    if match_csv_file == 0:
        print(f'error: 未能匹配到类型{datatype}可用的csv文件，exit.')
        exit()
    return csv_list


def get_column_from_csv(csv_file):
    with open(csv_file, 'r') as csv_file:
        first_line = csv_file.readline()  # 只取首行
    count_column = len(first_line.split(',')) - 1  # 例如第一行是：Time,root.test.g_0.d_0.s_15， -1减去了Time，所以csv就是1列
    return int(count_column)


def split_sql(sql):
    """
    create timeseries root.g1.boolean.plain.uncompressed with datatype=BOOLEAN,encoding=PLAIN,compressor=UNCOMPRESSED;
    """
    sql_split = (sql.rstrip(';')).split(' ')  # ['create', 'timeseries', 'root.g1.boolean.plain.uncompressed', 'with', 'datatype=BOOLEAN,encoding=PLAIN,compressor=UNCOMPRESSED']
    timeseries = sql_split[2]  # root.g1.boolean.plain.uncompressed
    datatype_encoding_compressor = sql_split[4]

    datatype_encoding_compressor_list = datatype_encoding_compressor.split(',')  # ['datatype=BOOLEAN', 'encoding=PLAIN', 'compressor=UNCOMPRESSED']
    datatype = ((datatype_encoding_compressor_list[0]).split('='))[1]  # BOOLEAN
    encoding = ((datatype_encoding_compressor_list[1]).split('='))[1]  # PLAIN
    compressor = ((datatype_encoding_compressor_list[2]).split('='))[1]  # UNCOMPRESSED

    return timeseries, datatype, encoding, compressor


def generate_test_timeseries_list_by_column(sql, timeseries, columns):
    create_ts_list = []
    ts_list = []
    for column in range(columns):  # 确定本次测试有多少列，就生成多少个创建时间序列的sql
        ts = f'{timeseries}.column_{column}'
        ts_list.append(ts)
        next_level_ts = sql.replace(timeseries, ts)  # 替换 timeseries 为 timeseries_number
        create_ts_list.append(next_level_ts.rstrip(';'))  # 无需保留最后的分号，iotdb_operation在创建时间序列的时候，会将list转为使用分号的分隔的string，
    return ts_list, create_ts_list


def check_result_file(output_result_csv_name, datatype, encoding, compressor, csv_file_name):
    with open(output_result_csv_name) as result_file:
        result_content = result_file.readlines()
        for one_result in result_content:
            if not one_result or one_result == '\n':
                continue
            history_case = ','.join(((one_result.rstrip('\n')).split(','))[:5])
            cur_case = f'result,{datatype},{encoding},{compressor},{csv_file_name}'
            if history_case == cur_case:
                return True
        return False


def write_to_result_file(result, output_result_csv_name):
    with open(output_result_csv_name, 'a+') as result_log:
        result_log.writelines('\n' + result)


def check_is_exist_result_file(output_result_csv_name):
    status = os.path.isfile(output_result_csv_name)
    print(f'info: 结果文件是否存在: {status}')
    return status


def check_is_exist_result_history(output_result_csv_name, datatype, encoding, compressor, csv_file_name):
    has_result_file = check_is_exist_result_file(output_result_csv_name)  # true or false
    if has_result_file:
        has_result = check_result_file(output_result_csv_name, datatype, encoding, compressor, csv_file_name)
        if has_result:
            return True
    return False


def main_workflow(create_sql, timeseries, csv_file, db_path, resource_usage_column_title):
    # 替换csv文件的title
    # 基于当前create_sql，在path后追加一段，用于区分多列（1，3，5列）
    # root.g1.boolean.plain.uncompressed.column_<0/1/2/3/4>，column_0，column_1，column_2...
    csv_count_column = get_column_from_csv(csv_file)  # csv有几列，用于替换csv的title
    ts_list, create_ts_list = generate_test_timeseries_list_by_column(create_sql, timeseries, csv_count_column)  # ts_list => [root.sg1.d1.s1,root.sg1.d1.s2], create_ts_list =>[create timeseries root.sg1.d1.s1_cloumn1, ***]
    replace_csv_title(ts_list, csv_file)  # 替换csv的title

    # 通过判断tsfile的大小和数量来确定是否执行成功
    import_elapsed_time, query_elapsed_time, data_size, tsfile_count = 0, 0, 0, 0  # 统计数据文件大小
    for i in range(case_retry_times + 1):
        if data_size == 0 or tsfile_count == 0:  # 如果失败，增加sleep时间，默认重试5次
            print(f'info: 开始第{i+1}次测试')
            import_elapsed_time, query_elapsed_time = iotdb_operation(csv_file, create_ts_list, db_path, resource_usage_column_title, sleep_step=i)  # 如果启动失败了，就增加sleep的时间
            data_size, tsfile_count = iotdb_get_data_size()
            continue
        else:
            break
    if data_size == 0 or tsfile_count == 0:
        print('error: 报错，然后重试了%s次，还是失败，GG.' % case_retry_times)
        exit()
    # 统计压缩率
    csv_size = os.path.getsize(csv_file)  # 确定csv大小
    compression_rate = round(csv_size / data_size, 2)
    return import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count


def main():
    # 检查结果目录是否存在
    result_dir = check_result_dir()
    # 检查存放结果的csv和db
    output_result_csv_name = os.path.join(result_dir, cf.get('results', 'output_result_csv_name'))  # 绝对路径
    db_path = os.path.join(result_dir, cf.get('results', 'output_result_db_name'))
    # 生成全部的sql文件列表
    timeseries_list = common.generate_all_timeseries()
    # 输出csv的title
    title = 'result,mark,datatype,encoding,compressor,csv_file_name,start_time_in_ms,end_time_in_ms,import_elapsed_time_in_ms,query_elapsed_time_in_ms,data_size_in_byte,compression_rate,tsfile_count'
    print(title)
    write_to_result_file(title, output_result_csv_name)
    # 创建db文件用于存储结果
    create_db(db_path)
    init_table(db_path)  # 初始化db文件

    # 主程序，遍历timeseries_list
    for create_sql in timeseries_list:
        # 从sql里面拆出来各项
        timeseries, datatype, encoding, compressor = split_sql(create_sql)

        # 检测进度
        print(f'info: 开始测试 {create_sql}')
        print(f'info: 当前第{timeseries_list.index(create_sql) + 1}个，剩余{len(timeseries_list) - timeseries_list.index(create_sql) - 1}个')  # index 可能会是0

        # 根据数据类型拿到可用的csv文件的绝对路径列表
        csv_list = get_csv_list(datatype)

        # 使用csv列表来循环
        for csv_file in csv_list:  # csv_file 是绝对路径
            # 开始执行
            csv_file_basename = os.path.basename(csv_file)  # 只留csv文件名+扩展名
            print(f'info: 开始 {datatype}-{encoding}-{compressor}-{csv_file_basename}，{time.strftime("%Y-%m-%d %H:%M:%S" ,time.localtime())}.')
            # 检查是否有历史记录：
            if check_is_exist_result_history(output_result_csv_name, datatype, encoding, compressor, csv_file_basename):
                print(f'info: 检测到 {datatype},{encoding},{compressor},{csv_file_basename} 已经测试完毕，跳过.')
                continue
            # 测试主流程
            start_time = int(time.time() * 1000)
            resource_usage_column_title = f'{mark}!{datatype}!{encoding}!{compressor}!{csv_file_basename}'
            import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count = main_workflow(create_sql, timeseries, csv_file, db_path, resource_usage_column_title)
            end_time = int(time.time() * 1000)

            # 打印、存储结果
            data = (mark, datatype, encoding, compressor, csv_file_basename, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count)  # 应和result保持一致
            result = 'result,' + ','.join([str(x) for x in data])
            print(result)
            write_to_result_file(result, output_result_csv_name)
            # 入库，注意问号的数量要和data的数量保持一致
            insert_query = '''
            INSERT INTO records (mark, datatype, encoding, compressor, csv_file_name, start_time_in_ms, end_time_in_ms, import_elapsed_time_in_ms, query_elapsed_time_in_ms, data_size_in_byte, compression_rate, tsfile_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            insert(db_path, insert_query, data)

            # 清理掉iotdb
            iotdb_stop()
            iotdb_rm_data()

            # 结束
            print(f'info: 结束 {datatype}-{encoding}-{compressor}-{csv_file_basename}，{time.strftime("%Y-%m-%d %H:%M:%S" ,time.localtime())}.')

    print('info: 程序执行完毕')


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
