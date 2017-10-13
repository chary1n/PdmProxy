# -*- coding: utf-8 -*-
import platform
import tkFileDialog

import os

import tornado
try:
    import win32con
except ImportError:
    print("1111")

from HclFtpLib import HclFtpLib
try:
    import win32ui
except ImportError:
    print("ss")

from tornado.options import define
import tornado.web

global upload_progress_dict
upload_progress_dict = {}
global send_size
send_size = 0

#下载速度
global rec_size
rec_size = 0

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
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        argument = self.request.arguments
        remote_file = argument.get("remotefile")[0]
        file_path = self.adapt_platform_to_show_filedialog()
        file_path = file_path.decode('gbk')
        if not file_path:
            return self.write({"result": "-1"})
        return self.write(self.do_get(remote_file, file_path))

    def do_get(self, remote_file, file_path):
        global  send_size
        send_size = 0
        new_remote_file = remote_file + os.path.splitext(file_path)[1]
        total_size = float(os.path.getsize(file_path))
        # yield tornado.gen.Task(, args=[5])
        count = 0
        def upload_callback(buf):
            global send_size
            send_size = send_size + len(buf)
            print(u'文件上传中'+ str(round(send_size / total_size * 100, 2)) + '%')
        ftp = HclFtpLib()
        ret = ftp.upload_file(file_path, new_remote_file, callback=upload_callback)
        if ret:
            return {"result": "1",
                               "path": new_remote_file,
                               "choose_file_name": os.path.basename(file_path)}
        else:
            return {"error": "ftp create file error"}

    def adapt_platform_to_show_filedialog(self):
        sysstr = platform.system()
        file_path = ''
        if sysstr == 'Windows':
            dlg = win32ui.CreateFileDialog(1)
            dlg.DoModal()
            file_path = dlg.GetPathName()
        elif sysstr == 'Darwin' or sysstr == 'Linux':  # mac os linux
            file_path = tkFileDialog.askopenfilename()
        print file_path

        return file_path

class GetProgress(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        argument = self.request.arguments
        # remote_file = argument.get("remotefile")[0]
        print(upload_progress_dict or '')
        return self.write(upload_progress_dict or '')

class DownloadFileHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        remote_file = self.request.arguments.get("remotefile")[0]
        sysstr = platform.system()
        file_name = os.path.basename(remote_file)
        file_path = ''
        if sysstr == 'Windows':
            dlg = win32ui.CreateFileDialog(0, "*.py", file_name, 0)
            dlg.DoModal()
            file_path = dlg.GetPathName()
            file_path = file_path.decode('gbk')
            file_path = os.path.split(file_path)[0]#win32UI 选择文件夹的时候  只能带上文件名
        elif sysstr == 'Darwin' or sysstr == 'Linux': # mac os linux
            file_path = tkFileDialog.askdirectory()
        print file_path
        if not file_path:
            return self.write({"result": "2"})
        ftp = HclFtpLib()
        # def download_callback(buf):
        #     global send_size
        #     send_size = send_size + len(buf)
        #     total_size = ftp.ftp.size(file_name)
        #     print(u'文件下载中'+ str(send_size / total_size * 100) + '%')
        total_size = ftp.size(remote_file)
        def download_callback(buf):
            global rec_size
            rec_size = rec_size + len(buf)
            print(u'文件下载中'+ str(round(rec_size * 1.0/ total_size * 100, 2)) + '%')
        ftp.download_file(local_file=os.path.join(file_path, file_name), remote_file=remote_file, cb=download_callback)
        return self.write({"result": "1"})
