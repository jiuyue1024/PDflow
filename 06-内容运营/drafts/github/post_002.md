# post_002 · GitHub Discussion 版

> 平台：GitHub Discussions
> 状态：待发布
> 创建：2026-06-14
> 字数控制：200-400 字（英文）

---

## Title

Trimmed our PySide6 installer from 799MB to 225MB (-72%) by removing unused QtWebEngine

## Body

We're building a local-first PDF tool (PDflow) with PySide6. First build: **799MB**.

Root cause: PySide6 ships modular packages. We had installed the full bundle including QtWebEngine (~350MB) during early evaluation — but never actually used it in code or UI.

Fix: Excluded `PySide6/QtWebEngine*` from the PyInstaller spec.

```
Before: 799MB
After:  225MB (-72%)
```

Takeaway: Not every installed dependency needs to ship. Check what you actually import — not what you installed months ago.

Targeting ≤150MB for the final release. Anyone else had similar experiences with PySide6 bloat?

---

## Publish Checklist

- [ ] Post in appropriate category (e.g., "Show and tell" or "General")
- [ ] No download link yet (V1.1 not released)
- [ ] Reply to first 5 comments within 24h