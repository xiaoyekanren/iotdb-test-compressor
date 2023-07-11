# coding=utf-8
import string
import random


def generate_all_timeseries():
    """
    see README.md
    """
    timeseries_list = []
    timeseries_prefix = 'root.g1'
    compressor = [
        'UNCOMPRESSED',
        'SNAPPY',
        'LZ4',
        'GZIP',
        'ZSTD',
        'LZMA2',
    ]
    encoding = {
        'BOOLEAN': ['PLAIN', 'RLE'],
        'INT32': ['PLAIN', 'RLE', 'TS_2DIFF', 'GORILLA', 'FREQ', 'ZIGZAG', 'CHIMP', 'SPRINTZ', 'RLBE'],
        'INT64': ['PLAIN', 'RLE', 'TS_2DIFF', 'GORILLA', 'FREQ', 'ZIGZAG', 'CHIMP', 'SPRINTZ', 'RLBE'],
        'FLOAT': ['PLAIN', 'RLE', 'TS_2DIFF', 'GORILLA', 'FREQ', 'CHIMP', 'SPRINTZ', 'RLBE'],
        'DOUBLE': ['PLAIN', 'RLE', 'TS_2DIFF', 'GORILLA', 'FREQ', 'CHIMP', 'SPRINTZ', 'RLBE'],
        'TEXT': ['PLAIN', 'DICTIONARY'],
    }
    # create timeseries root.g1.int32.zigzag.uncompressed with datatype=INT32,encoding=ZIGZAG,compressor=UNCOMPRESSED;
    for datatype_ in encoding.keys():
        for encoding_ in encoding[datatype_]:
            for compressor_ in compressor:
                ts = f'create timeseries {timeseries_prefix}.{datatype_.lower()}.{str(encoding_).lower()}.{str(compressor_).lower()} with datatype={datatype_.upper()},encoding={str(encoding_).upper()},compressor={str(compressor_).upper()};'
                timeseries_list.append(ts)
    return timeseries_list


def generate_random_code(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


if __name__ == '__main__':
    # # generate_all_timeseries
    # ts_list = generate_all_timeseries()
    # for i in ts_list:
    #     print(i)
    # print(f'info: 一共有{len(ts_list)}种sql组合.')
    # generate_random_code
    print(generate_random_code(10))
