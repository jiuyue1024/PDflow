# 印流PDflow V1.1 冻结报告（FREEZE_REPORT）

**报告时间：** 2026-06-05
**冻结范围：** 模板排版（template_layout_page / template_editor_page）+ 名片模板（business_card.json）
**冻结版本：** V1.1（开发冻结期 — 进入稳定化流程）
**生效日期：** 自本报告交付起，所有改动必须走 `fix(...)` 类型 commit
**配套文档：** `04-项目文档/RC_CHECKLIST.md`（阶段 6 发布门禁）

---

## 1. 冻结目的

消除 V1.1 RC1 阶段复发的三类高发缺陷：

| 缺陷类型 | 现象 | 根因 |
|:--|:--|:--|
| **预览正常 → 导出异常** | HTML 预览与 PDF 渲染管线不一致 | 预览与导出使用不同 state 分支，未走同一 RenderContext |
| **浅色正常 → 点击变深色** | 主题切换后控件残留旧 inline stylesheet | `apply_theme` 路径未覆盖所有子控件 |
| **改布局 → 字段丢失** | 重排表单/分组时 `self.field_widgets` 失效 | 字段存储结构与 UI 布局耦合 |

后续任何代码变更**必须**在不破坏上述三点的范围内进行。

---

## 2. 冻结对象清单（Baseline Inventory）

### 2.1 字段清单（10 项 — business_card.json）

| # | key | label | type | group | side | 备注 |
|:--|:--|:--|:--|:--|:--|:--|
| 1 | name_cn | 姓名（中文） | text | personal | front | emphasis / H1 |
| 2 | name_en | 姓名（英文） | text | personal | front | Body |
| 3 | title | 职位/头衔 | text | personal | front | Small |
| 4 | company | 公司名称 | text | company | front | emphasis / H2 |
| 5 | phone | 电话 | text | contact | front | Body |
| 6 | email | 邮箱 | text | contact | front | Body |
| 7 | back_logo | 背面 Logo 图片 | image_upload | back_info | back | TPL-05 |
| 8 | back_qr_image | 二维码图片 | image_upload | back_info | back | TPL-05 |
| 9 | back_qr_text | 二维码说明 | text | back_info | back | Small |
| 10 | back_content | 背面简介 | textarea | back_info | back | Body |

**编辑器侧隐式字段**（来自 `FIELD_GROUPS`，不直接渲染但参与回填）：
- back_title、back_slogan（在 back_info 分组下；sample 中已提供）

> **冻结后禁止新增任何字段。** 如确需扩展，需走 V1.2 规划周期。

### 2.2 按钮清单（24 项 — 按功能区分类）

#### 顶部栏
| # | 名称 | 行为 | 冻结策略 |
|:--|:--|:--|:--|
| 1 | `backBtn` | 返回模板网格 | 锁定 |
| 2 | `resetBtn` | 清空当前所有输入 | 锁定 |

#### 底部操作栏
| # | 名称 | 行为 | 冻结策略 |
|:--|:--|:--|:--|
| 3 | `generateBtn` | 调用 `template_renderer.render_business_card()` 生成 PDF | 锁定 |

#### 上传区（TPL-05）
| # | 名称 | 行为 | 冻结策略 |
|:--|:--|:--|:--|
| 4 | `uploadBtn` | 触发 `QFileDialog` 选择图片 | 锁定 |
| 5 | `clearUploadBtn` | 清空已上传图片 | 锁定 |

#### 自定义色块
| # | 名称 | 行为 | 冻结策略 |
|:--|:--|:--|:--|
| 6 | `bgColorBtn` | 自定义背景色 | 锁定 |
| 7 | `clear_bg_btn` | 清除自定义背景色 | 锁定 |
| 8 | `textColorBtn` | 文字色 | 锁定 |
| 9 | `clear_text_btn` | 清除文字色 | 锁定 |
| 10 | `secondaryColorBtn` | 次要文字色 | 锁定 |
| 11 | `clear_secondary_btn` | 清除次要文字色 | 锁定 |
| 12 | `bgImageBtn` | 选择背景图片 | 锁定 |
| 13 | `clear_bg_img_btn` | 清除背景图片 | 锁定 |

#### LOGO 形状
| # | 名称 | 行为 | 冻结策略 |
|:--|:--|:--|:--|
| 14 | `logoShapeSquare` | 方形 LOGO | 锁定 |
| 15 | `logoShapeCircle` | 圆形 LOGO | 锁定 |

