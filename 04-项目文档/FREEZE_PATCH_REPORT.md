# 印流PDflow 冻结补丁报告（FREEZE_PATCH_REPORT）

**补丁时间：** 2026-06-05
**补丁范围：** `04-项目文档/FREEZE_REPORT.md`（仅此一文件）
**补丁类型：** 规则追加（新增 1 条禁止 + 1 条允许）
**V1.1 RC 影响：** 无（仅明确规则边界，未改变 V1.1 RC 修复目标）

---

## 1. 新增规则

### 1.1 F-09：禁止修改 `assets/templates/*.json` 的 schema

| 项 | 内容 |
|:--|:--|
| 编号 | **F-09** |
| 类型 | 禁止行为（Hard Block） |
| 触发后果 | 立刻驳回 + 回退 V1.2 规划 |

**约束范围：**

| # | 禁止操作 | 备注 |
|:--|:--|:--|
| 1 | 新增 / 删除 / 重命名 `*.json` 顶层 key（如 `fields` / `styles` / `layout`） | schema 结构层 |
| 2 | 改变字段 `type` 约束（如 `text` → `image_upload`） | 与 F-01 字段锁定互补 |
| 3 | 改变 `group` 分组结构（如 personal / company / contact / back_info 拆分/合并） | 影响 FIELD_GROUPS |
| 4 | 改变 `required` 列表 | 影响空值校验 |
| 5 | 改变字段枚举值（如 `bar_position` 的 left/right/top/bottom/none） | 与 F-04 token 锁定互补 |

**允许的 JSON 操作：**
- 修改已有字段的**默认值**（不破坏 schema）
- 修改**注释**字段（`description` / `sample`）
- 修改**版本号**字段（`version` / `updated_at`）

**与已有规则关系：**
- F-09 是 F-01（禁止新增字段）的**强约束补充**，F-01 防字段层、F-09 防 schema 层
- F-09 是 F-04（禁止新增 token）的**对偶约束**，F-04 防 token 命名、F-09 防 schema 命名

### 1.2 A-06：允许新增测试文件

| 项 | 内容 |
|:--|:--|
| 编号 | **A-06** |
| 类型 | 允许行为（Whitelist） |
| 限制条件 | 走 `test(...)` commit；禁止在测试文件中夹带生产逻辑改动 |

**允许范围：**

| # | 允许操作 | 示例 |
|:--|:--|:--|
| 1 | 新增 `04-项目文档/preview_test/*.py` 验证脚本 | `fz001_theme_runtime_toggle.py` |
| 2 | 新增 `tests/golden/*.png` 截图基线 | 阶段 3 启动后 |
| 3 | 新增 `04-项目文档/*_REPORT.md` 验证报告 | `EXPORT_PREVIEW_DIFF_REPORT.md` |

**硬性禁止（在测试文件中）：**
- ❌ 修改任何 `pages/*.py` / `src/common/*.py` 生产代码
- ❌ 引入新的依赖包（在 `requirements.txt` 之外）
- ❌ 直接写数据库 / 网络副作用
- ❌ 跳过 F-09 schema 约束以"测试"名义

**与已有规则关系：**
- A-06 是 A-04（单元测试 / 回归脚本）的**目录范围收窄**
- A-04 允许"截图基线"，A-06 进一步明确测试文件应放在 `04-项目文档/preview_test/` 而非 `tests/`

---

## 2. 影响范围

### 2.1 对 V1.1 RC 修复工作的回溯影响

| 已有产出物 | 是否在 A-06 范围内 | 结论 |
|:--|:--|:--|
| `04-项目文档/preview_test/fz002_preview_export_parity.py` | ✅ 是（测试文件）| 已合规，无需调整 |
| `04-项目文档/preview_test/fz001_theme_state_check.py` | ✅ 是 | 已合规 |
| `04-项目文档/preview_test/fz001_theme_runtime_toggle.py` | ✅ 是 | 已合规 |
| `04-项目文档/EXPORT_PREVIEW_DIFF_REPORT.md` | ✅ 是（文档）| 已合规 |
| `04-项目文档/THEME_STATE_REPORT.md` | ✅ 是 | 已合规 |
| `pages/template_editor_page.py` 修改 | ❌ 否（生产代码）| 走 A-01/A-02 通道，已合规 |

