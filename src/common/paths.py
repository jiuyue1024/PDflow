"""
paths.py — 印流PDflow 统一路径管理

开发模式: 基于 __file__ 计算项目根目录
打包模式: 基于 sys._MEIPASS (PyInstaller) 计算资源根目录
用户数据: 统一写入 %APPDATA%/印流PDflow/ (Windows) 或 ~/.pdflow/ (其他)
"""
import os
import sys


def get_resource_root():
    """
    获取资源文件根目录（QSS、图标、模板等只读资源）
    开发模式: 项目根目录
    打包模式: sys._MEIPASS（PyInstaller 临时解压目录）
    """
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_app_root():
    """
    获取应用程序根目录
    开发模式: 项目根目录（与 get_resource_root 相同）
    打包模式: exe 所在目录
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_data_dir():
    """
    获取用户数据目录（config、recent_files 等可写数据）
    持久化存储，不会因更新或重装丢失
    Windows: %APPDATA%/印流PDflow/
    其他: ~/.pdflow/
    """
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
        data_dir = os.path.join(base, '印流PDflow')
    else:
        data_dir = os.path.join(os.path.expanduser('~'), '.pdflow')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def resource_path(*parts):
    """拼接资源文件路径: resource_path('pages', 'global.qss')"""
    return os.path.join(get_resource_root(), *parts)


def data_path(*parts):
    """拼接用户数据路径: data_path('config.json')"""
    return os.path.join(get_data_dir(), *parts)
