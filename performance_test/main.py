# coding=utf-8
import os
import subprocess
import time
import common
import configparser

cf = configparser.ConfigParser()
cf.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.ini'))
iotdb_home = cf.get('common', 'iotdb_home')
csv_folder = cf.get('common', 'csv_folder')
iotdb_host = cf.get('connect', 'iotdb_host')
iotdb_port = cf.get('connect', 'iotdb_port')
import_batch = cf.get('import', 'import_batch')
output_result_log_file = cf.get('common', 'output_result_log_file')
retry_times = int(cf.get('common', 'retry_times'))
output_system_resource_usage_file = cf.get('common', 'output_system_resource_usage_file')
system_resource_check_interval = cf.get('common', 'system_resource_check_interval')


def get_csv_list(datatype):
    csv_list = []
    csv_dir = os.path.join(csv_folder, datatype.upper())
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


def exec_linux_order(order, info=None, output=False):
    """
    默认：return elapsed_time
    output=True, return elapsed_time ,results
    """
    if info:  # 有要打的信息，就打
        print(f'info: {info}')
    if not output:  # 如果不要输出，就指给/dev/null
        order = order + ' > /dev/null'

    print(f'exec: {order}')

    if not output:  # 无输出，返回：耗时，1个
        exec_start_time = time.time() * 1000
        subprocess.getoutput(order + ' > /dev/null')
        exec_finish_time = time.time() * 1000
        return str(round(exec_finish_time - exec_start_time, 2))
    else:  # 有输出，返回：结果, 耗时，2个
        exec_start_time = time.time() * 1000
        results = subprocess.getoutput(order)
        exec_finish_time = time.time() * 1000
        print('output: %s' % results.replace('\n', ', '))
        return str(round(exec_finish_time - exec_start_time, 2)), results


def replace_csv_title(timeseries_list, csv):
    """
    这个地方使用sed是因为python的实现方式，会加载整个csv文件，这样性能太差，使用sed则只会修改第一行
    """
    exec_linux_order('sed -i \'1c Time,%s\' %s' % (','.join(timeseries_list), csv), info='替换csv title.')
    exec_linux_order('cat %s | head -n 1' % csv)


def iotdb_start(sleep_step=0):
    sleep = 10
    exec_linux_order('%s/sbin/start-standalone.sh' % iotdb_home, info='启动iotdb.')  # 启动
    time.sleep(sleep + sleep * sleep_step)


def iotdb_stop(sleep_step=0):
    sleep = 10
    exec_linux_order('%s/sbin/stop-standalone.sh' % iotdb_home, info='停止iotdb.')  # 停止
    time.sleep(sleep + sleep * sleep_step)


def iotdb_rm_data(sleep_step=0):
    sleep = 3
    data = os.path.join(iotdb_home, 'data')
    logs = os.path.join(iotdb_home, 'logs')
    exec_linux_order(f'rm -rf {data}', info='清空数据目录.')
    exec_linux_order(f'rm -rf {logs}', info='清空log目录.')
    time.sleep(sleep + sleep * sleep_step)


def iotdb_exec_by_cli(order, info=None, output=False):
    start_cli = os.path.join(iotdb_home, 'sbin/start-cli.sh')
    return exec_linux_order(f'{start_cli} -h {iotdb_host} -p {iotdb_port} -e \'{order}\'', info=info, output=output)


def iotdb_get_data_size():
    data_folder = os.path.join(iotdb_home, 'data/datanode/data')
    elapsed_time, tsfile_and_resource_list = exec_linux_order(f'find {data_folder} -name *.tsfile*', info='获取tsfile和resource文件数量', output=True).split('\n')  # 这个地方的output不能是false，也就是必须打印出来，不然exec_linux_order会返回空
    data_size, tsfile_count = 0, 0

    for file in tsfile_and_resource_list:
        file_abs_path = os.path.join(data_folder, file)
        # 文件大小
        data_size += os.path.getsize(file_abs_path)
        # tsfile数量
        if file_abs_path.split('.')[-1] == 'tsfile':
            tsfile_count += 1
    if data_size == 0 or tsfile_count == 0:
        print('error: tsfile数量为0，或者文件大小为0，要检查.')

    return data_size, tsfile_count


def iotdb_query(info=None):
    sql = 'select * from root.**'
    return iotdb_exec_by_cli(sql, info=info)


def iotdb_import_csv(csv, info=None):
    import_csv = os.path.join(iotdb_home, 'tools/import-csv.sh')
    para = f' -h {iotdb_host} -p {iotdb_port} -u root -pw root -batch {import_batch} -f {csv}'
    return exec_linux_order(import_csv + para, info=info)


def iotdb_operation(csv_file, test_create_sql_list, sleep_step=0):
    iotdb_stop(sleep_step)
    iotdb_rm_data(sleep_step)
    iotdb_start(sleep_step)

    # 创建时间序列
    iotdb_exec_by_cli(';'.join(test_create_sql_list), info='创建时间序列', output=False)
    # 导入csv
    import_elapsed_time = iotdb_import_csv(csv_file, info='导入csv.')
    # flush
    iotdb_exec_by_cli('flush', info='flush')
    # restart
    iotdb_stop()
    iotdb_start()
    # 查询
    query_elapsed_time = iotdb_query(info='开始查询')

    return import_elapsed_time, query_elapsed_time


