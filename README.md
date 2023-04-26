# iotdb-test-compressor
用于对比iotdb中不同数据类型的序列压缩率，按照数据类型、编码、压缩 的不同, 共130种组合


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

