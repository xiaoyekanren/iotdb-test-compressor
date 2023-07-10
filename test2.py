import multiprocessing
import time


def main():
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

    # 创建进程对象
    process_a_obj = multiprocessing.Process(target=process_a)
    process_b_obj = multiprocessing.Process(target=process_b)
    process_c_obj = multiprocessing.Process(target=process_c)

    # 启动进程a
    process_a_obj.start()

    # 同时启动进程b和c
    process_b_obj.start()
    process_c_obj.start()

    # 等待进程a结束
    process_a_obj.join()

    # 结束进程b和c
    process_b_obj.terminate()
    process_c_obj.terminate()


if __name__ == "__main__":
    main()
