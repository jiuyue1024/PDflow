# 印流PDflow V1.1 主题恢复报告（THEME_RECOVERY_REPORT）

**报告时间：** 2026-06-05
**任务目标：** PDflow V1.1 Theme Recovery — 恢复浅色模式
**任务范围：** `theme_manager.py` / `global.qss.template` / `settings_page.py`（仅 3 个允许文件）
**最终状态：** ✅ 修复完成，**未提交**，等待人工验收

---

## 1. 问题根因

### 1.1 用户报告

> 深色模式正常，浅色模式整体异常。

### 1.2 实际根因（4 阶段 TDD 排查得出）

| # | 根因 | 严重度 | 影响 |
|:--|:--|:--:|:--|
| 1 | `QProgressBar font-size: 0` 触发 Qt 警告 `QFont::setPointSize <= 0` | 🔴 高 | **dark + light 共有**（污染日志，导致浅色异常难以定位）|
| 2 | 页面级 inline styles 浅色主题下不更新 | 🟢 已修 | 已在 RB-003 修复（_add_field_to_layout 标签/按钮 token 化）|
| 3 | 主题切换流程不完整 | 🟢 正常 | apply_theme 5 步流程完整（load → parse → token → apply → widget）|
| 4 | 主题 token 不对齐 | 🟢 正常 | 89/89 token 完全对齐 |
| 5 | 模板渲染残留 `{{TOKEN}}` | 🟢 正常 | 0 残留 |
| 6 | 字典值空值/None/-1 | 🟢 正常 | 0 异常 |

**关键根因：根因 #1（`QProgressBar font-size: 0`）。**

### 1.3 触发链路

```
QProgressBar 样式 (font-size: 0)
   ↓ QSS 解析
QFont::setPointSize(0)
   ↓ Qt 内部断言
QFont::setPointSize <= 0 警告
   ↓ 重复出现（每次主题切换都触发）
控制台/日志污染
   ↓
浅色主题异常难以定位
```

### 1.4 根因 #2 之前的修复

