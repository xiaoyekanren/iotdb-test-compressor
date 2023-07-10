import multiprocessing
import time


def process_a():
    # 执行进程a的代码
    print("Process A started")
    time.sleep(3)
    # 进程a的代码逻辑
    print("Process A ended")

def process_b():
    for i in range(1000):
        print(f"Process B started. {i}")
        time.sleep(0.5)

def process_c():
    for i in range(1000):
        print(f"Process C started. {i}")
        time.sleep(0.5)


def main():
    # 创建进程对象
    pro_a = multiprocessing.Process(target=process_a)
    pro_b = multiprocessing.Process(target=process_b)
    pro_c = multiprocessing.Process(target=process_c)

    # 启动进程a
    pro_a.start()

    # 同时启动进程b和c
    pro_b.start()
    pro_c.start()

    # 等待进程a结束
    pro_a.join()

    # 结束进程b和c
    pro_b.terminate()
    pro_c.terminate()


if __name__ == "__main__":
    main()
