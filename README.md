# iotdb-test-compressor
根据iotdb中不同的数据类型、编码、压缩方式，组合出全部可能的时间序列，进行csv导入并查询来判断压缩的性能。  

每条序列进行1列、3列、5列，千万行、百万行、十万行 共计6轮测试。  

将提前准备好的csv文件导入到iotdb，将导入时间看作文件写入时间；flush之后的数据文件夹大小作为压缩后的大小，同时统计tsfile文件数量；查询部分数据作为解压缩的速度。  

对于想要执行测试类型的情况，也就是只测某种数据类型，可以在common.py里面改generate_all_timeseries这个方法，将不需要的行删除/注释掉。  

（未实现）如果预先开启了iotdb-metric并写入prometheus，可以从result.csv中拿到结果，使用generate_img_from_result.py生成图像
2023-04-27:当前共有228种序列


## 参考链接
iotdb的[数据类型、编码方式](https://iotdb.apache.org/zh/UserGuide/Master/Data-Concept/Encoding.html#%E5%9F%BA%E6%9C%AC%E7%BC%96%E7%A0%81%E6%96%B9%E5%BC%8F)，[压缩方式](https://iotdb.apache.org/zh/UserGuide/Master/Data-Concept/Compression.html)

## 软件依赖
### 只生成result结果
python == 3.x  
configparser  
### （未实现）将结果生成图片
prometheus_api_client  
matplotlib  


## 运行方式
```shell
# 前台
python3 main.py
# 后台
nohup python3 -u main.py > nohup.out 2>&1 &
```
## 文件说明
```shell
py_test_iotdb_compress/
├── README.md  # 读我
├── config.ini  # 配置文件 
├── example/
│   ├── csv/  # 压缩测试的样例数据
│   └── demo_result.csv  # 压缩测试的输出结果
├── generate_img/  # 读取结果集的时间信息，从prometheus查询数据
│   ├── generate_bar_from_csv.py  # 将csv的结果生成柱形图，压缩率、数据文件大小、导入速度、全量查询速度
│   ├── generate_bar_from_csv.py  # 将csv的结果生成柱形图，压缩率、数据文件大小、导入速度、全量查询速度
│   └── common.py  # 公共方法

├── performance_test/  # 压缩测试
│   ├── common.py  # 公共方法
│   └── main.py  # 主程序
└── *result.csv  # 由程序创建，用于压缩测试中断后继续
```
### 配置文件说明
[common]存放的是iotdb的路径和csv文件夹的路径，仅用于启动清理iotdb  

[test_loop]是根据准备的csv文件的情况来定的，根据csv的文件夹来判断  

**注：不要试图测试本工具，本工具禁不起测试**  

### csv文件夹
column-1 是说只有一列，column-3 即有3列；row-1000w就是说有1000行，以此类推。  
**如果不按照这个命名方式命名文件夹，肯定有问题**，文件名只要包含类型即可  
注：int32和int64都使用int文件
```shell
csv/
├── column-1
│   ├── row-10000w
│   │   ├── boolean-*.csv
│   │   ├── double-*.csv
│   │   ├── float-*.csv
│   │   ├── int-*.csv
│   │   └── text-*.csv
│   ├── row-1000w
│   ├── row-100w
│   └── row-10w
├── column-3
│   ├── row-10000w
│   ├── row-1000w
│   ├── row-100w
│   └── row-10w
├── column-5
│   ├── ...
```
### result.csv说明
存储输出结果，如果执行一半报错退出，再次启动时就会从这里读取结果，跳过已经执行完毕的部分。  

注：如果不在程序当前目录启动程序的话，至少要确定当前目录里有这个result，否则必然失败。  

## 输出结果
### 结果定义
```shell
info: 当前要干什么
exec: 执行的linux命令
output: 执行linux命令的返回结果
result: 最终想要的结果
```
### 过滤结果
```shell
cat nohup.out | grep result
```
### 结果显示
结果文件可在config.ini -> [common] -> "output_result_log_file=result.csv" 配置，就是只显示输出里面的result列。 

结果如下:   
```shell
result,开始时间,结束时间,类型,编码,压缩方式,压缩率,列,行,导入时间/s,查询时间/s,耗时/s,tsfile大小/kb,tsfile数量
result,start_time/ms,end_time/ms,datatype,encoding,compressor,compression_rate,column,row,import_elapsed_time/s,query_elapsed_time/s,data_size/b,tsfile_count
result,1682574882094,1682574893024,BOOLEAN,PLAIN,UNCOMPRESSED,17.13617,1,10w,2.843,5.369,119399,1
result,1682574919131,1682574939684,BOOLEAN,PLAIN,UNCOMPRESSED,17.13017,1,100w,11.221,6.504,1194387,11
result,1682574965811,1682574975936,BOOLEAN,PLAIN,SNAPPY,171.82138,1,10w,2.856,4.606,11908,1
result,1682575002046,1682575021118,BOOLEAN,PLAIN,SNAPPY,170.63549,1,100w,11.718,4.78,119905,11
result,1682575047234,1682575057464,BOOLEAN,PLAIN,LZ4,257.65558,1,10w,2.844,4.789,7941,1
result,1682575083576,1682575103083,BOOLEAN,PLAIN,LZ4,254.97287,1,100w,11.271,5.523,80244,11
result,1682575129191,1682575139245,BOOLEAN,PLAIN,GZIP,347.55223,1,10w,2.769,4.615,5887,1
result,1682575165350,1682575183803,BOOLEAN,PLAIN,GZIP,344.41033,1,100w,11.063,4.628,59406,11
result,1682575209910,1682575220148,BOOLEAN,PLAIN,ZSTD,482.67068,1,10w,2.912,4.834,4239,1
result,1682575246272,1682575265375,BOOLEAN,PLAIN,ZSTD,477.8597,1,100w,11.227,5.137,42816,11
result,1682575291479,1682575302054,BOOLEAN,PLAIN,LZMA2,409.29006,1,10w,2.95,4.837,4999,1
result,1682575328152,1682575348064,BOOLEAN,PLAIN,LZMA2,404.75659,1,100w,11.609,5.43,50549,11
result,1682575374167,1682575385116,BOOLEAN,RLE,UNCOMPRESSED,61.18913,1,10w,2.824,5.51,33438,1
result,1682575411243,1682575430218,BOOLEAN,RLE,UNCOMPRESSED,61.1169,1,100w,10.948,5.321,334769,11
result,1682575456323,1682575466584,BOOLEAN,RLE,SNAPPY,284.60801,1,10w,2.936,4.684,7189,1
result,1682575492682,1682575512223,BOOLEAN,RLE,SNAPPY,281.97419,1,100w,11.176,5.63,72560,11
result,1682575538330,1682575547785,BOOLEAN,RLE,LZ4,306.15607,1,10w,2.716,4.206,6683,1

...
```

