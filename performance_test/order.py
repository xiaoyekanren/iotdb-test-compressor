# coding=utf-8
import time
import subprocess
import configparser
import os
import psutil
import multiprocessing

from sql import insert

cf = configparser.ConfigParser()
cf.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.ini'))

# iotdb info
iotdb_home = cf.get('common', 'iotdb_home')
iotdb_host = cf.get('connect', 'iotdb_host')
iotdb_port = cf.get('connect', 'iotdb_port')
import_batch = cf.get('import', 'import_batch')
#
system_resource_check_interval = float(cf.get('common', 'system_resource_check_interval'))
#
cpu_usage_list = []
mem_usage_list = []


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
        elapsed_time = str(round(exec_finish_time - exec_start_time, 2))
        return elapsed_time  # 返回1个
    else:  # 有输出，返回：结果, 耗时，2个
        exec_start_time = time.time() * 1000
        results = subprocess.getoutput(order)
        exec_finish_time = time.time() * 1000
        elapsed_time = str(round(exec_finish_time - exec_start_time, 2))
        print('output: %s' % results.replace('\n', ', '))
        return elapsed_time, results  # 返回2个值


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
    order = f'find {data_folder} -name *.tsfile*'
    elapsed_time, tsfile_and_resource_list = exec_linux_order(order, info='获取tsfile和resource文件数量', output=True)  # 这个地方的output不能是false，也就是必须打印出来，不然exec_linux_order会返回空
    data_size, tsfile_count = 0, 0

    for file in str(tsfile_and_resource_list).split('\n'):  # output的输出，把换行符替换了，这个地方实际是\n
        file_abs_path = os.path.join(data_folder, file)
        # 文件大小
        data_size += os.path.getsize(file_abs_path)
        # tsfile数量
        if file_abs_path.split('.')[-1] == 'tsfile':
            tsfile_count += 1
    if data_size == 0 or tsfile_count == 0:
        print('error: tsfile数量为0，或者文件大小为0，要检查.')

    return data_size, tsfile_count


def iotdb_query(result_queue):
    sql = 'select * from root.**'
    # return iotdb_exec_by_cli(sql, info=f'info: {sql}')
    elapsed_time = iotdb_exec_by_cli(sql, info=f'info: {sql}')
    result_queue.put(elapsed_time)


def iotdb_import_csv(csv, result_queue):
    import_csv = os.path.join(iotdb_home, 'tools/import-csv.sh')
    para = f' -h {iotdb_host} -p {iotdb_port} -u root -pw root -batch {import_batch} -f {csv}'
    elapsed_time = exec_linux_order(import_csv + para)
    result_queue.put(elapsed_time)
    # return exec_linux_order(import_csv + para)


def iotdb_get_datanode_pid():
    # timechodb -> com.timecho.iotdb.DataNode
    # iotdb -> org.apache.iotdb.db.service.DataNode
    order = "ps -ef|grep '[D]ataNode'  | awk {'print $2'}"
    elapsed_time, iotdb_datanode_pid = exec_linux_order(order=order, output=True)
    return int(iotdb_datanode_pid)  # 这个地方，要转int，不然在后面的multiprocessing会将pid拆成单独的字母，例如123456拆成了 '1','2','3','4','5','6'


def get_cpu_usage(iotdb_datanode_pid):
    global cpu_usage_list
    process = psutil.Process(iotdb_datanode_pid)
    while True:
        print(f'---debug---cpu_usage_list---: {cpu_usage_list}')
        try:
            cpu_percent = process.cpu_percent(interval=1)
            cpu_usage_list.append(cpu_percent)
            time.sleep(0.5)
        except psutil.NoSuchProcess:
            cpu_usage_list.append('-1')
        time.sleep(system_resource_check_interval)


def get_mem_usage(iotdb_datanode_pid):
    global mem_usage_list
    while True:
        print(f'---debug---mem_usage_list---: {mem_usage_list}')
        elapsed_time, results = exec_linux_order(f'jstat -gc {iotdb_datanode_pid} | awk \'NR==2\'', output=True)
        results_float_list = [float(x) for x in str(results).split()]  # 列表里，str转浮点
        # S0C: 年轻代中第一个幸存区的容量（字节）。
        # S1C: 年轻代中第二个幸存区的容量（字节）。
        # S0U: 年轻代中第一个幸存区的使用量（字节）。
        # S1U: 年轻代中第二个幸存区的使用量（字节）。
        # EC: 年轻代的容量（字节）。
        # EU: 年轻代的使用量（字节）。
        # OC: 老年代的容量（字节）。
        # OU: 老年代的使用量（字节）。
        S0C, S1C, S0U, S1U, EC, EU, OC, OU = results_float_list[0:8]
        total_memory = S0C + S1C + EC + OC
        used_memory = S0U + S1U + EU + OU
        used_memory_percent = round(float(used_memory) / float(total_memory), 4)
        mem_usage_list.append((used_memory, used_memory_percent))
        time.sleep(system_resource_check_interval)


