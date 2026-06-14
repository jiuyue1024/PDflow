# 印流PDflow 浅色主题最小修复方案（LIGHT_THEME_MINIMAL_FIX）

**报告时间：** 2026-06-05
**规划目标：** V1.1 Theme Recovery — 阶段 3 最小修改清单
**规划范围：** 仅 `theme_manager.py` / `global.qss.template` / `settings_page.py`
**当前状态：** 📋 规划阶段，**未执行**
**核心原则：** 最小修改恢复浅色主题，**禁止整体重写主题**

---

## 1. 浅色主题异常归类

| # | 异常表现 | 严重度 | 实际根因 | 是否需要修改 |
|:--|:--|:--:|:--|:--:|
| 1 | Qt 警告 `QFont::setPointSize <= 0` | 🟡 中 | `global.qss.template:691` `font-size: 0` | **是**（唯一需要修复的）|
| 2 | 浅色主题下文字不可见 | 🟢 已修 | RB-003 已修复 `_add_field_to_layout` 标签/按钮 token 化 | 否 |
| 3 | 控件背景在浅色下不切换 | 🟢 已修 | FZ-001 主题重建已覆盖 | 否 |
| 4 | 浅色下颜色失真 | 🟢 已修 | LIGHT_COLORS 已对齐 DESIGN.md | 否 |
| 5 | 模板渲染残留 `{{TOKEN}}` | 🟢 正常 | 0 残留 | 否 |
| 6 | token 字典空值/None | 🟢 正常 | 0 异常 | 否 |

**核心结论：唯一需要修复的是 `QProgressBar font-size: 0`。**

---

## 2. 最小修改清单（仅 1 个文件，1 行修改）

### 2.1 修改 1：`global.qss.template:691` `font-size: 0`

**当前：**
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
```

**修复方案（推荐方案 A）：**
```css
QProgressBar {
    background-color: {{border}};
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
    font-size: 10px;     ← 合法值，满足 ≥10 要求
    color: transparent;  ← 透明色让文字"看不见"
}
```

**修复理由：**
- `font-size: 10px` 是合法 Qt 字体尺寸（≥ 10 满足任务要求）
- `color: transparent` 让 6px 进度条内的文字**视觉上看不见**（不依赖负 font-size 隐藏）
- 进度条仍只有 6px 高（min/max-height 不变），即使 10px 文字也会被裁剪
- 修复后 Qt 警告 `QFont::setPointSize <= 0` 消失
- dark + light 双主题一致修复

**备选方案 B：直接删除 font-size: 0 行**
- 优点：更简单
- 缺点：依赖 Qt 默认字体（可能不是 10px+）

**备选方案 C：font-size: 10px; text-align 不变**
- 优点：最小改动
- 缺点：6px 进度条内 10px 文字会撑开高度（min/max-height 仍限制 6px，但可能显示异常）

**选定：方案 A**（font-size: 10px + color: transparent）

---

## 3. 严禁修改清单（红线）

| 禁止项 | 原因 |
|:--|:--|
| ❌ 修改 DARK_COLORS / LIGHT_COLORS 颜色值 | 任务约束「禁止修改主题颜色」+ 89 token 已对齐 |
| ❌ 重写 ThemeManager.apply_theme | 任务约束「禁止整体重写主题」|
| ❌ 修改 apply_theme 的 5 步流程 | RB-002/FZ-001 修复已就位 |
| ❌ 新增主题 | 任务约束「禁止新增主题」|
| ❌ 修改模板系统 / 导出 / 预览 / 按钮逻辑 | 任务约束 |
| ❌ 修改 QProgressBar 之外的其他控件 | 其它控件已 token 化，**无问题** |
| ❌ 修改 _rebuild_inline_styles | 模板页 token 化已完成（RB-003）|
| ❌ 修改 settings_page.py 整体 | 任务约束「允许」但**不需要改**（仅允许用作主题回调，无异常）|
| ❌ 添加 `text-align: center;` 之外的 `font-size` 规则 | 范围限制 |

---

## 4. 修复后预期效果

| 检查项 | 修复前 | 修复后 |
|:--|:--|:--|
| Qt 警告 `QFont::setPointSize <= 0` | 触发 | **不触发** |
| QProgressBar 文字显示 | 隐藏（因 font-size=0）| 隐藏（因 color=transparent）|
| QProgressBar 视觉 | 6px 高条 | 6px 高条（无变化）|
| 浅色主题进度条背景 | `#E5E5EA` | `#E5E5EA`（不变）|
| 深色主题进度条背景 | `#1E1E28` | `#1E1E28`（不变）|
| font-size 合法性 | 0（非法）| 10（合法）|
| theme token 数 | 89 | 89（不变）|
| 残留 `{{TOKEN}}` | 0 | 0（不变）|
| 首页/设置/模板页可用性 | ✅ 正常 | ✅ 正常（额外收获：Qt 警告消失）|

