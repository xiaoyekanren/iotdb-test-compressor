# coding=utf-8
import os
import subprocess
import time
import common
import configparser

cf = configparser.ConfigParser()
cf.read('config.ini')
iotdb_home = cf.get('common', 'iotdb_home')
csv_folder = cf.get('common', 'csv_folder')
csv_column = cf.get('test_loop', 'csv_column').split(',')
csv_row = cf.get('test_loop', 'csv_row').split(',')
iotdb_host = cf.get('connect', 'iotdb_host')
iotdb_port = cf.get('connect', 'iotdb_port')
import_batch = cf.get('import', 'import_batch')
query_row = cf.get('query', 'query_row')


def get_csv(column, row, datatype):
    csv_path = os.path.join(csv_folder, 'column-' + column, 'row-' + row)
    if not os.path.isdir(csv_path):
        print('error: 找不到csv路径%s,exit' % csv_path)
        exit()

    if 'int' in datatype:  # 因为int32和int64都用int
        datatype = 'int'

    csv_file_list = os.listdir(csv_path)

    for csv_file in csv_file_list:
        if datatype in csv_file.lower():
            csv_file_abs_path = os.path.join(csv_path, csv_file)
            return csv_file_abs_path, os.path.getsize(csv_file_abs_path)
    print('error: %s下找不到%s类型的csv文件，exit' % (csv_path, datatype))
    exit()


def generate_test_timeseries_list_by_column(sql, columns):
    ts_list = []
    timeseries, datatype, encoding, compressor = common.split_sql(sql)
    for column in range(columns):
        next_level_ts = sql.replace(timeseries, timeseries + '.' + 'column_' + str(column))
        ts_list.append(next_level_ts)
    return ts_list


def exec_linux_order(order, info=None, output=True):
    if info:
        print(f'info: {info}')

    print(f'exec: {order}')
    results = subprocess.getoutput(order)

    if output:
        print('output: %s' % results.replace('\n', ', '))

    return results


def replace_csv_title(test_create_sql_list, csv):
    timeseries_list = []
    for test_create_sql in test_create_sql_list:
        timeseries, datatype, encoding, compressor = common.split_sql(test_create_sql)
        timeseries_list.append(timeseries)

    exec_linux_order('sed -i \'1c Time,%s\' %s' % (','.join(timeseries_list), csv), info='替换csv title.', output=False)
    exec_linux_order('cat %s | head -n 1' % csv)


def iotdb_start():
    exec_linux_order('%s/sbin/start-standalone.sh' % iotdb_home, info='启动iotdb.')  # 启动
    time.sleep(10)


def iotdb_stop():
    exec_linux_order('%s/sbin/stop-standalone.sh' % iotdb_home, info='停止iotdb.')  # 停止
    time.sleep(10)


def iotdb_rm_data():
    data = os.path.join(iotdb_home, 'data')
    logs = os.path.join(iotdb_home, 'logs')
    exec_linux_order(f'rm -rf {data}; rm -rf {logs}', info='清空数据、log目录.', output=False)
    time.sleep(3)


def iotdb_delete_sg():
    iotdb_exec_by_cli('delete storage group root.**', info='删除存储组.')


def iotdb_exec_by_cli(order, info=None, output=True):
    start_cli = os.path.join(iotdb_home, 'sbin/start-cli.sh')
    exec_linux_order(f'{start_cli} -h {iotdb_host} -p {iotdb_port} -e {order}', info=info, output=output)


def iotdb_import_csv(csv, info=None):
    import_csv = os.path.join(iotdb_home, 'tools/import-csv.sh')
    para = f' -h {iotdb_host} -p {iotdb_port} -u root -pw root -batch {import_batch} -f {csv}'
    before_start = time.time()
    exec_linux_order(import_csv + para, info=info)
    after_start = time.time()
    return str(round(after_start - before_start, 3))


def iotdb_get_data_size():
    data_folder = os.path.join(iotdb_home, 'data/datanode/data')

    tsfile_and_resource_list = exec_linux_order(f'find {data_folder} -name *.tsfile*', info='获取tsfile和resource文件数量').split('\n')

    data_size = 0
    tsfile_count = 0

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


def iotdb_query(test_create_sql_list, info=None):
    sensor_list = []
    for test_create_sql in test_create_sql_list:
        timeseries, datatype, encoding, compressor = common.split_sql(test_create_sql)
        sensor_list.append((str(timeseries).split('.'))[-1])
    str_sensor_list = ','.join(sensor_list)

    sql = f'select {str_sensor_list} from root.** limit {query_row}'

    before_start = time.time()
    iotdb_exec_by_cli(sql, info=info, output=False)
    after_start = time.time()

    return str(round(after_start - before_start, 3))


def iotdb_operation(csv_file, test_create_sql_list):
    # 创建时间序列
    iotdb_exec_by_cli(';'.join(test_create_sql_list), info='创建时间序列')
    # ！！！导入csv！！！
    import_elapsed_time = iotdb_import_csv(csv_file, info='导入csv.')
    # flush
    iotdb_exec_by_cli('flush', info='flush')
    # ！！！查询！！！
    query_elapsed_time = iotdb_query(test_create_sql_list, info='开始查询')

    return import_elapsed_time, query_elapsed_time


def main():
    # 尝试停止现有iotdb，并清理数据
    iotdb_stop()
    iotdb_rm_data()
    # 生成全部的sql文件列表
    create_timeseries_list = common.generate_all_timeseries()
    print('result', 'datatype', 'encoding', 'compressor', 'column', 'row', 'start_time/ms', 'end_time/ms', 'import_elapsed_time/s', 'query_elapsed_time/s', 'data_size/b', 'compression_rate', 'tsfile_count', sep=',')

    # 遍历，主程序
    for create_sql in create_timeseries_list:
        # 将sql拆分
        timeseries, datatype, encoding, compressor = common.split_sql(create_sql)

        # 序列的多种用例的遍历
        # 列循环，config.ini中的csv_column
        for column in csv_column:
            # 行循环， config.ini中的csv_row
            for row in csv_row:
                # 启动iotdb
                iotdb_start()
                # 启动时间
                start_time = int(time.time() * 1000)

                # 再重新拆分create-sql
                csv_file, csv_size = get_csv(column, row, datatype.lower())

                # 生成下一级时间序列的list，root.g1.boolean.plain.uncompressed.column_<0/1/2/3/4>
                test_create_sql_list = generate_test_timeseries_list_by_column(create_sql, int(column))

                # 替换csv文件的title
                replace_csv_title(test_create_sql_list, csv_file)

                # 主程序
                import_elapsed_time, query_elapsed_time = iotdb_operation(csv_file, test_create_sql_list)
                # 统计数据文件大小
                data_size, tsfile_count = iotdb_get_data_size()
                # 统计压缩率
                compression_rate = round(csv_size / data_size, 5)
                # 结束时间
                end_time = int(time.time() * 1000)

                # 打印结果
                print('result', datatype, encoding, compressor, column, row, start_time, end_time, import_elapsed_time, query_elapsed_time, data_size, compression_rate, tsfile_count, sep=',')

                # 清理掉iotdb
                iotdb_stop()
                iotdb_rm_data()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
