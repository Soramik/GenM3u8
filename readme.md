# GenM3u8

## 功能介绍

把视频自动转换成加密的m3u8文件

## 使用方法

调用`generate_m3u8.py`的`GenM3u8`类，用此类创建一个对象，然后调用`set()`函数设置参数，再调用`start()`函数即可开始转换。

详情请看`demo.py`

注：demo文件夹内使用的视频文件`test_video.mp4`为《魔女之旅》的NCOP，在此仅用于学习测试用。

## demo使用方法

在本目录打开命令行工具，输入一下命令

```commandline
python demo.py
python -m http.server 8000
```

然后使用vlc(或其他支持加密播放m3u8的播放器)打开`output_demo`文件夹下的`demo.m3u8`即可。