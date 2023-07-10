import subprocess
import time

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


def iotdb_get_datanode_pid():
    order = "ps -ef|grep '[i]otdb.DataNode'  | awk {'print $2'}"
    iotdb_datanode_pid = exec_linux_order(order=order, output=True)
    return iotdb_datanode_pid


if __name__ == '__main__':
    time,pid = iotdb_get_datanode_pid()
    print(pid)