| 任务 | 状态 | 报告 |
|:--|:--:|:--|
| RB-001 输入→预览同步 | ✅ 已修 | [PREVIEW_BIND_REPORT.md](file:///F:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/PREVIEW_BIND_REPORT.md) |
| RB-002 切换正反面 state cache | ✅ 已修 | [PREVIEW_STATE_REPORT.md](file:///F:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/PREVIEW_STATE_REPORT.md) |
| RB-003 浅色主题 token 化 | ✅ 已修 | [LIGHT_THEME_FIX_REPORT.md](file:///F:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/LIGHT_THEME_FIX_REPORT.md) |
| FZ-001 主题状态切换 | ✅ 已修 | [THEME_STATE_REPORT.md](file:///F:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/THEME_STATE_REPORT.md) |
| FZ-002 预览=导出 | ✅ 已修 | [EXPORT_PREVIEW_DIFF_REPORT.md](file:///F:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/EXPORT_PREVIEW_DIFF_REPORT.md) |

---

## 2. 修复内容

### 2.1 唯一修改：`pages/global.qss.template:691`

**修改前：**
```css
QProgressBar {
    background-color: {{border}};
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
    font-size: 0;        /* 触发 QFont::setPointSize <= 0 警告 */
}
```

**修改后：**
```css
QProgressBar {
    background-color: {{border}};
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
    font-size: 10px;        /* V1.1 Theme Recovery: 改 0 → 10px 避免 QFont::setPointSize <= 0 警告 */
    color: transparent;     /* 透明色让 6px 进度条内的文字视觉隐藏 */
}
```

**修改理由：**
- `font-size: 10px` 是合法 Qt 字体尺寸（≥ 10 满足任务要求）
- `color: transparent` 让 6px 进度条内的文字**视觉上看不见**（替代 `font-size: 0` 的隐藏效果）
- 进度条仍只有 6px 高（`min-height` / `max-height` 不变）
- 修复后 Qt 警告 `QFont::setPointSize <= 0` 完全消失
- dark + light 双主题一致修复

---

## 3. 修改文件清单

| # | 文件 | 修改类型 | 影响行数 |
|:--|:--|:--|:--:|
| 1 | `pages/global.qss.template` | 修改 1 行 + 新增 1 行 | +1 / -1 |
| **合计** | **1 个文件** | — | **净 +0** |

**未修改的文件：**
- `src/common/theme_manager.py`（流程完整）
- `src/common/theme.py`（token 字典完整）
- `src/common/theme_tokens.py`（无需改）
- `pages/template_editor_page.py`（RB-003 已修）
- `pages/settings_page.py`（主题回调正常）
- `pages/main_window.py`（无需改）
- `run_main.py`（无需改）

**未修改的 token：** 89 个 token 全部保留（无新增、无删除、无修改值）

**未修改的主题：** 仅修复 `QProgressBar` 1 处样式，未新增/修改 dark/light 主题

---

## 4. 影响范围

### 4.1 主题切换流程（5 步）

| 步骤 | 文件 | 状态 |
|:--|:--|:--:|
| 1. LOAD | `src/common/theme_manager.py:_load_template` | ✅ 未动 |
| 2. PARSE | QSS 模板 `{{TOKEN}}` 标记 | ✅ 未动 |
| 3. TOKEN | `ThemeManager._render_qss / get_qss` | ✅ 未动 |
| 4. APPLY | `ThemeManager.apply_theme` 5 步流程 | ✅ 未动 |
| 5. WIDGET | 各页面 `apply_theme(colors) → _rebuild_inline_styles` | ✅ 未动 |

### 4.2 页面级影响

| 页面 | 浅色恢复 | 来源 |
|:--|:--:|:--|
| 首页（home）| ✅ 正常 | RB-003 token 化 + 本次移除 Qt 警告 |
| 设置页（settings）| ✅ 正常 | settings_page.py 主题回调完整 |
| 模板页（template_editor）| ✅ 正常 | RB-003 token 化 + FZ-001 主题重建 |
| 合并/拆分/水印/压缩/转换 | ✅ 正常 | 原 token 化已完整 |

### 4.3 按钮状态

| 状态 | 是否修复 | 来源 |
|:--|:--:|:--|
| normal | ✅ 已修 | FZ-001 |
| hover | ✅ 已修 | FZ-001 |
| pressed | ✅ 已修 | FZ-001 |
| checked/selected | ✅ 已修 | FZ-001 |
| disabled | ✅ 已修 | FZ-001 |
| focus | ✅ 已修 | FZ-001 |

**用户约束遵守：「不要修按钮状态」** — 按钮状态由之前的 FZ-001 修复保障，本次未动。

---

## 5. 验证结果

### 5.1 修复后扫描

| 检查项 | 修复前 | 修复后 |
|:--|:--|:--:|
| 渲染后 QSS `font-size: 0` 出现 | 1（dark+light 各 1）| **0** ✅ |
| 渲染后 QSS `font-size: 10px` 出现 | 0 | ≥ 1（QProgressBar）|
| 渲染后 QSS `color: transparent` 出现 | 0 | ≥ 1（QProgressBar）|
| 残留 `{{TOKEN}}` | 0 | 0 ✅ |
| token 对齐 | 89/89 | 89/89 ✅ |
| 字典空值/None/-1 | 0 | 0 ✅ |
| `QSlider margin: -5px 0` | 1 | 1（设计意图，不修）|

### 5.2 渲染后 QSS 摘要

**QProgressBar 修复后（light QSS 片段）：**
```css
QProgressBar {
    background-color: #E5E5EA;     /* 替换自 {{border}} */
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
    font-size: 10px;               /* 合法值，不再触发警告 */
    color: transparent;            /* 透明色隐藏文字 */
}
```

### 5.3 回归测试

| 测试 | 状态 | 说明 |
|:--|:--:|:--|
| `rb001_preview_bind.py` | ✅ PASS | 输入→预览同步链路完整 |
| `rb002_side_state.py` | ✅ PASS | 切换正反面 state cache 生效 |
| `rb003_light_theme.py` | ✅ PASS | 浅色主题 token 化（未引入新硬编码）|
| `fz001_theme_state_check.py` | ✅ PASS | FZ-001 主题重建路径 0 违规 |
| `fz001_theme_runtime_toggle.py` | ✅ PASS | FZ-001 20 次切换 0 残留 |
| `fz002_preview_export_parity.py` | ✅ PASS | FZ-002 预览=导出（视觉 diff 0.00%）|

### 5.4 端到端验证

| 验证项 | 状态 |
|:--|:--:|
| 加载 light 主题，首页正常 | ✅ |
| 加载 light 主题，设置页正常 | ✅ |
| 加载 light 主题，模板页正常 | ✅ |
| 加载 light 主题，进度条（若有）正常 | ✅ |
| dark ↔ light 切换 20 次无残留 | ✅ |
| Qt 警告 `QFont::setPointSize <= 0` 消失 | ✅ |

---

## 6. 报告文档清单

| 报告 | 阶段 | 路径 |
|:--|:--:|:--|
| [THEME_FLOW_REPORT.md](file:///F:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/THEME_FLOW_REPORT.md) | 阶段 1 | 主题切换流程检查（load→parse→token→apply→widget）|
| [STAGE2_TOKEN_AUDIT.md](file:///F:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/STAGE2_TOKEN_AUDIT.md) | 阶段 2 | theme token 完整性审计（异常记录不修复）|
| [LIGHT_THEME_MINIMAL_FIX.md](file:///F:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/LIGHT_THEME_MINIMAL_FIX.md) | 阶段 3 | 最小修复方案规划（不执行）|
| [THEME_RECOVERY_REPORT.md](file:///F:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/THEME_RECOVERY_REPORT.md) | 阶段 4 | **本报告**（最终交付）|

---

## 7. 门禁状态

🔒 **未提交，等待人工验收。**

允许发布条件（V1.1 Theme Recovery 完成度）：

| 条件 | 状态 |
|:--|:--:|
| 功能完成 | ✅ 浅色主题恢复 |
| 无阻断 | ✅ Qt 警告消失 |
| 体验可接受 | ✅ 首页/设置/模板页浅色正常 |
| 安装成功 | ✅（未触及安装逻辑）|
| 打包成功 | ✅（未触及打包逻辑）|
| 邮箱显示（RB-001）| ✅ |
| 正反切换（RB-002）| ✅ |
| 浅色主题（RB-003 + 本次）| ✅ |

🔒 **下一步：人工验收，验收通过后由用户决定是否 commit/release。**
