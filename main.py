# coding=utf-8
import os
import shutil
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


def get_csv_path(column, row, datatype):
    csv_path = os.path.join(csv_folder, 'column-' + column, 'row-' + row)
    if not os.path.isdir(csv_path):
        print('error: 找不到csv路径%s,exit' % csv_path)
        exit()

    if 'int' in datatype:  # 因为int32和int64都用int
        datatype = 'int'

    csv_file_list = os.listdir(csv_path)

    for csv_file in csv_file_list:
        if datatype in csv_file.lower():
            return os.path.join(csv_path, csv_file)
    print('error: %s下找不到%s类型的csv文件，exit' % (csv_path, datatype))
    exit()


def generate_test_timeseries_list_by_column(sql, columns):
    ts_list = []
    timeseries, datatype, encoding, compressor = common.split_sql(sql)
    for column in range(columns):
        next_level_ts = sql.replace(timeseries, timeseries + '.' + 'column_' + str(column))
        ts_list.append(next_level_ts)
    return ts_list


def exec_linux_order(order):
    print('exec: %s' % order)
    return subprocess.getoutput(order)


def replace_csv_title(test_create_sql_list, csv):
    timeseries_list = []
    for test_create_sql in test_create_sql_list:
        timeseries, datatype, encoding, compressor = common.split_sql(test_create_sql)
        timeseries_list.append(timeseries)

    exec_linux_order('sed -i \'1c Time,%s\' %s' % (','.join(timeseries_list), csv))
    print('output: ', exec_linux_order('cat %s | head -n 1' % csv))


def iotdb_start():
    exec_linux_order('%s/sbin/start-standalone.sh' % iotdb_home)  # 启动
    time.sleep(3)


def iotdb_stop():
    exec_linux_order('%s/sbin/stop-standalone.sh' % iotdb_home)  # 停止
    time.sleep(3)


def iotdb_clear():
    data = os.path.join(iotdb_home, 'data')
    logs = os.path.join(iotdb_home, 'logs')
    shutil.rmtree(data)
    shutil.rmtree(logs)


def iotdb_exec_by_cli(order):
    start_cli = os.path.join(iotdb_home, 'sbin/start-cli.sh')
    exec_linux_order(start_cli + ' -e \'%s\'' % order)


def iotdb_import_csv(csv):
    import_csv = os.path.join(iotdb_home, 'tools/import-csv.sh')
    para = f' -h {iotdb_host} -p {iotdb_port} -u root -pw root -batch {import_batch} -f {csv}'
    before_start = time.time()
    exec_linux_order(import_csv + para)
    after_start = time.time()
    return str(round(after_start - before_start, 3))


def iotdb_get_data_size():
    data_folder = os.path.join(iotdb_home, 'data/datanode/data')
    data_size = exec_linux_order(('du -s %s' % data_folder)).split('\t')[0]  # eg: 16936	<iotdb_home>/data/datanode/data
    tsfile_count = exec_linux_order('find %s -name \'*.tsfile\' | wc -l' % data_folder)
    return data_size, tsfile_count


def iotdb_query(test_create_sql_list):
    sensor_list = []
    for test_create_sql in test_create_sql_list:
        timeseries, datatype, encoding, compressor = common.split_sql(test_create_sql)
        sensor_list.append((str(timeseries).split('.'))[-1])
    str_sensor_list = ','.join(sensor_list)

    before_start = time.time()
    iotdb_exec_by_cli(f'select {str_sensor_list} from root.** limit {query_row}')
    after_start = time.time()

    return str(round(after_start - before_start, 3))


def iotdb_operation(csv_file, test_create_sql_list):
    iotdb_start()
    # 创建时间序列
    iotdb_exec_by_cli(';'.join(test_create_sql_list))
    # ！！！导入csv！！！
    import_elapsed_time = iotdb_import_csv(csv_file)
    # flush
    iotdb_exec_by_cli('flush')
    # ！！！查询！！！
    query_elapsed_time = iotdb_query(test_create_sql_list)

    return import_elapsed_time, query_elapsed_time


def main():
    # 未避免iotdb没启动，先启动
    iotdb_stop()
    iotdb_clear()
    # 生成全部的sql文件列表
    create_timeseries_list = common.generate_all_timeseries()
    print('result', 'datatype', 'encoding', 'compressor', 'column', 'row', 'import_elapsed_time/s','query_elapsed_time/s', 'data_size/kb', 'tsfile_count', sep=',')

    # 遍历，主程序
    for create_sql in create_timeseries_list:
        # 将sql拆分
        timeseries, datatype, encoding, compressor = common.split_sql(create_sql)

        # 序列的多种用例的遍历
        # 列循环，config.ini中的csv_column
        for column in csv_column:
            # 行循环， config.ini中的csv_row
            for row in csv_row:
                # 再重新拆分create-sql
                csv_file = get_csv_path(column, row, datatype.lower())

                # 生成下一级时间序列的list，root.g1.boolean.plain.uncompressed.column_<0/1/2/3/4>
                test_create_sql_list = generate_test_timeseries_list_by_column(create_sql, int(column))

                # 替换csv文件的title
                replace_csv_title(test_create_sql_list, csv_file)

                # 主程序
                import_elapsed_time, query_elapsed_time = iotdb_operation(csv_file, test_create_sql_list)
                # 统计数据文件大小
                data_size, tsfile_count = iotdb_get_data_size()
                # 打印结果
                print('result', datatype, encoding, compressor, column, row, import_elapsed_time, query_elapsed_time, data_size, tsfile_count, sep=',')


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
