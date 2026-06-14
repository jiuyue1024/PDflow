# Architectural Decisions

> 重大架构决策记录（ADR，Architecture Decision Record）。

---

## 决策模板

### 日期：

### 决策：

### 原因：

### 影响：

### 状态：已确定 / 待评估 / 已废弃

---

## 决策记录

### 2026-05

#### 决策：技术栈从 Flet 切换为 PySide6

**原因：** Flet 0.84.0 打包后中文顽固乱码，PySide6 对中文支持更稳定，且 Qt 生态更成熟。

**影响：** 所有历史 Flet 代码归档至 `_旧版归档/`，UI 重做，PDF 后端 API 保留。

**状态：** ✅ 已确定（V2.3）

---

#### 决策：速文创作拆分为「模板排版」+「自由创作」双模式

**原因：** 模板化排版（结构化输出）和自由创作（PDF 内文编辑）属于两类不同使用场景，UI/交互差异大，强行合并增加复杂度。

**影响：** 模板排版作为 V2.3 主线开发，自由创作延后。

**状态：** ✅ 已确定（V2.3）

---

#### 决策：OCR 延后至 V1.2

**原因：** 安装包控制，OCR 引擎（Tesseract / PaddleOCR）会显著增加安装包体积，超出 V1.1 安装包 < 150MB 目标。

**影响：** V1.1 无 OCR 功能。

**状态：** ✅ 已确定（2026-06）

---

#### 决策：引入 `defusedxml` 防护 XML XXE

**原因：** Bandit 安全扫描发现 `xml.etree.ElementTree` 在解析 Word 文档时存在 XXE 风险。

**影响：** `speedwrite_page.py` 改用 `defusedxml.ElementTree.fromstring`，并做兼容回退。

**状态：** ✅ 已确定（2026-05）
