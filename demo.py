# -*- coding: UTF-8 -*-
"""
@Project  : GenM3u8
@File     : demo.py
@Author   : Sorami
@GitHub   : https://github.com/Soramik
"""
from generate_m3u8 import GenM3u8
import os


def demo():
    enc_url = "http://127.0.0.1:8000/output_demo/"
    input_video_file_p = os.path.abspath("./demo/test_video.mp4")

    # 创建对象
    gg = GenM3u8(
        hls_time=30,      # 每个切片的视频段时间，可不填，不填则为180秒
        print_ffmpeg_flag=True,
    )
    # 设置参数
    gg.set(
        encrypt_url=enc_url,    # 加密文件的url直链 <必填参数>
        input_video_file_path=input_video_file_p,   # 输入的视频文件路径 <必填参数>
        output_folder_path="./output_demo",         # 输出的文件夹，可不填，不填则输出到项目文件夹下的"output_{视频文件名称}"目录下
        output_m3u8_file_name="demo",               # 输出的m3u8文件名称，可不填，不填则沿用视频文件的文件名称
        storage_url="http://127.0.0.1:8000/output_demo/"   # 如果你要把分段的这批ts文件上传到某个url文件目录下，则填写，否则不填
    )
    # 开始
    gg.start()


if __name__ == "__main__":
    demo()