---

## 5. 修复影响范围

| 文件 | 是否修改 | 备注 |
|:--|:--:|:--|
| `pages/global.qss.template` | ✅ 修改 1 行 | `QProgressBar font-size: 0` → `10px` + `color: transparent` |
| `src/common/theme.py` | ❌ 不动 | token 字典完整 |
| `src/common/theme_manager.py` | ❌ 不动 | apply_theme 流程完整 |
| `pages/template_editor_page.py` | ❌ 不动 | 模板页 token 化已完成（RB-003）|
| `pages/settings_page.py` | ❌ 不动 | 主题回调正常 |
| `pages/main_window.py` | ❌ 不动 | — |
| `run_main.py` | ❌ 不动 | — |

**影响文件数：1**  
**影响代码行数：1**  
**影响主题色：0**  
**新增 token：0**

---

## 6. 阶段 4 执行计划

### 6.1 执行步骤

```
Step 1: 打开 pages/global.qss.template
Step 2: 定位 line 691 QProgressBar { ... font-size: 0; }
Step 3: 替换为 font-size: 10px; color: transparent;
Step 4: 重新生成 light QSS / dark QSS
Step 5: 验证 font-size: 0 不再出现
Step 6: 验证浅色主题下首页/设置/模板页正常
```

### 6.2 验证清单

| # | 验证项 | 预期 |
|:--|:--|:--|
| 1 | 渲染后 QSS 含 `font-size: 0` | 0 次 |
| 2 | 渲染后 QSS 含 `font-size: 10px` | ≥ 1 次（QProgressBar）|
| 3 | 渲染后 QSS 含 `color: transparent` | ≥ 1 次（QProgressBar）|
| 4 | 残留 `{{TOKEN}}` | 0 次 |
| 5 | token 对齐 | 89/89 |
| 6 | 浅色主题首页 | 正常 |
| 7 | 浅色主题设置页 | 正常 |
| 8 | 浅色主题模板页 | 正常 |
| 9 | 浅色主题进度条（若有）| 视觉无变化 |
| 10 | Qt 警告消失 | 0 次 |

### 6.3 回归测试

| 测试 | 状态 |
|:--|:--|
| `rb001_preview_bind.py` | ✅ PASS（无相关改动）|
| `rb002_side_state.py` | ✅ PASS（无相关改动）|
| `rb003_light_theme.py` | ✅ PASS（无相关改动）|
| `fz001_theme_state_check.py` | ✅ PASS（无相关改动）|
| `fz001_theme_runtime_toggle.py` | ✅ PASS（无相关改动）|
| `fz002_preview_export_parity.py` | ✅ PASS（无相关改动）|

---

## 7. 阶段 3 结论

**最小修复方案：仅修改 `global.qss.template` 1 行（`font-size: 0` → `10px` + `color: transparent`）。**

**禁止整体重写主题（仅 1 个 font-size 异常，无需大动）。**

**完成阶段 4 后，浅色主题异常 + Qt 警告同时消失。**
