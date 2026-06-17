# 帖子库 · post_002

> 类型：开发日志
> 日期：2026-06-14
> 状态：待发布
> 截图依赖：225MB 终端截图、排除前后对比图（见 screenshot/采集清单.md）
> 灵感来源：ideas.md — 安装包 799MB→225MB 优化过程

---

## 正文（完整版）

### 标题

独立开发第 15 天：
把 AI PDF 软件安装包从 799MB 压到 225MB

### 背景

PDflow V1.1 功能全部跑通了。模板排版、主题切换、PDF 工具箱——

然后第一次打包：**799MB**。

一个 PDF 工具 799MB，这件事本身就是个帖子。

上一帖（post_001）讲的是"问题被发现"，这一帖讲"问题怎么解决的"。

### 遇到的问题

核心问题只有一个：**安装了 PySide6 WebEngine，但从没用过它。**

PySide6 分多个模块包。PDflow 不需要打开网页、不需要渲染 HTML、不需要 Web 引擎。但打包时，PyInstaller 默认把所有已安装的 PySide6 模块全打进去——包括 QtWebEngine，一个 350MB+ 的庞然大物。

### 怎么定位

定位过程不复杂，但需要耐心：

```
1. 查看打包日志 → 发现多个 QtWebEngine 相关 dll
2. 搜索代码 → 确认没有任何 from PySide6.QtWebEngine 引用
3. 搜索 .ui 文件 → 确认没有 QWebEngineView 控件
4. 确认后 → 在打包 spec 中排除
```

关键不是技术有多难，而是**你敢不敢排除一个"已安装"的依赖**。

### 最终结果

```
排除 WebEngine 前：   799MB
排除 WebEngine 后：   225MB
减重：                72%
```

225MB 还没到目标（150MB），但方向验证了：
**不是所有依赖都需要打包。**

### 截图

![排除前后对比图](../screenshots/post_002/size_comparison.png)
![225MB 结果截图](../screenshots/post_002/result_225mb.png)

### 一句反思

> 很多时候问题不在你写了什么，而在你带了什么。

有人也做桌面软件吗？你们最大的依赖体积来源是什么？
评论区聊聊，我准备把下一步"225MB 压到 150MB"也整理出来。

---

## 多平台改写

### 小红书版（≤ 300 字）

**标题：**
装了但没用，350MB 白白打包

**正文：**
做 PDF 工具到 beta，第一次打包 799MB。
排查发现：PySide6.WebEngine 占了 350MB。
但我的软件根本不打开网页。

确认代码一个 WebEngine 引用都没有之后——
在打包配置里排除掉。

799MB → 225MB。
减了 72%。

不是所有依赖都需要打包。
很多时候问题不在你写了什么，而在你带了什么。

做桌面软件的朋友，你们最大的体积负担是什么？

#独立开发 #桌面软件 #Python #PySide6

---

### Nodeloc 版（500-800 字）

**标题：**
PySide6 安装包 799MB → 225MB，排除 QtWebEngine 就减了 72%

**正文：**

PDflow V1.1 做完打包，799MB。

排查过程：
1. 先看打包日志，定位体积最大的 dll 群
2. 锁定 PySide6/QtWebEngine 相关模块 ~350MB
3. 全局搜索代码：无 `from PySide6.QtWebEngine` 引用
4. 搜索 .ui：无 QWebEngineView 控件
5. 确认：WebEngine 是早期评估时装的，后来没用上

修复：在 PyInstaller spec 中排除整个 `PySide6/QtWebEngine*` 树。

```
排除前：799MB
排除后：225MB
```

几行排除配置，砍掉 72%。

**反思：**
打包这件事，反直觉的地方在于——你安装的依赖只要用不上，就是负债。
PySide6 的模块化做得很好，按需导入是可行的。但前提是你知道自己在用什么。

后续目标：225MB → ≤150MB（字体子集化 + onedir 模式）
有人也踩过类似的打包坑吗？

---

### 微信公众号版（1500-2000 字）

**标题：**
装了但没用，350MB：一个打包依赖把安装包从 799MB 压到 225MB 的故事

**副标题：**
不是因为代码写得好，而是因为知道什么不该带

