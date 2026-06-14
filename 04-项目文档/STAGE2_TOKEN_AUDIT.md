# 印流PDflow Theme Token 审计报告（STAGE 2）

**报告时间：** 2026-06-05
**审计目标：** V1.1 Theme Recovery — 阶段 2 token 完整性验证
**审计范围：** `src/common/theme.py`（DARK_COLORS / LIGHT_COLORS）+ `pages/global.qss.template` + 渲染后 QSS
**当前状态：** 🔍 **检查阶段，禁止自动修复**

---

## 1. Token 对齐检查

| 指标 | 数值 |
|:--|:--:|
| DARK_COLORS key 数 | 89 |
| LIGHT_COLORS key 数 | 89 |
| 仅在 DARK 的 key | 0（无遗漏）|
| 仅在 LIGHT 的 key | 0（无遗漏）|
| **key 对齐率** | **100%** ✅ |

**结论：** 89 个 token 在 dark/light 模式完全一一对应，无遗漏。

---

## 2. Token 值异常检查

### 2.1 DARK_COLORS 异常值扫描

| 检查项 | 命中数 | 说明 |
|:--|:--:|:--|
| `None` | 0 | — |
| 空字符串 `''` | 0 | — |
| `'-1'` | 0 | — |
| `'None'` 字符串 | 0 | — |

### 2.2 LIGHT_COLORS 异常值扫描

| 检查项 | 命中数 | 说明 |
|:--|:--:|:--|
| `None` | 0 | — |
| 空字符串 `''` | 0 | — |
| `'-1'` | 0 | — |
| `'None'` 字符串 | 0 | — |

**结论：** 两个 token 字典值**全部有效**。无空值、None、-1。

---

## 3. 渲染后 QSS 异常值扫描

### 3.1 dark QSS 异常

| 异常类型 | 命中数 | 详情 |
|:--|:--:|:--|
| `font-size: 0` | **1** | QProgressBar（line 691 in 模板）|
| `font-size: < 10` | 0 | — |
| 空 background | 0 | — |
| 空 color | 0 | — |
| 空 border | 0 | — |
| 残留 `None` | 0 | — |
| 残留 `-1` | 0 | — |
| `0` 值（width/height/padding/margin/border-width/radius）| 12 | 全部为合法 0（如 `border: none`）|

### 3.2 light QSS 异常

| 异常类型 | 命中数 | 详情 |
|:--|:--:|:--|
| `font-size: 0` | **1** | QProgressBar（同 dark）|
| `font-size: < 10` | 0 | — |
| 空 background | 0 | — |
| 空 color | 0 | — |
| 空 border | 0 | — |
| 残留 `None` | 0 | — |
| 残留 `-1` | 0 | — |
| `0` 值 | 12 | 同 dark |

---

## 4. 模板本身（global.qss.template）异常扫描

| 行号 | 异常 | 模板内容 | 严重度 |
|:--:|:--|:--|:--:|
| 691 | `font-size: 0;` | `QProgressBar { ... font-size: 0; }` | 🔴 **触发 Qt 警告** |
| 771 | `margin: -5px 0;` | `QSlider::handle:horizontal { ... margin: -5px 0; }` | 🟢 设计意图（handle 居中）|

### 4.1 详细分析

#### 问题 1：`QProgressBar font-size: 0`（line 691）

**完整模板片段：**
```css
QProgressBar {
    background-color: {{border}};
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
    font-size: 0;        ← 触发 QFont::setPointSize <= 0
}

QProgressBar::chunk {
    background-color: {{primary}};
    border-radius: 3px;
}
```

**触发路径：**
1. QSS 解析时 `font-size: 0` → `QFont::setPointSize(0)`
2. Qt 内部断言 `setPointSize <= 0` 失败
3. 控制台打印 `QFont::setPointSize <= 0 ...` 警告
4. Qt 6.x 版本会**回退到默认字体**（导致 progress 文字可能显示）

**影响：**
- 🟡 **dark + light 共有**（不区分主题）
- 🟡 仅影响 `QProgressBar`（项目内使用较少）
- 🔴 **Qt 警告污染日志**（干扰其他调试信息）

**根因：**
原作者用 `font-size: 0` 试图隐藏 6px 进度条内的文字。

**修复方向（阶段 4 才执行）：**
- 改用 `color: transparent;` 隐藏文字（保留合法 font-size）
- 或 `font-size: 10; color: transparent;`（满足 ≥10 要求）
- 或直接删除 `font-size: 0;` 行

#### 问题 2：`QSlider margin: -5px 0`（line 771）

**完整模板片段：**
```css
QSlider::handle:horizontal {
    background-color: {{primary}};
    border: none;
    border-radius: 8px;
    width: 16px;
    height: 16px;
    margin: -5px 0;      ← 负 margin
}
```

**分析：**
- handle 16×16 圆形，groove 6px 高
- `-5px` 让 handle 上下各溢出 5px，正好与 groove 居中对齐
- **Qt 滑块标准技巧**（无 bug）
- 不触发任何警告
- **不需要修复**

---

## 5. 全局 `font-size` 完整性

**light QSS 中所有 font-size 值：**

| 范围 | 数量 | 备注 |
|:--|:--:|:--|
| `font-size: 0` | 1 | 🔴 触发警告 |
| `font-size: 1-9` | 0 | ✅ 无 |
| `font-size: 10-15` | 较多 | 正常（按钮、tab、菜单等）|
| `font-size: 16+` | 较少 | 标题 |

**结论：** 唯一异常是 `QProgressBar font-size: 0`，无 font-size < 10 的实例。

---

## 6. 阶段 2 关键发现汇总

| # | 发现 | 严重度 | 是否浅色特有 | 建议阶段 |
|:--|:--|:--:|:--:|:--:|
| 1 | `QProgressBar font-size: 0` | 🔴 高 | 否（dark+light）| 阶段 4 |
| 2 | `QSlider margin: -5px 0` | 🟢 误报 | 否 | 不修 |
| 3 | 89 token 完全对齐 | 🟢 正常 | — | — |
| 4 | 渲染后 0 残留 token | 🟢 正常 | — | — |
| 5 | 字典值 0 异常值 | 🟢 正常 | — | — |
| 6 | 模板 0 处空 background/color/border | 🟢 正常 | — | — |
| 7 | 模板 0 处 font-size < 10 | 🟢 正常 | — | — |

---

## 7. 阶段 2 行动项结论

**只发现 1 个真正需要修复的异常：** `QProgressBar font-size: 0`（dark/light 共有，触发 Qt 警告）。

**浅色主题整体异常的根因不在 token 层，而在：**
- 页面级 inline styles（已在 RB-003 修复，标签/按钮/表格）
- palette 同步
- QProgressBar 警告污染日志

**下一阶段（阶段 3）行动项：**
- 撰写 `LIGHT_THEME_MINIMAL_FIX.md`（仅规划，不执行）
- 列出最小修改点
- 给出恢复浅色主题的最少必要修改清单