def check_result_file(datatype, encoding, compressor, csv_file_name):
    with open(output_result_log_file) as result_file:
        result_content = result_file.readlines()
        for one_result in result_content:
            if not one_result or one_result == '\n':
                continue
            history_case = ','.join(((one_result.rstrip('\n')).split(','))[:5])
            cur_case = f'result,{datatype},{encoding},{compressor},{csv_file_name}'
            if history_case == cur_case:
                return True
        return False


def write_to_result_file(result):
    with open(output_result_log_file, 'a+') as result_log:
        result_log.writelines('\n' + result)


def check_is_exist_result_file():
    status = os.path.isfile(output_result_log_file)
    print(f'info: 结果文件是否存在: {status}')
    return status


def check_is_exist_result_history(datatype, encoding, compressor, csv_file_name):
    has_result_file = check_is_exist_result_file()  # true or false
    if has_result_file:
        has_result = check_result_file(datatype, encoding, compressor, csv_file_name)
        if has_result:
            return True
    return False


def main_workflow(create_sql, timeseries, csv_file):
    # 替换csv文件的title
    # 基于当前create_sql，在path后追加一段，用于区分多列（1，3，5列）
    # root.g1.boolean.plain.uncompressed.column_<0/1/2/3/4>，column_0，column_1，column_2...
    csv_count_column = get_column_from_csv(csv_file)  # csv有几列，用于替换csv的title
    ts_list, create_ts_list = generate_test_timeseries_list_by_column(create_sql, timeseries, csv_count_column)  # ts_list => [root.sg1.d1.s1,root.sg1.d1.s2], create_ts_list =>[create timeseries root.sg1.d1.s1_cloumn1, ***]
    replace_csv_title(ts_list, csv_file)  # 替换csv的title

    # 通过判断tsfile的大小和数量来确定是否执行成功
    import_elapsed_time, query_elapsed_time, data_size, tsfile_count = 0, 0, 0, 0  # 统计数据文件大小
    for i in range(retry_times + 1):
        if data_size == 0 or tsfile_count == 0:  # 如果失败，增加sleep时间，默认重试5次
            print(f'info: 开始第{i+1}次测试')
            import_elapsed_time, query_elapsed_time = iotdb_operation(csv_file, create_ts_list, sleep_step=i)
            data_size, tsfile_count = iotdb_get_data_size()
            continue
        else:
            break
    if data_size == 0 or tsfile_count == 0:
        print('error: 报错，然后重试了%s次，还是失败，GG.' % retry_times)
        exit()
    # 统计压缩率
    csv_size = os.path.getsize(csv_file)  # 确定csv大小
    compression_rate = round(csv_size / data_size, 5)
    return import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count


def main():
    # 生成全部的sql文件列表
    timeseries_list = common.generate_all_timeseries()
    # 输出csv的title
    title = 'result,datatype,encoding,compressor,csv_file_name,start_time_in_ms,end_time_in_ms,import_elapsed_time_in_ms,query_elapsed_time_in_ms,data_size_in_byte,compression_rate,tsfile_count'
    print(title)
    write_to_result_file(title)

    # 主程序，遍历timeseries_list
    for create_sql in timeseries_list:
        # 从sql里面拆出来各项
        timeseries, datatype, encoding, compressor = split_sql(create_sql)
        # 根据数据类型拿到可用的csv文件的绝对路径列表
        csv_list = get_csv_list(datatype)
        # 使用csv列表来循环
        for csv_file in csv_list:  # csv_file 是绝对路径
            csv_file_basename = os.path.basename(csv_file)
            print(f'info: 开始 {datatype}-{encoding}-{compressor}-{csv_file_basename}，{time.strftime("%Y-%m-%d %H:%M:%S" ,time.localtime())}.')
            # 检测进度
            print(f'当前第{timeseries_list.index(create_sql)}个，剩余{len(timeseries_list) - timeseries_list.index(create_sql)}个')
            # 检查是否有历史记录：
            if check_is_exist_result_history(datatype, encoding, compressor, csv_file_basename):
                print(f'info: 检测到 {datatype},{encoding},{compressor},{csv_file_basename} 已经测试完毕，跳过.')
                continue
            # 测试主流程
            start_time = time.time() * 1000
            import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count = main_workflow(create_sql, timeseries, csv_file)
            end_time = time.time() * 1000
            # 打印、存储结果
            result = f'result,{datatype},{encoding},{compressor},{csv_file_basename},{start_time},{end_time},{import_elapsed_time},{query_elapsed_time},{data_size},{compression_rate},{tsfile_count}'
            print(result)
            write_to_result_file(result)
            # 清理掉iotdb
            iotdb_stop()
            iotdb_rm_data()
            # 结束
            print(f'info: 结束 {datatype}-{encoding}-{compressor}-{csv_file_basename}，{time.strftime("%Y-%m-%d %H:%M:%S" ,time.localtime())}.')

    print('info: 程序执行完毕')


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