> **结论：V1.1 RC 修复阶段所有产出物均在 A-06 允许范围内或通过 A-01/A-02 通道。**  
> 补丁 A-06 是对已有实践的**形式化确认**，无回溯修改需求。

### 2.2 对未来工作的影响

| 未来场景 | 适用规则 | 操作 |
|:--|:--|:--|
| 阶段 3 截图回归（tests/golden/）| A-06 | 直接新建 `04-项目文档/preview_test/golden/` 即可 |
| 阶段 4 Token 替换 | A-02 / A-03 | 走 `fix(token-color)` / `fix(token-missing)` commit |
| 阶段 6 RC 门禁 | A-06 | 验证脚本新增无需打破 F-09 |
| 新增 RC bug 修复 | A-01 | 走 `fix(theme)` / `fix(export)` / `fix(theme-state)` 等 |
| template.json 字段补全 | ❌ F-09 禁止 | 必须走 V1.2 规划 |

### 2.3 与 V1.1 RC 修复相关文件的一致性

| 文件 | 当前状态 | F-09 影响 | A-06 影响 |
|:--|:--|:--|:--|
| `assets/templates/business_card.json` | 10 字段 + 4 分组 + 5 type | 未修改 | 无 |
| `assets/templates/notice.json` | 未动 | 未修改 | 无 |
| `assets/templates/product_spec.json` | 未动 | 未修改 | 无 |
| `pages/template_editor_page.py` | 修复后 | 未改 JSON schema | 未引入新测试 |
| `src/common/template_renderer.py` | 修复后 | 未改 JSON schema | 未引入新测试 |
| `src/common/theme_manager.py` | 未动 | 无 | 无 |
| `src/common/theme_tokens.py` | 未动 | 无 | 无 |

---

## 3. 是否影响 RC

### 3.1 影响判定

| 维度 | 影响 | 说明 |
|:--|:--|:--|
| V1.1 RC1 修复目标（FZ-001 / FZ-002）| **无影响** | 规则补丁不改变修复路径与修复结果 |
| V1.1 RC 打包发布 | **无影响** | 仅文档规则追加，不修改任何生产代码或资源 |
| V1.1 RC 验收门禁（阶段 6）| **无影响** | 门禁项不变 |
| V1.2 规划起点 | **正面影响** | F-09 明确 schema 边界，让 V1.2 规划更聚焦"新增字段"而非"调整 schema" |

### 3.2 RC 阶段产出物核对

| 产出物 | 状态 | 与补丁兼容性 |
|:--|:--|:--|
| FREEZE_REPORT.md | ✅ 已更新（F-09 + A-06）| 本补丁主体 |
| EXPORT_PREVIEW_DIFF_REPORT.md | ✅ 已交付 | A-06 合规 |
| THEME_STATE_REPORT.md | ✅ 已交付 | A-06 合规 |
| 3 个验证脚本 | ✅ 已交付 | A-06 合规 |
| 测试截图（6+ 张 PNG）| ✅ 已生成 | A-06 合规 |

### 3.3 收尾确认

| 项 | 状态 |
|:--|:--|
| FREEZE_REPORT.md 规则更新 | ✅ 完成 |
| FREEZE_PATCH_REPORT.md 出具 | ✅ 本报告 |
| V1.1 RC 修复阶段（FZ-001/FZ-002）| ✅ 已完成（见两份修复报告）|
| 用户确认 | ⏳ 等待用户签字确认本补丁 |

---

## 4. 签字栏

| 角色 | 状态 | 备注 |
|:--|:--|:--|
| PM Agent（补丁出具方）| ✅ 已交付 | 本报告 |
| 项目负责人 | ⏳ 待用户确认 | 确认后 FREEZE_REPORT.md 升级为 V2.5 规则版 |
| 开发 Agent | ⏸ 待机 | 后续 commit 必须遵守 F-09 + A-06 |

---

*本补丁由 PM Agent 在不修改任何生产代码/资源的前提下出具，仅追加 1 条禁止 + 1 条允许规则，对 V1.1 RC 修复工作零影响。*
