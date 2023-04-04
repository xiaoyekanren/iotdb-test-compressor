# coding=utf-8
import os
import shutil
import subprocess
import time


iotdb_home = '/Users/zhangzhengming/apache-iotdb-1.2.0-SNAPSHOT-all-bin'
csv_folder = '/Users/zhangzhengming/iotdb_data_src/line1000w'
sql_file = 'sql.txt'


def iotdb_get_data_size():
    iotdb_exec_by_cli('flush')
    data_folder = os.path.join(iotdb_home, 'data/datanode/data')
    size = 0
    for root, dirs, files in os.walk(data_folder):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size


def get_csv_path(datatype):
    if datatype == 'DOUBLE':
        return os.path.join(csv_folder, 'double.csv')
    elif datatype == 'FLOAT':
        return os.path.join(csv_folder, 'float.csv')
    elif datatype == 'INT32' or datatype == 'INT64':
        return os.path.join(csv_folder, 'int32_64.csv')
    elif datatype == 'TEXT':
        return os.path.join(csv_folder, 'text.csv')
    elif datatype == 'BOOLEAN':
        return os.path.join(csv_folder, 'boolean.csv')
    else:
        print('检查到不符合的数据类型，%s' % datatype)
        exit()


def get_sql_list():
    sql_list = []
    with open(sql_file, 'r') as lines:
        for i in lines.readlines():
            if i[0] == '#' or not i.strip('\n'):
                continue
            sql_list.append(i.strip('\n'))
    return sql_list


def parse_sql(sql):
    timeseries = sql.split(' ')[2]  # root.g1.boolean.plain.UNCOMPRESSED
    datatype_encoding_compressor = sql.split(' ')[4].strip(';')  # datatype=BOOLEAN,encoding=PLAIN,compressor=UNCOMPRESSED
    datatype = (((datatype_encoding_compressor.split(','))[0]).split('='))[1]
    encoding = (((datatype_encoding_compressor.split(','))[1]).split('='))[1]
    compressor = (((datatype_encoding_compressor.split(','))[2]).split('='))[1]
    return timeseries, datatype, encoding, compressor


def exec_linux_order(order):
    return subprocess.getoutput(order)


def replace_csv_title(timeseries, csv):
    exec_linux_order('sed -i \'1c Time,%s\' %s' % (timeseries, csv))


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
    exec_linux_order(start_cli + '-e \'%s\'' + order)


def iotdb_import_csv(csv):
    import_csv = os.path.join(iotdb_home, 'tools/import-csv.sh')
    para = ' -h 127.0.0.1 -p 6667 -u root -pw root -batch 1000000 -f %s' % csv
    before_start = time.time()
    exec_linux_order(import_csv + para)
    after_start = time.time()
    # print('Elapsed time %s' % (str(after_start - before_start)))
    return str(after_start - before_start)


# def iotdb_get_data_size():
#     data_folder = os.path.join(iotdb_home, 'data/datanode/data')
#     iotdb_exec_by_cli('flush')
#     data_size = os.path.getsize(data_folder)
#     return data_size


def iotdb_operation(csv_file):
    iotdb_stop()
    iotdb_clear()
    iotdb_start()
    elapsed_time = iotdb_import_csv(csv_file)
    return elapsed_time


def main():
    iotdb_start()
    sql_list = get_sql_list()
    for sql in sql_list:
        timeseries, datatype, encoding, compressor = parse_sql(sql)
        csv_file = get_csv_path(datatype)
        replace_csv_title(timeseries, csv_file)
        elapsed_time = iotdb_operation(csv_file)
        data_size = iotdb_get_data_size()
        print(datatype, encoding, compressor, elapsed_time, data_size)


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