def test_import_csv(csv_file, iotdb_datanode_pid, db_path, resource_usage_column_title):
    result_queue = multiprocessing.Queue()
    # 创建进程对象
    import_csv = multiprocessing.Process(target=iotdb_import_csv, args=(csv_file, result_queue))
    get_cpu = multiprocessing.Process(target=get_cpu_usage, args=(iotdb_datanode_pid, ))
    get_mem = multiprocessing.Process(target=get_mem_usage, args=(iotdb_datanode_pid, ))

    # 启动进程a
    import_csv.start()
    # 同时启动进程b和c
    get_cpu.start()
    get_mem.start()

    # 等待进程a结束
    import_csv.join()
    elapsed_time = result_queue.get()

    # 结束进程b和c
    get_cpu.terminate()
    get_mem.terminate()

    # global
    global cpu_usage_list, mem_usage_list
    print(cpu_usage_list, mem_usage_list, sep='\n')
    # 入库
    datatype, encoding, compressor, csv_file_name = str(resource_usage_column_title).split('!')
    insert_query = '''
    INSERT INTO system_monitor (datatype, encoding, compressor, csv_file_name, operate, cpu_used_percent_list, mem_used_percent_list)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    data = (datatype, encoding, compressor, csv_file_name, 'import', str(cpu_usage_list), str(mem_usage_list))
    insert(db_path, insert_query, data)
    # init global list
    cpu_usage_list = []
    mem_usage_list = []

    return elapsed_time


def test_query_all(iotdb_datanode_pid, db_path, resource_usage_column_title):
    result_queue = multiprocessing.Queue()
    # 创建进程对象
    query_all = multiprocessing.Process(target=iotdb_query, args=(result_queue,))
    get_cpu = multiprocessing.Process(target=get_cpu_usage, args=(iotdb_datanode_pid, ))
    get_mem = multiprocessing.Process(target=get_mem_usage, args=(iotdb_datanode_pid, ))

    # 启动进程a
    query_all.start()
    # 同时启动进程b和c
    get_cpu.start()
    get_mem.start()

    # 等待进程a结束
    query_all.join()
    elapsed_time = result_queue.get()

    # 结束进程b和c
    get_cpu.terminate()
    get_mem.terminate()

    # global
    global cpu_usage_list, mem_usage_list
    print(cpu_usage_list, mem_usage_list, sep='\n')
    # 入库
    datatype, encoding, compressor, csv_file_name = str(resource_usage_column_title).split('!')
    insert_query = '''
    INSERT INTO system_monitor (datatype, encoding, compressor, csv_file_name, operate, cpu_used_percent_list, mem_used_percent_list)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    data = (datatype, encoding, compressor, csv_file_name, 'query_all', str(cpu_usage_list), str(mem_usage_list))
    insert(db_path, insert_query, data)
    # init global list
    cpu_usage_list = []
    mem_usage_list = []

    return elapsed_time


def iotdb_operation(csv_file, test_create_sql_list, db_path, resource_usage_column_title, sleep_step=0):
    iotdb_stop(sleep_step)
    iotdb_rm_data(sleep_step)
    iotdb_start(sleep_step)

    # 创建时间序列
    iotdb_exec_by_cli(';'.join(test_create_sql_list), info='创建时间序列', output=False)

    # 拿到datanode id
    iotdb_datanode_pid = iotdb_get_datanode_pid()

    # import csv
    import_elapsed_time = test_import_csv(csv_file, iotdb_datanode_pid, db_path, resource_usage_column_title)

    # flush
    iotdb_exec_by_cli('flush', info='flush')
    # restart
    iotdb_stop()
    iotdb_start()

    # 拿到datanode id
    iotdb_datanode_pid = iotdb_get_datanode_pid()
    # 查询
    query_elapsed_time = test_query_all(iotdb_datanode_pid, db_path, resource_usage_column_title)
    # query_elapsed_time = iotdb_query(info='开始查询')

    return import_elapsed_time, query_elapsed_time


# if __name__ == '__main__':
#     get_mem_usage(30296)
