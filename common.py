# coding=utf-8

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


if __name__ == '__main__':
    for i in generate_all_timeseries():
        print(i)
    print(len(generate_all_timeseries()))
