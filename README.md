# iotdb-test-compressor
根据iotdb中不同的数据类型、编码、压缩方式，组合出全部可能的时间序列，进行csv导入并查询来判断压缩的性能。  

每条序列进行1列、3列、5列，千万行、百万行、十万行 共计6轮测试。  

将提前准备好的csv文件导入到iotdb，将导入时间看作文件写入时间；flush之后的数据文件夹大小作为压缩后的大小，同时统计tsfile文件数量；查询部分数据作为解压缩的速度。  

## 参考链接
iotdb的[数据类型、编码方式](https://iotdb.apache.org/zh/UserGuide/Master/Data-Concept/Encoding.html#%E5%9F%BA%E6%9C%AC%E7%BC%96%E7%A0%81%E6%96%B9%E5%BC%8F)，[压缩方式](https://iotdb.apache.org/zh/UserGuide/Master/Data-Concept/Compression.html)

## 运行方式
```shell
# 前台
python3 main.py
# 后台
nohup python3 -u main.py > nohup.out 2>&1 &
```
## 文件说明
```shell
.
├── README.md  # 读我
├── main.py  # 主程序
├── common.py  # 公共function
├── config.ini  # 配置文件 
```
### 配置文件说明
[common]存放的是iotdb的路径和csv文件夹的路径，仅用于启动清理iotdb，**不要试图修改data_dir，肯定有问题。**  
[test_loop]是根据准备的csv文件的情况来定的，根据csv的文件夹来判断

### csv文件夹
如果不按照这个命名方式命名文件夹，**肯定有问题**，文件名只要包含类型即可  
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
│   ├── row-10000w
│   ├── row-1000w
│   ├── row-100w
│   └── row-10w
```


## 输出结果
### 结果定义
```shell
exec: 执行的linux命令
output: 执行linux命令的返回结果
result: 最终想要的结果
```
### 过滤出来结果
```shell
cat nohup.out | grep result
```
### 结果显示
结果如下: output,类型,编码,压缩方式,耗时/s,大小/kb,tsfile数量
```shell
result,datatype,encoding,compressor,elapsed_time/s,data_size/kb,tsfile_count
result,BOOLEAN,PLAIN,UNCOMPRESSED,3.384,328,2
result,BOOLEAN,PLAIN,SNAPPY,3.492,228,2
result,BOOLEAN,PLAIN,LZ4,3.24,224,2
result,BOOLEAN,PLAIN,GZIP,3.523,224,2
result,BOOLEAN,PLAIN,ZSTD,3.438,220,2
result,BOOLEAN,RLE,UNCOMPRESSED,3.382,236,2
result,BOOLEAN,RLE,SNAPPY,3.362,224,2
result,BOOLEAN,RLE,LZ4,3.646,224,2
result,BOOLEAN,RLE,GZIP,3.395,220,2
result,BOOLEAN,RLE,ZSTD,3.357,220,2
result,INT32,PLAIN,UNCOMPRESSED,3.356,424,2
...
```

