# iotdb-test-compressor
根据iotdb中不同的数据类型、编码、压缩方式，组合出全部可能的时间序列（228种），进行csv导入并查询来判断压缩的性能。(20230427:IoTDB V1.2.0 支持228种序列)  

1. 将提前准备好的csv文件导入到iotdb，将导入时间看作文件写入时间；
2. flush之后的数据文件夹大小作为压缩后的大小
3. 同时统计tsfile文件数量；查询全量数据作为解压缩的速度。  
4. 在2,3执行的时候，定时取datanode进程的CPU、内存的使用率

对于想要执行测试类型的情况，也就是只测某种数据类型，可以在common.py里面改generate_all_timeseries这个函数，将不需要的行删除/注释掉。  
**注：不要试图测试本工具，本工具禁不起测试**  

## 参考链接
(20230712,官网不再提供未发布版本链接，需要等待1.2.0开源版发布)  
~~iotdb的[数据类型、编码方式](https://iotdb.apache.org/zh/UserGuide/Master/Data-Concept/Encoding.html#%E5%9F%BA%E6%9C%AC%E7%BC%96%E7%A0%81%E6%96%B9%E5%BC%8F)，[压缩方式](https://iotdb.apache.org/zh/UserGuide/Master/Data-Concept/Compression.html)~~

## 当前模块
1. performance_test  # 真正的测试过程
2. generate_img
   1. ~~demo_plt_plot.py~~
   2. ~~demo_query_from_prometheus.py~~
   3. generate_bar_from_csv.py  # 将csv的结果生成柱形图

## 软件依赖
### performance_test
* python == 3.x  
    * configparser  # 读取配置文件
    * multiprocessing  # 获取cpu、mem使用率
    * psutil  # 执行linux命令

### 将结果生成图片
* python == 3.x  
    * prometheus_api_client  # 读取prometheus
    * matplotlib  # 画图

## 运行方式
```shell
# 前台
python3 performance_test/main.py
# 后台, 注意-u必须
nohup python3 -u performance_test/main.py > nohup.out 2>&1 &
```
## 文件说明
```shell
py_test_iotdb_compress/
├── README.md  # 读我
├── config.ini  # 配置文件 
├── performance_test/  # 压缩测试
│   ├── main.py  # 主程序
│   ├── order.py  # linux相关的函数
│   ├── sql.py  # 操作sqlite相关的函数
│   └── common.py  # 公共函数
├── generate_img/  # 读取结果集的时间信息，从prometheus查询数据
│   ├── generate_bar_from_csv.py  # 将csv的结果生成柱形图，压缩率、数据文件大小、导入速度、全量查询速度
│   ├── demo_query_from_prometheus.py  # 未完成：读取prometheus，生成图片
│   ├── demo_plt_plot.py  # 未开始：生成折线图的demo
│   └── common.py  # 公共函数
├── example/
│   ├── csv/  # 压缩测试的样例数据
│   ├── img_bar/  # 读csv生成柱形图的样例数据
│   └── demo_result.csv  # 压缩测试的输出结果
└── results # 存放sqlite文件夹, *如果报错，那么要手动创建该文件夹
    ├── results.csv  # 存储结果的csv
    └── results.db  # 存储结果的db
```

### 配置文件说明
```ini
[connect]  # iotdb的连接方式
[common]  # iotdb的路径和csv文件夹的路径，仅用于启动清理iotdb  
[results]  # 输出结果的参数
[import]  # iotdb import csv的参数
[generate_img]  # 生成图片的相关参数
```

### 数据集(csv)文件夹
csv目录下是由6种类型的大写字母组成的文件夹，每个文件夹下放的是对应的类型的csv文件
```shell
csv/
├── BOOLEAN
│   ├── file-1.csv
│   └── file-*.csv
├── INT32
│   ├── file-1.csv
│   └── file-*.csv
├── INT64
│   ├── file-1.csv
│   └── file-*.csv
├── FLOAT
│   ├── file-1.csv
│   └── file-*.csv
├── DOUBLE
│   ├── file-1.csv
│   └── file-*.csv
└── TEXT
    ├── file-1.csv
    └── file-*.csv
```
### result.csv说明
存储输出结果，如果执行一半报错退出，再次启动时就会从这里读取结果，跳过已经执行完毕的部分。  

注：如果不在程序当前目录启动程序的话，至少要确定当前目录里有这个result，否则必然失败。  

## 输出结果
建议nohup启动，这样有什么问题也方便调整。
### 结果定义
```shell
info: 当前要干什么
exec: 执行的linux命令
output: 执行linux命令的返回结果
result: 最终想要的结果
```
### 结果显示
结果文件可在config.ini -> [results] -> "output_result_csv_name=result.csv" 配置，就是只显示输出里面的result列。 

结果如下:   
```shell
result,datatype,encoding,compressor,csv_file_name,start_time_in_ms,end_time_in_ms,import_elapsed_time_in_ms,query_elapsed_time_in_ms,data_size_in_byte,compression_rate,tsfile_count
结果,类型,编码,压缩方式,被测试文件名,测试时间,结束时间,导入耗时ms,查询耗时ms,数据大小byte,压缩率,tsfile数量
result,INT32,PLAIN,GZIP,int-sg0-line3-100w0_0.csv,1689142051206.4468,1689142178086.4812,15632.64,57365.25,237800,115.85411,7
result,INT32,PLAIN,ZSTD,int-sg0-line5-100w0_0.csv,1689142191183.3918,1689142324688.8877,17522.64,62185.98,279635,128.1677,7
result,INT32,PLAIN,ZSTD,int-sg0-line3-100w0_0.csv,1689142337779.2312,1689142470201.6458,16328.27,62004.46,168587,163.41774,7
result,INT32,PLAIN,LZMA2,int-sg0-line5-100w0_0.csv,1689142483319.4924,1689142618817.041,18505.84,62170.37,336668,106.45556,7
result,INT32,PLAIN,LZMA2,int-sg0-line3-100w0_0.csv,1689142631902.2124,1689142764639.8115,16376.27,62189.05,202916,135.77101,7
result,INT32,RLE,UNCOMPRESSED,int-sg0-line5-100w0_0.csv,1689142777732.1135,1689142911859.4688,17820.13,62202.39,7863236,4.55795,7
result,INT32,RLE,UNCOMPRESSED,int-sg0-line3-100w0_0.csv,1689142924961.645,1689143056666.6707,15561.22,62129.83,4718730,5.83846,7
result,INT32,RLE,SNAPPY,int-sg0-line5-100w0_0.csv,1689143069763.5662,1689143203562.2036,17720.92,62123.39,854922,41.92216,7
result,INT32,RLE,SNAPPY,int-sg0-line3-100w0_0.csv,1689143216672.269,1689143345181.975,15733.38,59037.92,513723,53.62833,7
...

```

## 废弃项
1. 如果预先开启了iotdb-metric并写入prometheus，可以从result.csv中拿到结果，使用generate_img_from_result.py生成图像  
    > 改为实时统计cpu 内存使用率，存sqlite