**正文：**

#### 一

PDflow V1.1 功能跑通了。

模板排版：选择 → 填写 → 预览 → 导出。六个模板。
主题切换：深色、浅色，跟系统走。
PDF 工具箱：合并、拆分、压缩、转换，一顿全做完。

功能完成那一刻，我很兴奋。
然后我跑了一遍 PyInstaller。

输出：**799MB。**

如果你看过上一帖，你应该知道这个数字的冲击力。
但这一帖不讲冲击，讲解决。

#### 二

我的排查路径是这样的：

先看打包日志。PyInstaller 在打包过程中会列出所有被包含的模块。
浏览一遍，PySide6 开头的模块占了绝大部分篇幅。

但 PySide6 本身不到 100MB。
问题在它带的子模块。

我注意到了 `PySide6.QtWebEngine` 系列——大约 350MB。
这是一个 Web 渲染引擎，用来在 Qt 程序里打开网页。

我的程序需要打开网页吗？
不需要。
我确认了三遍：
- 代码里搜 `from PySide6.QtWebEngine` → 0 个结果
- .ui 文件里搜 `QWebEngineView` → 0 个结果
- 印象里有没有用过 → 没有，早期评估时装的，后来换了思路

确认后，我在打包配置里加了一行排除规则。

#### 三

```
排除前：799MB
排除后：225MB
减重：72%
```

一行排除，350MB 没了。

这件事让我想了很久。

我们做软件的时候，天然倾向于"装全了再说"。
PySide6 装全量包、字体装整套、依赖装最新版——
这些在开发阶段没毛病，开发效率第一。

但发布是另一套逻辑。
发布的时候，**你安装的每一个没用上的依赖，都是负债。**

不是代码的问题。是工程的问题。

#### 四

225MB 不是终点。V1.1 总章程红线是 ≤150MB。

接下来还要做：
- 字体子集化（我们内置了中文字体，只用几百个字，却装了整包）
- 改 `onedir` 打包模式（减少自我解压开销）
- 进一步排查 hidden imports

但这 72% 的减重，验证了一个方向：
**桌面软件优化的第一步，不是优化你写了什么。**
**是优化你带了什么。**

#### 五

写代码快 15 年了，这件事我竟然到今天才真正想明白。

以前总觉得"加一个依赖而已"，"装全了省心"。
这些习惯在 Web 时代没问题——npm install 几 MB，部署也是几 MB。
但桌面软件不一样。每一个 MB 都是用户下载时间、磁盘占用、启动速度。

安装包体积，就是桌面软件的产品质量。

最后问一句：
你们做桌面软件的时候，最大的依赖体积来源是什么？
评论区聊聊，我准备把下一步优化过程也整理出来。

关注我，持续更新这个 PDF 工具的瘦身日记。

—— 一个被 799MB 教育过的独立开发者

---

### GitHub Discussion 版（英文）

**Title:**
Trimmed our PySide6 installer from 799MB to 225MB by removing unused QtWebEngine (72% reduction)

**Body:**

We're building a local-first PDF tool (PDflow) with PySide6. First build: **799MB**.

Root cause: PySide6 ships modular packages. We had installed the full bundle including QtWebEngine (~350MB) during early eval — but never actually used it in code or UI.

Fix: Excluded `PySide6/QtWebEngine*` from the PyInstaller spec.

```
Before: 799MB
After:  225MB (-72%)
```

Takeaway: Not every installed dependency needs to ship. Check what you actually import — not what you installed months ago.

Targeting ≤150MB for the final release. Anyone else had similar experiences with PySide6 bloat?

---

## 发布清单

- [ ] 正文已完成（完整版）
- [ ] 小红书版 / Nodeloc 版 / 公众号版 / GitHub Discussion 版已完成
- [ ] 截图：需要 225MB 结果截图 + 排除前后对比图
- [ ] changelog.md 已更新 → ✅ 2026-06-14
- [ ] ideas.md 已更新 → ✅ 标记完成

## 不发（红线）

- ❌ 不放下载链接
- ❌ 不堆砌 PyInstaller 配置参数
- ❌ 不剧透 V1.2 / V2.0
- ❌ 不暴露后端实现细节