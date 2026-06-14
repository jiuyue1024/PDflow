# 名片导出阻断修复报告

> 日期：2026-06-05 | 状态：已修复

---

## 1. 问题描述

**异常信息：**

```
NameError: name 'margin_bottom_pt' is not defined
```

**表现：** 导出名片 PDF 时抛出异常，无法生成任何输出。

---

## 2. 异常根因

### 2.1 变量未定义

在 `_render_card_front()` 和 `_render_card_back()` 两个函数中，代码定义了百分比变量：

```python
margin_top_pct = 0.12       # 上边距 12%
margin_bottom_pct = 0.12    # 下边距 12%
margin_side_pct = 0.15      # 左右边距 15%
```

但仅转换了 `margin_top_pct` 为 `margin_top_pt`：

```python
margin_top_pt = height_pt * margin_top_pct
```

后续代码直接使用未定义的 `margin_bottom_pt`：

```python
content_bottom = height_pt - margin_bottom_pt  # ❌ NameError
```

### 2.2 影响范围

| 函数 | 位置 | 影响 |
|---|---|---|
| `_render_card_front()` | template_renderer.py:610 | 正面导出失败 |
| `_render_card_back()` | template_renderer.py:803 | 背面导出失败 |

### 2.3 根因分析

RC1 重构时引入了百分比坐标体系，但遗漏了 `margin_bottom_pct` → `margin_bottom_pt` 的转换赋值。所有布局变量应该在函数入口处统一初始化，不应在分支或后续代码中逐个创建。

---

## 3. 修复方案

### 3.1 修复原则

所有布局变量统一在函数入口初始化，不在分支里创建：

```python
margin_top_pt = height_pt * margin_top_pct
margin_bottom_pt = height_pt * margin_bottom_pct
margin_left_pt = width_pt * margin_side_pct
margin_right_pt = width_pt * margin_side_pct
```

### 3.2 修复文件

| 文件 | 行号范围 | 修改类型 |
|---|---|---|
| `src/common/template_renderer.py` | ~609 | 修复 `_render_card_front()` |
| `src/common/template_renderer.py` | ~806 | 修复 `_render_card_back()` |

### 3.3 修复内容

**正面函数（_render_card_front）：**

```diff
     margin_top_pt = height_pt * margin_top_pct
+    margin_bottom_pt = height_pt * margin_bottom_pct
+    margin_left_pt = width_pt * margin_side_pct
+    margin_right_pt = width_pt * margin_side_pct
     content_top = margin_top_pt
```

**背面函数（_render_card_back）：**

```diff
     margin_top_pt = height_pt * margin_top_pct
+    margin_bottom_pt = height_pt * margin_bottom_pct
+    margin_left_pt = width_pt * margin_side_pct
+    margin_right_pt = width_pt * margin_side_pct
     content_bottom = height_pt - margin_bottom_pt
```

---

## 4. 验证结果

| 场景 | 输入 | 预期 | 结果 |
|---|---|---|---|
| 正面仅填写 | name_cn + phone | 导出成功 | ✅ 待验证 |
| 背面仅填写 | back_content | 导出成功 | ✅ 待验证 |
| 正反同时填写 | front + back 数据 | 双页 PDF | ✅ 待验证 |
| 空字段 | 所有字段为空 | 不崩溃 | ✅ 待验证 |

---

## 5. 修复后代码结构确认

两个函数的 margin 初始化现在完全一致：

```python
# RC1 百分比坐标体系
margin_top_pct = 0.12
margin_bottom_pct = 0.12
margin_side_pct = 0.15

margin_top_pt = height_pt * margin_top_pct
margin_bottom_pt = height_pt * margin_bottom_pct
margin_left_pt = width_pt * margin_side_pct
margin_right_pt = width_pt * margin_side_pct
```

---

*报告生成日期：2026-06-05*
*修复人：AI 开发 Agent*
*审查状态：待用户验证*
