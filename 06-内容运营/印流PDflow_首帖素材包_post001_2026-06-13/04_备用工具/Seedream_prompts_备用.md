# post_001 配图 Prompt 手册

> 为 post_001 三平台首帖准备的 3 张配图 prompt。
> 适配模型：Volcengine Seedream 5.0（推荐）/ 4.5 / 4.0
> 输出尺寸按平台优化。

---

## 总约束（所有 prompt 共用）

- ❌ 不生成印流PDflow LOGO（总章程 4.2 红线）
- ❌ 不出现具体二维码
- ❌ 不出现真实人脸
- ❌ 不暴露 PyInstaller 真实命令截图
- ✅ 颜色基调：印流PDflow 主题色 #4D7CFE（蓝）+ 深色 #0B0E11
- ✅ 风格：现代极简、科技感、独立开发者审美
- ✅ 数字「798MB」「≤150MB」必须醒目可读

---

## 图 1 / 公众号头图

**文件名：** `assets/cover/post_001_cover.png`
**尺寸：** `landscape_16_9`（1920×1080 公众号头图标准）
**模型：** 5.0
**输出格式：** png

**Prompt（English, 推荐）：**

```
A modern minimalist cover image for a tech blog post. Deep dark
background (#0B0E11) with electric blue accent (#4D7CFE). Center
composition: a giant bold "798MB" number in glowing electric blue
typography, slightly tilted. Below it, a single line of smaller
white text: "When your desktop app first ships." Visual elements:
a faint transparent file folder icon at the bottom-right corner, a
subtle grid of dots in the background, a soft glow ring around the
number. Cinematic lighting, tech magazine cover style, clean
typography, no logos, no QR codes, no human faces. Aspect ratio
16:9.
```

**Prompt 备选（中文版，部分模型对中文更友好）：**

```
极简科技感博客头图。深色背景 #0B0E11，蓝色主光 #4D7CFE。
中央巨大加粗数字"798MB"以发光蓝色字体显示，略微倾斜。
下方一行较小的白色文字："当你的桌面软件第一次发布时"。
视觉元素：右下角淡透明文件夹图标，背景点阵网格，
数字周围柔和光晕。电影感打光，科技杂志封面风格，
排版干净，无 logo、无二维码、无人脸。16:9 比例。
```

---

## 图 2 / 小红书配图

**文件名：** `assets/screenshots/post_001_xhs.png`
**尺寸：** `square_hd`（小红书方形首图最佳）
**模型：** 5.0
**输出格式：** png

**Prompt（English）：**

```
A square social media cover for Xiaohongshu. Dark background
(#0B0E11) with electric blue (#4D7CFE) accent. Bold central
number "798MB" in massive glowing blue typography. Top tag
"独立开发" in small white text. Bottom caption in Chinese
characters: "第一次做桌面软件发布". Subtle file folder icon
beside the number. Clean modern minimalist style, no logos,
no QR codes, no faces. Square 1:1 aspect.
```

**Prompt 备选（中文版）：**

```
小红书方形首图。深色背景 #0B0E11，蓝色主光 #4D7CFE。
中央巨大发光蓝色数字"798MB"。顶部小字"独立开发"白色。
底部中文一行小字"第一次做桌面软件发布"。
数字旁有淡文件夹图标。极简科技风，无 logo、无二维码、
无人脸。1:1 方形。
```

---

## 图 3 / 公众号正文配图（体积演变示意）

**文件名：** `assets/screenshots/post_001_size_journey.png`
**尺寸：** `landscape_16_9`（公众号正文 16:9 视觉最好）
**模型：** 5.0
**输出格式：** png

**Prompt（English）：**

```
A clean infographic showing desktop application package size
evolution. Dark background (#0B0E11), electric blue (#4D7CFE)
and warm red accents. Three milestone stages laid out
horizontally with connecting arrows:
- Stage 1 (large red bar): "798MB" labeled "V1.1-beta 首次打包"
- Stage 2 (medium orange bar): "瘦身中" labeled "剥离 WebEngine"
- Stage 3 (small blue bar): "≤150MB" labeled "V1.1 正式版目标"
At the bottom a thin progress bar showing the journey. No logos,
no QR codes, no human faces. Clean infographic style, modern
typography, 16:9 aspect.
```

**Prompt 备选（中文版）：**

```
极简信息图，展示桌面软件安装包体积演变。
深色背景 #0B0E11，蓝主色 #4D7CFE，红色重点。
三阶段横向并排，用箭头连接：
- 阶段 1（高红条）："798MB" 标注"V1.1-beta 首次打包"
- 阶段 2（中橙条）："瘦身中" 标注"剥离 WebEngine"
- 阶段 3（矮蓝条）："≤150MB" 标注"V1.1 正式版目标"
底部一条进度条。无 logo、无二维码、无人脸。
干净信息图风格，16:9。
```

---

## 跑图命令（你贴 API key 后我用这个跑）

```bash
# 图 1：公众号头图
python seedream_image_generate.py \
  --prompt "<上方 5.0 prompt>" \
  --size landscape_16_9 \
  --output-format png \
  --no-watermark \
  --version 5.0

# 图 2：小红书配图
python seedream_image_generate.py \
  --prompt "<上方 5.0 prompt>" \
  --size square_hd \
  --output-format png \
  --no-watermark \
  --version 5.0

# 图 3：体积演变示意
python seedream_image_generate.py \
  --prompt "<上方 5.0 prompt>" \
  --size landscape_16_9 \
  --output-format png \
  --no-watermark \
  --version 5.0
```

---

## 跑图前确认

- [ ] 已设置 `ARK_API_KEY`（或 `MODEL_IMAGE_API_KEY`）
- [ ] 已安装 `httpx`（已装：httpx 0.28.1）
- [ ] 输出目录 `06-内容运营/assets/cover/` 与 `assets/screenshots/` 已存在（已建）
- [ ] 图片下载后用 `move` / `cp` 命令归位到 `assets/cover/` 和 `assets/screenshots/`