#### 样式预设组（radio group，N 个按钮）
| # | 组名 | 按钮数 | 锁定策略 |
|:--|:--|:--|:--|
| 16 | `theme_color` | 8（科技蓝/活力红/森林绿/深邃紫/暖阳橙/高级黑/海洋青/玫瑰金） | 锁定，**禁止新增预设** |
| 17 | `bar_position` | 5（左/右/上/下/无） | 锁定 |
| 18 | `bg_style` | 4（纯白/浅灰/渐变上→下/渐变左→右） | 锁定 |
| 19 | `bg_texture` | 4（无/点阵/网格/斜线） | 锁定 |
| 20 | `font_style` | 仅 notice 模板使用 | 不影响名片冻结 |

> **冻结后禁止新增任何按钮。** 现有按钮的 label、tooltip、顺序、样式保持不变。

### 2.3 主题清单（2 套 — global.qss 兼容）

| 主题 | 定义位置 | 状态 | Token 源 |
|:--|:--|:--|:--|
| **dark** | `DARK_COLORS` in `src/common/theme.py` | ✅ 已冻结 | `theme_tokens.DARK_TOKENS` |
| **light** | `LIGHT_COLORS` in `src/common/theme.py` | ✅ 已冻结 | `theme_tokens.LIGHT_TOKENS` |

**已固化的 Token 体系**（`src/common/theme_tokens.py`）：

| 分层 | Tokens |
|:--|:--|
| 背景 | `bg_primary` / `bg_secondary` / `bg_tertiary` / `bg_quaternary` / `bg_hover` / `bg_pressed` / `bg_disabled` / `bg_overlay` |
| 文字 | `text_primary` / `text_secondary` / `text_tertiary` / `text_quaternary` / `text_muted` / `text_inverse` |
| 边框 | `border_primary` / `border_secondary` / `border_hover` / `border_focus` |
| 强调 | `accent` / `accent_hover` / `accent_pressed` / `accent_subtle` / `accent_subtle_2` / `on_accent` |
| 状态 | `success` / `success_hover` / `warning` / `warning_hover` / `error` / `error_hover` |
| 特殊 | `transparent` / `white` / `black` / `shadow` / `preview_bg` / `preview_fallback` / `preview_border` |

> **冻结后禁止新增主题。** Token 名亦不接受新增（只能复用现有）。

---

## 3. 冻结规则

### 3.1 禁止行为（Hard Block）

| # | 行为 | 触发后果 |
|:--|:--|:--|
| **F-01** | 新增字段 | 立刻驳回 + 回退 V1.2 规划 |
| **F-02** | 新增按钮 | 立刻驳回 |
| **F-03** | 新增主题 | 立刻驳回 |
| **F-04** | 新增 token 名 | 立刻驳回（必须复用现有 token） |
| **F-05** | 修改 `template_renderer.render_business_card()` 签名 | 立刻驳回 |
| **F-06** | 拆分 `self.field_widgets` 字段存储结构 | 立刻驳回（详见阶段 2 CardModel 替代） |
| **F-07** | 引用 `_旧版归档/` 任何代码 | 立刻驳回 |
| **F-08** | 在 src/ 写 `import flet` | 立刻驳回 |
| **F-09** | 修改 `assets/templates/*.json` 的 schema（字段定义、type 约束、group 结构、required 列表） | 立刻驳回 + 回退 V1.2 规划 |

### 3.2 允许行为（Whitelist）

| # | 行为 | 限制条件 |
|:--|:--|:--|
| **A-01** | 修复 Bug（影响正确性/性能/视觉） | 走 `fix(...)` commit，≤3 文件、≤1 目标 |
| **A-02** | 重构同一模块内的硬编码颜色为 token | 走 `fix(token-color)` commit |
| **A-03** | 补全缺失的 token 映射（仅复用现有 token 名） | 走 `fix(token-missing)` commit |
| **A-04** | 单元测试 / 回归脚本 / 截图基线 | 走 `test(...)` commit |
| **A-05** | 文档同步更新（V1.1 报告、CODE_REVIEW 等） | 走 `docs(...)` commit |
| **A-06** | 新增测试文件（`04-项目文档/preview_test/*.py`） | 走 `test(...)` commit；**禁止在新增测试文件中夹带生产逻辑改动** |

