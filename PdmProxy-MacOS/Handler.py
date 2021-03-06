# -*- coding: utf-8 -*-
import json
import logging
import platform
import tkFileDialog

import os

import sys

import time
import tornado

from HclFtpLib import HclFtpLib
# from Main import root
from tornado.options import define
import tornado.web
import global_d
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
_logger.addHandler(ch)

global upload_progress_dict
upload_progress_dict = {}
global send_size
send_size = 0

# 下载速度
global rec_size
rec_size = 0


def parse_pdm_server_info(info):
    return {"op_path": info.get("op_path")[0],
            "pdm_account": info.get("pdm_account")[0],
            "pdm_external_ip": info.get("pdm_external_ip")[0],
            "pdm_intranet_ip": info.get("pdm_intranet_ip")[0],
            "pdm_port": info.get("pdm_port")[0],
            "pdm_pwd": info.get("pdm_pwd")[0],
            }


def show_progress(pre_title, int_progress, float_progress):
    ss = u'\r%s:%s%% ' % (pre_title, str(float_progress))
    root = global_d.get_value('root')
    root.progress['text'] = ss
    root.main_window.update()
    # sys.stdout.write(u'\r%s:%s%% ' % (pre_title, str(float_progress)))
    # sys.stdout.flush()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        respon_json = tornado.escape.json_encode({"result": "1"})
        return self.write({"result": "1"})


class UploadFileHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        argument = self.request.arguments
        remote_file = argument.get("remotefile")[0]
        file_path = self.adapt_platform_to_show_filedialog()
        try:
            file_path = file_path.decode('gbk')
        except UnicodeEncodeError:
            pass
        if not file_path:
            return self.write({"result": "-1"})
        return self.write(
            self.do_get(remote_file, file_path, parse_pdm_server_info(argument)))

    def do_get(self, remote_file, file_path, server_info):
        global send_size
        send_size = 0
        new_remote_file = remote_file + os.path.splitext(file_path)[1]
        total_size = float(os.path.getsize(file_path))
        # yield tornado.gen.Task(, args=[5])
        count = 0

        def upload_callback(buf):
            global send_size
            send_size = send_size + len(buf)
            rounded_progress = round(send_size * 1.0 / total_size * 100, 2)
            int_progress = int(send_size * 1.0 / total_size * 100)
            print(rounded_progress)
            show_progress(u"上传中", int_progress, rounded_progress)
            # print(u'文件上传中'+ str(round(send_size / total_size * 100, 2)) + '%')
        try:
            ftp = HclFtpLib(ip_addr=server_info["pdm_intranet_ip"],
                            ip_addr_out=server_info["pdm_external_ip"],
                            login_name=server_info["pdm_account"],
                            port=server_info["pdm_port"],
                            pwd=server_info["pdm_pwd"],
                            op_path=server_info["op_path"],
                            )
        except:
            return {
                "result": "-1",
                "msg": u"文件服务器连接失败,请检查设置."
            }

        ret = ftp.upload_file(file_path, new_remote_file, callback=upload_callback)
        _logger.info(u"-------******--------上传完成-------******--------")
        show_progress(u"-------******--------上传完成-------******--------", 100, 100)
        if ret:
            return {"result": "1",
                    "path": new_remote_file,
                    "size": total_size,
                    "suffix": os.path.splitext(file_path)[1],
                    "choose_file_name": os.path.basename(file_path)}
        else:
            return {"error": "ftp create file error"}

    def adapt_platform_to_show_filedialog(self):
        sysstr = platform.system()
        file_path = ''
        if sysstr == 'Windows':
            pass
            # dlg = win32ui.CreateFileDialog(1)
            # dlg.DoModal()
            # file_path = dlg.GetPathName()
        elif sysstr == 'Darwin' or sysstr == 'Linux':  # mac os linux
            file_path = tkFileDialog.askopenfilename()
        _logger.info(file_path)

        return file_path


