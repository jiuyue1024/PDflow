# 印流PDflow

设计师专用的轻量级 PDF 工具箱 — 合并拆分、压缩、格式转换、水印、模板排版，一站式解决。

> 纯本地处理，无需联网，隐私安全。

---

## ✨ 主要功能

| 功能 | 说明 | 状态 |
| :--- | :--- | :--- |
| **合并拆分** | 多个 PDF 合并为一个，或按页/范围拆分为独立文件 | ✅ 完成 |
| **压缩优化** | 三档压缩质量可选（高/中/低），有效减小文件体积 | ✅ 完成 |
| **格式转换** | PDF ↔ 图片 / Word / Excel / PPT，支持批量处理 | ✅ 完成 |
| **水印处理** | 文字水印或图片水印，支持透明度、旋转角度、平铺/居中 | ✅ 完成 |
| **模板排版** | 名片、合同、发票、报告等预设模板，表单输入 + 实时预览 + PDF 生成 | ✅ 完成 |
| **PDF → Excel** | 标准模式 + 高级 OCR 模式（RapidOCR），支持图片保真嵌入 | ✅ 完成 |
| **自由创作** | 轻量级文本编辑器（通过设置页「开发者模式」开启） | 📋 规划中 |

---

## 📸 界面截图

<img width="1875" height="1014" alt="settings-page" src="https://github.com/user-attachments/assets/5e0b336f-956b-4201-9806-8d872b975559" />

<img width="1875" height="1080" alt="hero-main" src="https://github.com/user-attachments/assets/3c443d08-6541-4520-b594-f280542173eb" />

<img width="1920" height="1020" alt="template-editor" src="https://github.com/user-attachments/assets/d9a2d7d4-c314-46e0-8823-8691e8fac2e2" />

<img width="1920" height="1020" alt="pdf-convert" src="https://github.com/user-attachments/assets/b1d05403-a91f-4976-8e76-d6d9bf9157fc" />

---

## 📥 下载与安装

1. 访问 [Releases 页面](https://github.com/jiuyue1024/PDflow/releases)
2. 下载 `PDFlow_V1.2_Setup.exe`（211 MB）
3. 双击运行安装向导，选择安装路径
4. 勾选「创建桌面快捷方式」，安装完成后自动启动

**无需安装 Python 或任何依赖环境，安装即用。**

---

## 💻 系统要求

| 项目 | 要求 |
| :--- | :--- |
| 操作系统 | Windows 10 / 11（64 位） |
| 内存 | 建议 4GB 以上 |
| 磁盘空间 | 安装后约 500MB |

---

## 🛠️ 技术栈

| 层级 | 技术 |
| :--- | :--- |
| UI 框架 | PySide6（Qt 6） |
| PDF 引擎 | PyMuPDF（fitz） |
| OCR 引擎 | RapidOCR |
| 语言 | Python 3.12+ |
| 打包工具 | PyInstaller |
| 安装程序 | Inno Setup 6 |

---

## 🔒 隐私说明

本软件为**纯单机工具**，所有文件处理均在本地完成。不收集任何个人信息、无需注册登录、不联网上传文件。你的 PDF 文件自始至终只存在于你自己的电脑上。

---

## 🚀 版本路线图

| 版本 | 内容 | 状态 |
| :--- | :--- | :--- |
| **V1.0** | 工具箱发布（合并/压缩/转换/水印） | ✅ 已发布 |
| **V1.1** | PDF → Excel 引擎升级（PaddleOCR → RapidOCR） | ✅ 已发布 |
| **V1.2** | 模板排版系统 + 深浅色主题 + Inno Setup 安装包 | ✅ 已发布 |
| **V2.0** | 设计排版模块全面升级，开放版式自定义 | 🚀 开发中 |
| **V3.0** | AI 排版助手、云端增值服务 | 📋 规划中 |

---

## 📧 反馈与联系

如有问题或建议，请在 [Issues](https://github.com/jiuyue1024/PDflow/issues) 中提交。
