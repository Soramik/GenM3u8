import os
import subprocess
import time
import datetime
import traceback
import shutil
import random
import logging as log

log.basicConfig(level=log.INFO,
                format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

prj_path = os.path.abspath(os.path.dirname(__file__))
ffmpeg_path = os.path.join(prj_path, r"ffmpeg\bin\ffmpeg.exe")


class GenM3u8:
    _encrypt_url = None               # 存储加密文件的url
    _storage_url = None               # 存储视频文件的url
    _input_video_file_path = None     # 输入的视频文件路径
    _output_folder_path = None        # 输出的文件夹路径
    _output_m3u8_file_name = None     # 输出的m3u8文件

    def __init__(self, hls_time: int = 180):
        """
        GenM3u8类初始化
        :param hls_time: 每个分段视频的时间长度(单位：秒)
        """
        self.hls_time = hls_time
        self.random_str = ''.join(random.sample("zyxwvutsrqponmlkjihgfedcba9876543210", 8))
        self._TEMP_KEYINFO_PATH = os.path.join(prj_path, f'enc_{self.random_str}.keyinfo')  # 临时keyinfo文件
        self._TEMP_ENC_PATH = os.path.join(prj_path, f'encrypt_{self.random_str}.key')  # 临时enc文件

    def set(self, input_video_file_path, encrypt_url, **kwargs):
        """
        设置参数函数
        :param input_video_file_path: 输入的视频文件路径
        :param encrypt_url: 存储加密文件的url
        :param kwargs: storage_url, output_folder_path, output_m3u8_file_name
        :return:
        """
        self._input_video_file_path = input_video_file_path
        if not self._input_video_file_path:
            raise ValueError("你还没有设置必选参数-->输入的视频文件路径[input_video_file_path]")
        input_video_file_name = os.path.splitext(os.path.basename(self._input_video_file_path))[0]
        self._encrypt_url = encrypt_url
        if not self._encrypt_url:
            raise ValueError("你还没有设置必选参数-->存储加密文件的url[encrypt_url]")
        self._output_folder_path = kwargs.get("output_folder_path")
        if not self._output_folder_path:
            self._output_folder_path = os.path.join(prj_path, f"output_{input_video_file_name}")
        self._output_m3u8_file_name = kwargs.get("output_m3u8_file_name")
        if not self._output_m3u8_file_name:
            self._output_m3u8_file_name = input_video_file_name
        if self._output_m3u8_file_name[-5:] != ".m3u8":    # 加后缀
            self._output_m3u8_file_name = self._output_m3u8_file_name + ".m3u8"
        self._storage_url = kwargs.get("storage_url")

    def start(self):
        """
        开始生成m3u8文件和加密ts视频
        :return:
        """
        # 创建输出文件夹
        if not os.path.exists(self._output_folder_path):
            os.mkdir(self._output_folder_path)
        # 生成加密文件
        # self._genEncrypt()
        # 生成视频
        # self._genVideo()
        # 把目标存储的url嵌入m3u8中
        self._genNewM3u8()
        # 把enc文件移动到指定输出目录下
        # shutil.move(self._TEMP_ENC_PATH, os.path.join(self._output_folder_path, "encrypt.key"))
        # 删除临时的keyinfo文件
        # os.remove(self._TEMP_KEYINFO_PATH)

    @staticmethod
    def __runcmd(command):
        """
        运行cmd命令，一般用于运行执行时间较短的命令，3秒超时
        :param command:
        :return:
        """
        ret = subprocess.run(command, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             timeout=3
                             )
        return ret

    @staticmethod
    def __runcmd_wait(cmd):
        """
        运行cmd命令
        :param cmd:
        :return:
        """
        p = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True
                             )
        p.communicate()
        # 清理内存
        if p.stdin:
            p.stdin.close()
        if p.stdout:
            p.stdout.close()
        if p.stderr:
            p.stderr.close()
        try:
            p.kill()    # 杀死子进程，清理内存
        except OSError:
            pass

    @staticmethod
    def __genIV():
        result_str = ""
        for i in range(32):
            result_str += random.choice("1234567890abcdef")
        return result_str

    def _genEncrypt(self):
        """
        生成加密信息
        :return:
        """
        # 参数预处理
        if not self._encrypt_url:
            raise ValueError("你还没有设置必选参数-->存储加密文件的url[encrypt_url]")
        if self._encrypt_url[-1] == "/":
            self._encrypt_url = self._encrypt_url[:-1]

        # 命令
        gen_ssl_cmd = f"openssl rand 16 > {self._TEMP_ENC_PATH}"

        log.info("开始生成加密文件...")
        # 生成ssl
        if os.path.exists(self._TEMP_ENC_PATH):   # 生成前删除已存在的encrypt.key文件
            os.remove(self._TEMP_ENC_PATH)
            time.sleep(1)
        ret_ssl = self.__runcmd(gen_ssl_cmd)
        if ret_ssl.returncode != 0:
            raise Exception("ssl生成失败")
        # 生成IV
        IV = self.__genIV()

        # 生成keyinfo
        if os.path.exists(self._TEMP_KEYINFO_PATH):  # 生成前删除已存在的keyinfo文件
            os.remove(self._TEMP_KEYINFO_PATH)
            time.sleep(1)
        with open(self._TEMP_KEYINFO_PATH, "w", encoding="utf-8") as f:
            f.write(
                f"{self._encrypt_url}/encrypt.key\n"
                f"{self._TEMP_ENC_PATH}\n"
                f"{IV}\n"
            )
        log.info("完成生成加密文件...")
        return

    def _genVideo(self):
        """
        生成视频
        :return:
        """
        # 参数预处理
        if not self._input_video_file_path:
            raise ValueError("你还没有设置必选参数-->输入的视频文件路径[input_video_file_path]")
        input_video_file_name = os.path.splitext(os.path.basename(self._input_video_file_path))[0]
        if not self._output_folder_path:
            self._output_folder_path = os.path.join(prj_path, "output")
        if not self._output_m3u8_file_name:
            self._output_m3u8_file_name = input_video_file_name
        if self._output_m3u8_file_name[-5:] != ".m3u8":    # 加后缀
            self._output_m3u8_file_name = self._output_m3u8_file_name + ".m3u8"

        output_ts_file_type = f"{input_video_file_name}.part%d.ts"
        output_ts_file_path = os.path.join(self._output_folder_path, output_ts_file_type)
        output_m3u8_file_path = os.path.join(self._output_folder_path, self._output_m3u8_file_name)

        gen_cmd = f"{ffmpeg_path} " \
                  f"-y " \
                  f"-i {self._input_video_file_path} " \
                  f"-c:v libx264 " \
                  f"-c:a copy " \
                  f"-f hls " \
                  f"-hls_time {self.hls_time} " \
                  f"-hls_list_size 0 " \
                  f"-hls_key_info_file {self._TEMP_KEYINFO_PATH} " \
                  f"-hls_playlist_type vod " \
                  f"-hls_segment_filename " \
                  f"{output_ts_file_path} " \
                  f"{output_m3u8_file_path}"

        log.info(f"开始【{os.path.basename(self._input_video_file_path)}】的编码...")
        # log.info(gen_cmd)
        self.__runcmd_wait(gen_cmd)   # 运行
        log.info(f"完成【{os.path.basename(self._input_video_file_path)}】的编码...")

    def _genNewM3u8(self):
        """
        生成新的嵌入了url的m3u8
        :return:
        """
        if not self._storage_url:   # 没有设置，不需要嵌入url
            return
        if self._encrypt_url[-1] == "/":
            self._encrypt_url = self._encrypt_url[:-1]

        log.info(f"开始对【{self._output_m3u8_file_name}】嵌入url...")
        m3u8_path = os.path.join(self._output_folder_path, self._output_m3u8_file_name)
        w_lines = []
        with open(m3u8_path, "r", encoding="utf-8") as rf:
            lines = rf.readlines()
            for line in lines:
                if ".part" in line:
                    line = self._storage_url + "/" + line
                w_lines.append(line)
        with open(m3u8_path, "w", encoding="utf-8") as wf:
            wf.writelines(w_lines)
        log.info(f"完成对【{self._output_m3u8_file_name}】嵌入url...")


if __name__ == "__main__":
    enc_url = "http://127.0.0.1:55244/d/Local/"
    input_video_file_p = os.path.abspath("./[SP26].mp4")

    gg = GenM3u8()
    gg.set(
        encrypt_url=enc_url, input_video_file_path=input_video_file_p, storage_url="http://127.0.0.1:55244/d/Local/test"
    )
    gg.start()
