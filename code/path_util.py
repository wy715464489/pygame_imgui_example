
# 常用的路径处理
import os


class PathUtils:
    def __init__(self, path):
        self.path = path

    def get_filename(self):
        """获取文件名（不包含后缀）"""
        return os.path.splitext(os.path.basename(self.path))[0]

    def get_extension(self):
        """获取文件后缀（包含点号）"""
        return os.path.splitext(self.path)[1]

    def get_directory(self):
        """获取文件所在文件夹路径"""
        return os.path.dirname(self.path)

    def is_file(self):
        """检查路径是否是一个文件"""
        return os.path.isfile(self.path)

    def is_directory(self):
        """检查路径是否是一个文件夹"""
        return os.path.isdir(self.path)
