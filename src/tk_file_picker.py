# tk_file_picker.py — tkinter 原生文件/文件夹选择器（替代 flet FilePicker）
# 用途：Flet 0.84.0 桌面客户端不支持 FilePicker 控件，用 tkinter 原生对话框替代

import os
try:
    import tkinter as tk
    from tkinter import filedialog
    _TK_AVAILABLE = True
except ImportError:
    _TK_AVAILABLE = False


class TkFilePickerFile:
    """模拟 flet.FilePickerFile"""
    def __init__(self, path, name, size):
        self.path = path
        self.name = name
        self.size = size

    def __repr__(self):
        return f"TkFilePickerFile(path={self.path!r}, name={self.name!r}, size={self.size})"


class TkFilePickerResultEvent:
    """模拟 flet FilePicker.on_result 事件对象"""
    def __init__(self, files, path=None):
        self.files = files    # list[TkFilePickerFile]
        self.path = path      # 目录选择时使用


class TkFilePicker:
    """模拟 flet.FilePicker 的 API：
    - file_picker.pick_files(allow_multiple, dialog_title, allowed_extensions)
    - file_picker.on_result = callback
    - file_picker.get_directory_path(dialog_title) → 同步返回路径
    """

    def __init__(self):
        self.on_result = None
        self._allowed_extensions = None
        self._dialog_title = ""
        self._allow_multiple = True

    # ------------------------------------------------------------------
    # pick_files — 打开文件选择对话框
    # ------------------------------------------------------------------
    def pick_files(
        self,
        allowed_extensions=None,
        dialog_title="选择文件",
        allow_multiple=True,
        file_type=None,      # flet.FilePickerFileType — 忽略，用 allowed_extensions
    ):
        if not _TK_AVAILABLE:
            if self.on_result:
                self.on_result(TkFilePickerResultEvent(files=[]))
            return

        self._allowed_extensions = allowed_extensions
        self._dialog_title = dialog_title
        self._allow_multiple = allow_multiple

        # 构建 tkinter filetypes
        if allowed_extensions:
            ext_list = ";".join(["*." + ext.lower() for ext in allowed_extensions])
            filetypes = [("支持的文件", ext_list), ("所有文件", "*.*")]
        else:
            filetypes = [("所有文件", "*.*")]

        root = tk.Tk()
        root.withdraw()
        # 注意：不要在这里设置 topmost，tkinter 对话框本身会正确显示
        # root.attributes('-topmost', True)  # 已移除，避免 Windows 文件对话框异常

        try:
            paths = ()
            if allow_multiple:
                paths = filedialog.askopenfilenames(title=dialog_title, filetypes=filetypes)
            else:
                p = filedialog.askopenfilename(title=dialog_title, filetypes=filetypes)
                if p:
                    paths = (p,)
        finally:
            root.destroy()

        # 构建 FilePickerFile 列表
        files = []
        for fp in paths:
            try:
                name = os.path.basename(fp)
                size = os.path.getsize(fp)
            except OSError:
                name = os.path.basename(fp)
                size = 0
            files.append(TkFilePickerFile(path=fp, name=name, size=size))

        # 触发 on_result 回调
        event = TkFilePickerResultEvent(files=files)
        if self.on_result:
            self.on_result(event)

    # ------------------------------------------------------------------
    # get_directory_path — 打开文件夹选择对话框，同步返回路径
    # ------------------------------------------------------------------
    def get_directory_path(self, dialog_title="选择目录"):
        if not _TK_AVAILABLE:
            return ""

        root = tk.Tk()
        root.withdraw()
        # 注意：不要在这里设置 topmost，避免 Windows 文件对话框异常

        try:
            path = filedialog.askdirectory(title=dialog_title)
            return path if path else ""
        finally:
            root.destroy()

    # ------------------------------------------------------------------
    # save_file — 打开另存为对话框，返回选择的文件路径
    # ------------------------------------------------------------------
    def save_file(self, dialog_title="保存文件", default_name="output.pdf",
                  allowed_extensions=None):
        if not _TK_AVAILABLE:
            return ""

        if allowed_extensions:
            ext_list = ";".join(["*." + ext.lower() for ext in allowed_extensions])
            filetypes = [("支持的文件", ext_list), ("所有文件", "*.*")]
        else:
            filetypes = [("所有文件", "*.*")]

        root = tk.Tk()
        root.withdraw()
        # 注意：不要在这里设置 topmost，避免 Windows 文件对话框异常

        try:
            path = filedialog.asksaveasfilename(
                title=dialog_title,
                initialfile=default_name,
                filetypes=filetypes,
                defaultextension="." + (allowed_extensions[0] if allowed_extensions else "pdf"),
            )
            return path if path else ""
        finally:
            root.destroy()
