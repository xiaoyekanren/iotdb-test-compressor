# coding=utf-8
import os
import sqlite3


def sqlite_execute_statement(db_path, sql):
    # 连接到数据库（如果数据库不存在，则会创建一个新的数据库文件）
    conn = sqlite3.connect(db_path)
    # 创建一个游标对象，用于执行SQL语句
    cursor = conn.cursor()
    # 创建一个表
    cursor.execute(sql)
    # 提交事务
    conn.commit()
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()


def create_db(db_name, result_dir):
    # 连接到一个不存在的数据库文件，如果文件不存在，则会创建一个新的数据库文件
    db_path = os.path.abspath(os.path.join(result_dir, db_name))
    print(f'info: 创建sqlite文件:{db_path}.')
    conn = sqlite3.connect(db_path)
    # 关闭数据库连接
    conn.close()
    return db_path


def init_table(db_path):
    """
    1. check schema
    2. create schema
    """
    # 连接到数据库（如果数据库不存在，则会创建一个新的数据库文件）
    conn = sqlite3.connect(db_path)
    # 创建一个游标对象，用于执行SQL语句
    cursor = conn.cursor()
    # 创建一个表
    cursor.execute('''
        CREATE TABLE records (
        datatype TEXT,
        encoding TEXT,
        compressor TEXT,
        csv_file_name TEXT,
        start_time_in_ms REAL,
        end_time_in_ms REAL,
        import_elapsed_time_in_ms REAL,
        query_elapsed_time_in_ms REAL,
        data_size_in_byte REAL,
        compression_rate REAL,
        tsfile_count INTEGER
)
    ''')
    cursor.execute('''
        CREATE TABLE system_monitor (
        datatype TEXT,
        encoding TEXT,
        compressor TEXT,
        csv_file_name TEXT,
        operate TEXT,
        cpu_used_percent_list TEXT,
        mem_used_percent_list TEXT
    )
        ''')
    # 提交事务
    conn.commit()
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()


def insert(db_path, insert_query, data):
    # 连接到数据库
    conn = sqlite3.connect(db_path)

    # 创建一个游标对象，用于执行SQL语句
    cursor = conn.cursor()

    # 执行插入语句
    cursor.execute(insert_query, data)

    # 提交事务
    conn.commit()

    # 关闭游标和数据库连接
    cursor.close()
    conn.close()