### 3.3 Commit 命名规范（小步提交约束）

```
<type>(<scope>): <subject>
```

| type | 用途 | 示例 |
|:--|:--|:--|
| `fix` | 修复已有问题 | `fix(card-theme): 修复浅色模式残留 inline stylesheet` |
| `fix` | 重构同模块 | `fix(card-export): 统一导出管线为 RenderContext` |
| `test` | 新增/调整测试 | `test(card): 补充 golden screenshot 基线` |
| `docs` | 文档同步 | `docs(freeze): 更新 FREEZE_REPORT.md 阶段 3 完成` |

**小步提交硬性规则：**
- 每次 commit ≤ 3 个文件
- 每次 commit ≤ 1 个目标（layout / theme / export / preview 不能同 commit）
- commit message 中必须明确写出修复的字段 key 或按钮名

---

## 4. 已知问题登记（Phase 1 锁定，不再新增）

| # | 编号 | 现象 | 根因（已识别） | 归属阶段 | 优先级 |
|:--|:--|:--|:--|:--|:--|
| 1 | FZ-001 | 浅色模式点击触发变深 | `apply_theme` 后 `_reload_qss` 范围不全 | 阶段 2 + 4 | 🔴 P0 |
| 2 | FZ-002 | 预览正常导出异常 | HTML 预览与 PyMuPDF 渲染分叉 | 阶段 2 | 🔴 P0 |
| 3 | FZ-003 | 改布局字段丢失 | `field_widgets` 与布局耦合 | 阶段 2 | 🔴 P0 |
| 4 | FZ-004 | 装饰条位置有 5 种但实际渲染偶尔错位 | CSS 模板拼接顺序依赖 | 阶段 2 | 🟡 P1 |
| 5 | FZ-005 | 主题色预设切换 hover 状态未同步 | radio group 状态机缺失 | 阶段 2 | 🟡 P1 |
| 6 | FZ-006 | 自定义背景色与 bg_style 互斥逻辑边界 | 二者 CSS 拼接顺序 | 阶段 4 | 🟠 P2 |
| 7 | FZ-007 | 启动后无最近编辑恢复入口 | 草稿持久化未做 | 阶段 4 | 🟠 P2 |

> 阶段 1 起**冻结问题清单**。新问题发现后必须先**追加到本表**才能进入修复。

---

## 5. 阶段产出物映射

| 阶段 | 目标 | 产出 | 状态 |
|:--|:--|:--|:--|
| **1** | 冻结 | `FREEZE_REPORT.md`（本文件） | ✅ 本次交付 |
| **2** | CardModel 单一数据源 | `pages/card_model.py`（新建） + 编辑器 / 渲染器重构 | ⏳ 待启动 |
| **3** | 截图回归 | `tests/golden/preview.png` / `tests/golden/export.png` | ⏳ 待启动 |
| **4** | 视觉 Token | 移除所有 `color:#XXXXXX` 硬编码 | ⏳ 待启动 |
| **5** | 小步提交 | 严格执行 commit 规则 | 🔁 持续 |
| **6** | 发布门禁 | `RC_CHECKLIST.md` 5/5 PASS | ⏳ 待启动 |

---

## 6. 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|:--|:--|:--|:--|
| 阶段 2 CardModel 重构破坏 V1.1 RC1 已修复点 | 中 | 高 | 走 `fix(card-refactor)` 单 commit + 阶段 3 截图回归拦截 |
| 阶段 4 Token 替换不彻底 | 高 | 中 | 引入 lint 规则：禁止 `pages/` 出现 `#XXXXXX` 字面量 |
| 阶段 5 提交粒度过大 | 中 | 中 | commit message 模板强制校验 |
| 阶段 6 门禁项遗漏 | 中 | 高 | 5 项门禁全部 PASS 才允许打包 |

---

## 7. 签字栏

| 角色 | 状态 | 备注 |
|:--|:--|:--|
| 项目负责人 | ⏳ 待用户确认本报告 | 用户确认后阶段 1 正式生效 |
| PM Agent | ✅ 本报告交付 | 阶段 2-6 待用户下达 `进入阶段 N` 指令后启动 |
| 开发 Agent | ⏸ 待机 | 仅在用户授权后开始 `fix(...)` 类型 commit |

---

*本报告由 PM Agent 出具，所有改动需用户确认签字。后续阶段启动需用户单独下达指令。*
