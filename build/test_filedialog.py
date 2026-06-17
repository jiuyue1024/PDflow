# -*- coding: utf-8 -*-
"""最小化测试：确认 QFileDialog 能否正常弹出"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QFileDialog, QPushButton, QVBoxLayout, QWidget, QLabel

app = QApplication(sys.argv)

w = QWidget()
layout = QVBoxLayout(w)

lbl = QLabel("点击按钮测试文件选择对话框")
layout.addWidget(lbl)

btn = QPushButton("选择PDF文件")
layout.addWidget(btn)

result_lbl = QLabel("结果: 未选择")
layout.addWidget(result_lbl)

def on_click():
    print("[DEBUG] 按钮被点击了")
    files, _ = QFileDialog.getOpenFileNames(
        w,
        "选择PDF",
        "",
        "PDF Files (*.pdf)"
    )
    print(f"[DEBUG] 选择了 {len(files) if files else 0} 个文件")
    if files:
        for f in files:
            print(f"[DEBUG]   {f}")
        result_lbl.setText(f"结果: 选择了 {len(files)} 个文件")
    else:
        result_lbl.setText("结果: 取消选择")

btn.clicked.connect(on_click)

w.setWindowTitle("文件选择测试")
w.resize(400, 200)
w.show()

sys.exit(app.exec())
