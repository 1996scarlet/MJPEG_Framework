# 基于MJPEG协议的流媒体服务框架

## 功能介绍与原理简要说明

* [基于MJPEG协议的流媒体服务框架说明](./introduction/intro.pdf)

## 性能对比（对照组：H.264+nginx_rtmp+flash）

|                        	| 本架构v1           	| 本架构v2  	| 对照组             	|
|:----------------------:	|--------------------	|-----------	|--------------------	|
| 首帧等待               	| 0.2s~0.5s          	| 小于0.2s  	| 0.5s~1.0s          	|
| 低负载图像延迟         	| 0.5s~1.0s          	| 小于0.5s  	| 1.0s取决于HLS分片  	|
| 高负载图像延迟（4路）  	| 1.0s~2.0s          	| 小于0.5s  	| 2.0s~断开          	|
| 低负载切换延迟         	| 小于0.1s           	| 小于0.2s  	| 1~2个GOP 约为2s    	|
| 高负载切换延迟（4路）  	| 小于0.1s           	| 0.2s~0.5s 	| 5~20个GOP 约为14s  	|
| 带宽占用(1080P)        	| 4.0Mbps * 相机数量 	| 4.5Mbps   	| 2.0Mbps~4.0Mbps    	|
| 前端兼容性             	| HTML5              	| HTML5     	| 需要flash 兼容性差 	|
| 画质对比               	| 清晰 不流畅        	| 清晰 流畅 	| 较清晰 流畅        	|
| 中断续流               	| 强                 	| 强        	| 小中断强 大中断弱  	|
| 网络抖动影响（稳定性） 	| 无影响             	| 无影响    	| 一旦GOP延迟就断开  	|

## 使用方式

> Server

* 可以按照模板`cds_server.py`实现
* 首先初始化memcache和SocketIO

```python
import memcache
mc = memcache.Client(['127.0.0.1:12000'], debug=True) # 注意端口号与启动脚本中一致 IP一般情况下不用修改

app = Flask(__name__)
socketio = SocketIO(app) # 一个针对flask的开源异步通信websocket封装库 包括前端和后端的封装
```

* 注册socketIO的回调响应

```python
# 以注解的形式去修饰函数 需要标明使用的通道名 例如remiria
@socketio.on('connect', namespace='/remiria')
def remiria_connect():
    函数体
```

* 实现上传接受与websocket转发action

```python
socketio.emit('frame_data', {'data': image_data}, namespace='/remiria')
```

* 启动配置

```python
socketio.run(app, debug=True, port=6789, host='0.0.0.0') # 建议使用0.0.0.0 可以同时监听本机所有IP
```

> Client

* 客户端只需要完成图片上传逻辑即可（以Python为例）

```python
if mc.get("current_ip") == ip_address:
    try:
        requests.post("http://127.0.0.1:6789/upload", # 尽量将客户端和服务端部署到一台机器上
                      data=cv2.imencode('.jpg', hkcp.frame())[1].tostring())
    except:
        print(
            colored('=>_<= Do not forget to start cds flask server =>_<=', 'yellow'))
```

> Setup

* 设置要查看的IPC

```python
address_dict = ['10.41.0.208', '10.41.0.210', '10.41.0.211', '10.41.0.212']
```

* 根据桌面环境设置terminal载体（默认使用gnome-terminal 其他发行版可以安装gnome或者对预设命令进行替换）

* 设置memcache参数

```python
memcache_string = 'memcached -d -m 10 -u humanmotion -l 127.0.0.1 -p 12000 -c 256 -P /tmp/memcached.pid' # 如有需要可以额外设置守护进程
```

> WebPage

* 修改`server_ip`为本机局域网或公网IP

```JavaScript
var server_ip = "10.41.0.229";
```

* 需要根据`address_dict`修改按钮的参数 实现点击切换

```JavaScript
<div class="btn-group w-100 h-75" role="group" id="orderBtnGroup">
    <button value="10.41.0.208">机柜01</button>
</div>
```

## 环境要求

> Basic

* `Ubuntu 18.04.X LTS`（或其他发行版本 要求Linux内核版本>=4.14）
* `Python 3`（建议使用3.7版本）
* `pip 3`（sudo apt install python3-pip）
* `opencv-python`（编译Opencv时可选择生成对应版本的whl 不建议通过pip或apt安装）
* `gnome-terminal`（不喜欢gnome可以在`link_start.py`中进行设置）

> FLASK相关依赖

* `Flask`（pip3 install flask）
* `Flask-SocketIO`（pip3 install flask_socketio）
* `schedule`（pip3 install schedule）
* `eventlet`（pip3 install eventlet）
* `xdotool`（sudo apt install xdotool）

> MEMCACHED相关依赖

* `memcached`（sudo apt-get install memcached）
* `memcached-tools`（sudo apt-get install libmemcached-tools）
* `python-memcached`（pip3 install python-memcached）

> Optional（如果使用IPC测试推流 则需要安装以下依赖）

* `Opencv 3/4`（建议下载源码自行编译 版本选择取决于使用的取帧接口）
* `ffmpeg 3/4`（建议下载源码自行编译 版本选择取决于使用的取帧接口）
* `numpy-dev`
* `python3-dev/python-dev`
* `opencv-contrib-python`
* `gcc/g++`
* `libx264-dev`

## 目录结构说明

```shell
.
|-- README.md
|-- cds_server.py #HTTP WEB SERVER
|-- introduction
|-- static
|   |-- cds_core
|   |   |-- HCNetSDKCom #非开源海康sdk shared library
|   |   |   |-- libHCCoreDevCfg.so
|   |   |   |-- libHCPreview.so
|   |   |   |-- libHKCamera_v4.so
|   |   |   |-- libanalyzedata.so
|   |   |   `-- libhcnetsdk.so
|   |   |-- interface.py #接口定义
|   |   |-- link_start.py #启动脚本
|   |   `-- peropero_v1.py #用于模拟数据上传
|   `-- extras #HTML资源
|       |-- css
|       |-- images
|       `-- js
`-- templates #存放Action响应后返回的HTML本体
    `-- lunatic.html
```

## 注意事项（Cautious）

* 编译安装`ffmpeg`前需要设置`./configure --enbale-shared`来防止`opencv`编译过程无法引用动态库导致的`video.so`相关错误
* 编译安装`opencv`时若出现`xfeatures2d`相关错误，需要[重新下载`curl`](https://curl.haxx.se/download.html)并按照如下步骤编译安装
    1. `cd /root/Downloads/curl`
    2. `./configure --with-ssl`
    3. `make`
    4. `sudo make install`
* 在Ubuntu 18上编译安装openCV可以参考[这个链接](https://www.pyimagesearch.com/2018/08/15/how-to-install-opencv-4-on-ubuntu/)