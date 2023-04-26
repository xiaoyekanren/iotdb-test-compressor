# coding=utf-8

def generate_all_timeseries():
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
                ts = f'create timeseries {timeseries_prefix}.{datatype_.lower()}.{str(encoding_).lower()}.{str(compressor_).lower()} with datatype={datatype_},encoding={encoding_},compressor={compressor_};'
                timeseries_list.append(ts)
    return timeseries_list


