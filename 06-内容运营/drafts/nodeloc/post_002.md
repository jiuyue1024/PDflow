# post_002 · Nodeloc / V2EX 版

> 平台：Nodeloc / V2EX
> 节点：V2EX → Python / 分享创造
> 状态：待发布
> 创建：2026-06-14
> 字数控制：500-800 字

---

## 标题

PySide6 安装包 799MB → 225MB，排除 QtWebEngine 就减了 72%

## 正文

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

## 发布清单

- [ ] 配图：排除前后对比图
- [ ] 不放下载链接
- [ ] 24h 内回复前 10 条评论

## 互动钩子

> "有人也踩过类似的打包坑吗？"