class GetProgress(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        argument = self.request.arguments
        # remote_file = argument.get("remotefile")[0]
        _logger.info(upload_progress_dict or '')
        return self.write(upload_progress_dict or '')


class DownloadFileHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        self.get(args, kwargs)
    def get(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        global rec_size
        rec_size = 0
        remote_file = self.get_argument("remotefile")
        try:
            remote_file = json.loads(remote_file)
        except ValueError:
            pass
        server_info = parse_pdm_server_info(self.request.arguments)
        sysstr = platform.system()
        file_path = ''

        #  选择存储路径
        if sysstr == 'Windows':
                pass
            # dlg = win32ui.CreateFileDialog(0, None, file_name, 0)
            # dlg.DoModal()
            # file_path = dlg.GetPathName()
            # file_path = file_path.decode('gbk')
            # file_path = os.path.split(file_path)[0]  # win32UI 选择文件夹的时候  只能带上文件名

        elif sysstr == 'Darwin' or sysstr == 'Linux':  # mac os linux
            file_path = tkFileDialog.askdirectory()

        #  初始化ftp
        ftp = HclFtpLib(ip_addr=server_info["pdm_intranet_ip"],
                        ip_addr_out=server_info["pdm_external_ip"],
                        login_name=server_info["pdm_account"],
                        port=server_info["pdm_port"],
                        pwd=server_info["pdm_pwd"],
                        op_path=server_info["op_path"],
                        )

        if type(remote_file) == list:
            file_names = remote_file
            file_name = os.path.basename(remote_file[0])
        else:
            file_names = [remote_file]
            file_name = os.path.basename(remote_file)
        _logger.info(file_path)
        if not file_path:
            return self.write({"result": "2"})

        self.download_file(ftp, file_names, file_path)
        # def download_callback(buf):
        #     global send_size
        #     send_size = send_size + len(buf)
        #     total_size = ftp.ftp.size(file_name)
        #     print(u'文件下载中'+ str(send_size / total_size * 100) + '%')

        return self.write(
            {"result": "1", "chose_path": file_path, "file_name": file_name})

    def download_file(self, ftp, remote_files, file_path):
        index = 1
        total = len(remote_files)
        for remote_file in remote_files:
            total_size = ftp.size(remote_file)
            file_name = os.path.basename(remote_file)
            def download_callback(buf):
                global rec_size
                rec_size = rec_size + len(buf)
                rounded_progress = round(rec_size * 1.0 / total_size * 100, 2)
                int_progress = int(rec_size * 1.0 / total_size * 100)
                show_progress(u"下载中", int_progress, rounded_progress)
                # sys.stdout.write(u'\r下载中:[%s%s]%s' % ("*" * int_progress, " " * (100 - int_progress), str(rounded_progress)) + '%')
                # sys.stdout.flush()

            ftp.download_file(local_file=os.path.join(file_path, file_name),
                              remote_file=remote_file, cb=download_callback)
            _logger.info(u"-------******--------(%d/%d)下载完成-------******--------" % (index, total))
            show_progress(u"-------******--------(%d/%d)下载完成-------******--------" % (index, total), 100, 100)
            index = index + 1


class OpenFileBrowserHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        file_path = self.request.arguments.get("file_path")[0]
        file_name = self.request.arguments.get("file_name")[0]
        direct_open = self.request.arguments.get("direct_open")[0]
        import subprocess, sys
        if sys.platform == "darwin":
            opener = "open"
        elif sys.platform == 'win32':
            if direct_open == 'true':
                os.startfile(os.path.join(file_path, file_name))
            else:
                os.startfile(file_path)
            return self.write({"result": "1"})
        else:
            opener = "xdg-open"
        if direct_open == 'true':
            new_path = os.path.join(file_path, file_name)
        else:
            new_path = file_path
        subprocess.call([opener, new_path])
