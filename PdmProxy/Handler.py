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

def parse_pdm_server_info(info):
    return {"op_path": info.get("op_path")[0],
    "pdm_account": info.get("pdm_account")[0],
    "pdm_external_ip": info.get("pdm_external_ip")[0],
    "pdm_intranet_ip": info.get("pdm_intranet_ip")[0],
    "pdm_port": info.get("pdm_port")[0],
    "pdm_pwd": info.get("pdm_pwd")[0],
    }
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
        return self.write(self.do_get(remote_file, file_path, parse_pdm_server_info(argument)))

    def do_get(self, remote_file, file_path, server_info):
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
        ftp = HclFtpLib(ip_addr=server_info["pdm_intranet_ip"],
                        ip_addr_out=server_info["pdm_external_ip"],
                        login_name=server_info["pdm_account"],
                        port=server_info["pdm_port"],
                        pwd=server_info["pdm_pwd"],
                        op_path=server_info["op_path"],
                        )
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
        global rec_size
        rec_size = 0
        remote_file = self.request.arguments.get("remotefile")[0]
        server_info = parse_pdm_server_info(self.request.arguments)
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
        ftp = HclFtpLib(ip_addr=server_info["pdm_intranet_ip"],
                        ip_addr_out=server_info["pdm_external_ip"],
                        login_name=server_info["pdm_account"],
                        port=server_info["pdm_port"],
                        pwd=server_info["pdm_pwd"],
                        op_path=server_info["op_path"],
                        )
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
        return self.write({"result": "1","chose_path":file_path,"file_name":file_name})

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
            opener ="open"
        elif sys.platform == 'win32':
            if direct_open == 'true':
                os.startfile(os.path.join(file_path, file_name))
            else:
                os.startfile(file_path)
            return self.write({"result": "1"})
        else:
            opener = "xdg-open"
        if direct_open:
            new_path = os.path.join(file_path, file_name)
        else:
            new_path = file_path
        subprocess.call([opener, new_path])