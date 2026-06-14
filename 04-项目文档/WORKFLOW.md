# PDflow 标准开发流程

> PDflow 团队所有开发活动必须严格遵守本流程。
> **核心原则：先有文档，后有代码。**

---

## 一、工作流概览

```
1. 需求 ──→ DECISIONS.md
              ↓
2. 开发 ──→ CHANGELOG.md
              ↓
3. 测试 ──→ TEST_REPORT.md
              ↓
4. 打包 ──→ BUILD_REPORT.md
            PACKAGE_SIZE_REPORT.md
              ↓
5. 发布评审 ──→ RELEASE_GATE.md
              ↓
6. 发布 ──→ RELEASE_NOTES.md
              ↓
7. 复盘 ──→ ROADMAP.md（更新）
            KNOWN_ISSUES.md（更新）
```

---

## 二、各阶段详细规范

### 阶段 1：需求

**输入：** 用户需求、市场反馈、BUG 报告

**活动：**
- PM Agent 收集与梳理需求
- 红线检查（对照《项目总章程》和《DESIGN.md》）
- 任务归类与排序（P0/P1/P2）

**输出文档：** [DECISIONS.md](file:///F:/印流PDflow项目/04-项目文档/DECISIONS.md)

**输出要求：**
- 记录每项重要决策（功能取舍、技术选型、API 设计）
- 每项决策包含：日期、决策、原因、影响、状态

**门禁：** 决策未记录，不得进入开发。

---

### 阶段 2：开发

**输入：** 阶段 1 的决策文档

**活动：**
- 开发 Agent 读取所有必读文档（总章程 + DESIGN.md + 决策）
- 按 PM Agent 指令编码
- 同步更新 CHANGELOG.md

**输出文档：** [CHANGELOG.md](file:///F:/印流PDflow项目/04-项目文档/CHANGELOG.md)

**输出要求：**
- 分类填写：新增 / 优化 / 修复 / 废弃
- 每项写具体功能点，避免空话

**日常节奏：** 每天开发结束前更新 CHANGELOG（不可积累到版本结束）。

**门禁：** CHANGELOG 当日未更新，视为今日无产出。

---

### 阶段 3：测试

**输入：** 阶段 2 完成的代码

**活动：**
- 执行核心回归测试用例
- 记录通过的用例和失败的用例
- 失败用例同步到 KNOWN_ISSUES.md

**输出文档：** [TEST_REPORT.md](file:///F:/印流PDflow项目/04-项目文档/TEST_REPORT.md)

**输出要求：**
- 日期 + 模块 + 通过/失败数
- 末尾的回归测试用例表逐项更新
- 失败用例必须在 KNOWN_ISSUES 记录

**门禁：** 失败用例必须修复或记录到 KNOWN_ISSUES，不得遗留。

---

### 阶段 4：打包

**输入：** 阶段 3 通过的代码

**活动：**
- 执行 PyInstaller 打包
- 记录打包过程的问题
- 分析安装包体积
- 启动时间和内存测试

**输出文档：**
- [BUILD_REPORT.md](file:///F:/印流PDflow项目/04-项目文档/BUILD_REPORT.md)
- [PACKAGE_SIZE_REPORT.md](file:///F:/印流PDflow项目/04-项目文档/PACKAGE_SIZE_REPORT.md)

**输出要求：**
- 打包报告含版本、时间、大小、启动、内存、问题、结果
- 安装包报告含目录大小排行、是否必须、优化方案

**门禁：** 安装包 < 150MB，启动 < 3 秒，否则必须优化后重打包。

---

### 阶段 5：发布评审

**输入：** 阶段 4 完成的安装包

**活动：**
- PM Agent + 项目负责人联合评审
- 逐项检查 [RELEASE_GATE.md](file:///F:/印流PDflow项目/04-项目文档/RELEASE_GATE.md)
- 安全扫描：Bandit + pip-audit 必须零问题
- 核心功能 9 项回归用例必须全通过

**输出文档：** [RELEASE_GATE.md](file:///F:/印流PDflow项目/04-项目文档/RELEASE_GATE.md)

**输出要求：**
- 全部 12 项勾选才能发布
- 门禁状态表追加新行

**门禁：** 任何一项未勾选，禁止进入发布阶段。

---

### 阶段 6：发布

**输入：** 阶段 5 通过的安装包

**活动：**
- 撰写用户视角的发布说明
- 上传到分发渠道
- 通知用户

**输出文档：** [RELEASE_NOTES.md](file:///F:/印流PDflow项目/04-项目文档/RELEASE_NOTES.md)

**输出要求：**
- 给最终用户看，避免技术术语
- 突出新功能亮点
- 明确升级建议

**门禁：** 文档不完整，禁止发布。

---

### 阶段 7：复盘

**输入：** 发布后的用户反馈和运行数据

**活动：**
- 收集用户反馈
- 总结本期得失
- 更新下一期规划
- 整理本期未解决问题

**输出文档：**
- [ROADMAP.md](file:///F:/印流PDflow项目/04-项目文档/ROADMAP.md)（更新）
- [KNOWN_ISSUES.md](file:///F:/印流PDflow项目/04-项目文档/KNOWN_ISSUES.md)（更新）

**输出要求：**
- ROADMAP 调整下一版本的目标
- KNOWN_ISSUES 更新问题状态

**节奏：** **每周一上午**复盘上一周，更新 ROADMAP（每周一必做）。

---

## 三、工作流时间节奏

| 文档 | 更新时机 | 频率 |
|:-----|:---------|:-----|
| **DECISIONS.md** | 做出架构决策时 | 每次决策 |
| **CHANGELOG.md** | **每天开发结束** | **每日** |
| **TEST_REPORT.md** | 回归测试后 | 每次测试 |
| **BUILD_REPORT.md** | 打包后 | 每次打包 |
| **PACKAGE_SIZE_REPORT.md** | 安装包变化时 | 体积变更 |
| **RELEASE_GATE.md** | 发布评审时 | 每次发布 |
| **RELEASE_NOTES.md** | 发布时 | 每次发布 |
| **ROADMAP.md** | **每周一上午** | **每周一** |
| **KNOWN_ISSUES.md** | 发现/修复问题 | 即时 |

---

## 四、规则

### 🚫 禁止

- ❌ **先写代码再补文档** — 文档与代码必须同步
- ❌ **跳过任何阶段** — 阶段之间有严格依赖
- ❌ **CHANGELOG 累积到版本结束** — 必须每日更新
- ❌ **门禁未通过就发布** — RELEASE_GATE 任何一项未勾选禁止发布
- ❌ **删除已废弃决策** — DECISIONS.md 中废弃项标记状态即可，不得删除
- ❌ **跳过 ROADMAP 复盘** — 周一上午必须更新 ROADMAP

### ✅ 要求

- ✅ **每阶段结束必须有报告** — 没有报告视为该阶段未完成
- ✅ **CHANGELOG 每日更新** — 不可跨日累积
- ✅ **ROADMAP 每周一更新** — 即使无变化也要标注"无变化"
- ✅ **KNOWN_ISSUES 即时更新** — 发现即记录，修复即标记
- ✅ **所有日期用 YYYY-MM-DD 格式** — 避免歧义
- ✅ **所有决策不修改历史** — 追加新记录，旧记录标记状态

---

## 五、版本规范

```
Vx.x-alpha  ──→ 内部开发版本，仅团队内测试
    ↓
Vx.x-beta   ──→ 公测版本，外部用户可参与
    ↓
Vx.x-RC     ──→ 候选发布版本，冻结功能
    ↓
Vx.x        ──→ 正式发布版本
```

### 版本号递增规则

- **主版本号（V1 → V2）**：重大架构变更或不向后兼容
- **次版本号（V1.1 → V1.2）**：新增功能或模块
- **修订号（V1.1.1）**：BUG 修复和小优化

### 状态说明

| 状态 | 说明 | 是否可发布 |
|:-----|:-----|:----------:|
| `alpha` | 内部测试，可能有重大 BUG | ❌ |
| `beta` | 公测，可能有少量 BUG | ⚠️ 灰度发布 |
| `RC` | 候选发布，必须稳定 | ⚠️ 准发布 |
| 无后缀 | 正式发布 | ✅ |

---

## 六、文档与阶段对应速查表

| 阶段 | 主输出文档 | 必填字段 |
|:-----|:-----------|:---------|
| 1 需求 | [DECISIONS.md](file:///F:/印流PDflow项目/04-项目文档/DECISIONS.md) | 日期、决策、原因、影响、状态 |
| 2 开发 | [CHANGELOG.md](file:///F:/印流PDflow项目/04-项目文档/CHANGELOG.md) | 新增、优化、修复、废弃 |
| 3 测试 | [TEST_REPORT.md](file:///F:/印流PDflow项目/04-项目文档/TEST_REPORT.md) | 日期、模块、通过、失败 |
| 4 打包 | [BUILD_REPORT.md](file:///F:/印流PDflow项目/04-项目文档/BUILD_REPORT.md) / [PACKAGE_SIZE_REPORT.md](file:///F:/印流PDflow项目/04-项目文档/PACKAGE_SIZE_REPORT.md) | 版本、时间、大小、问题 |
| 5 评审 | [RELEASE_GATE.md](file:///F:/印流PDflow项目/04-项目文档/RELEASE_GATE.md) | 12 项勾选 |
| 6 发布 | [RELEASE_NOTES.md](file:///F:/印流PDflow项目/04-项目文档/RELEASE_NOTES.md) | 版本、日期、新增、修复、建议 |
| 7 复盘 | [ROADMAP.md](file:///F:/印流PDflow项目/04-项目文档/ROADMAP.md) / [KNOWN_ISSUES.md](file:///F:/印流PDflow项目/04-项目文档/KNOWN_ISSUES.md) | 状态、计划修复版本 |

---

## 七、变更记录

| 日期 | 版本 | 变更 |
|:-----|:-----|:-----|
| 2026-06-03 | V1.0 | 工作流文档初始化（基于项目总章程 V2.4） |
