# -*- coding: utf-8 -*-
"""
PDFlow Logo 品牌应用手册 PDF 生成脚本（嵌入中文字体）
"""
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Flowable,
    Image as RLImage,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json, os

# ═══ 注册中文字体 ═══
pdfmetrics.registerFont(TTFont('ChineseFont', r'C:\Windows\Fonts\msyh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('ChineseBold', r'C:\Windows\Fonts\msyhbd.ttc', subfontIndex=0))

# ═══ 配色常量 ═══
ACCENT = '#165DFF'
BG_LIGHT = '#EEF4FF'
TEXT_DARK = '#1a1a2e'
MUTED = '#888888'

# ═══ Callout 组件 ═══
class CalloutBox(Flowable):
    def __init__(self, text, style, accent=ACCENT, bg=BG_LIGHT):
        Flowable.__init__(self)
        self._para = Paragraph(text, style)
        self._accent = HexColor(accent)
        self._bg = HexColor(bg)

    def wrap(self, aw, ah):
        self._w = aw
        _, ph = self._para.wrap(aw - 36, ah)
        self._h = ph + 22
        return aw, self._h

    def draw(self):
        c = self.canv
        c.setFillColor(self._bg)
        c.roundRect(0, 0, self._w, self._h, 5, fill=1, stroke=0)
        c.setFillColor(self._accent)
        c.rect(0, 0, 4, self._h, fill=1, stroke=0)
        self._para.drawOn(c, 18, 11)


# ═══ 样式定义 ═══
styles = {
    'title': ParagraphStyle('Title', fontName='ChineseBold', fontSize=28, leading=36,
                            alignment=TA_CENTER, textColor=HexColor(TEXT_DARK), spaceAfter=20),
    'h1': ParagraphStyle('H1', fontName='ChineseBold', fontSize=22, leading=30,
                          textColor=HexColor(TEXT_DARK), spaceBefore=24, spaceAfter=12),
    'h2': ParagraphStyle('H2', fontName='ChineseBold', fontSize=16, leading=24,
                          textColor=HexColor(TEXT_DARK), spaceBefore=18, spaceAfter=8),
    'h3': ParagraphStyle('H3', fontName='ChineseBold', fontSize=13, leading=20,
                          textColor=HexColor(TEXT_DARK), spaceBefore=12, spaceAfter=6),
    'body': ParagraphStyle('Body', fontName='ChineseFont', fontSize=10.5, leading=18,
                            alignment=TA_JUSTIFY, textColor=HexColor(TEXT_DARK), spaceAfter=8),
    'bullet': ParagraphStyle('Bullet', fontName='ChineseFont', fontSize=10.5, leading=18,
                             leftIndent=18, bulletIndent=0, textColor=HexColor(TEXT_DARK), spaceAfter=4),
    'callout': ParagraphStyle('Callout', fontName='ChineseFont', fontSize=10.5, leading=18,
                              textColor=HexColor(TEXT_DARK)),
    'caption': ParagraphStyle('Caption', fontName='ChineseFont', fontSize=9, leading=14,
                              textColor=MUTED, alignment=TA_CENTER),
    'meta': ParagraphStyle('Meta', fontName='ChineseFont', fontSize=8.5, leading=12, textColor=MUTED),
}


# ═══ 文档模板（页眉页脚） ═══
class MyDoc(BaseDocTemplate):
    def __init__(self, path, **kw):
        BaseDocTemplate.__init__(self, path, **kw)
        fr = Frame(self.leftMargin, self.bottomMargin,
                   self.width, self.height, id='body')
        tmpl = PageTemplate(id='main', frames=fr, onPage=self._decorate)
        self.addPageTemplates([tmpl])

    def _decorate(self, canv, doc):
        lm, rm = doc.leftMargin, doc.rightMargin
        pw, ph = doc.pagesize
        top = ph - doc.topMargin
        canv.saveState()
        # 页眉线 + 标题/日期
        canv.setStrokeColor(HexColor(ACCENT))
        canv.setLineWidth(1.5)
        canv.line(lm, top + 12, pw - rm, top + 12)
        canv.setFillColor(MUTED)
        canv.setFont('ChineseFont', 8.5)
        canv.drawString(lm, top + 16, 'PDFLOW LOGO 品牌应用手册')
        canv.drawRightString(pw - rm, top + 16, '2026年4月')
        # 页脚线 + 作者/页码
        canv.setStrokeColor(HexColor('#DDDDDD'))
        canv.setLineWidth(0.5)
        canv.line(lm, doc.bottomMargin - 12, pw - rm, doc.bottomMargin - 12)
        canv.setFont('ChineseFont', 8.5)
        canv.drawString(lm, doc.bottomMargin - 22, 'PDFlow Design Team')
        canv.drawRightString(pw - rm, doc.bottomMargin - 22, str(doc.page))
        canv.restoreState()


# ═══ 构建文档 ═══
BASE = r'c:\Users\Administrator\WorkBuddy\20260417091523\NotionEditor\assets'
OUT = os.path.join(BASE, 'PDFlow_Logo品牌应用手册_2026-04-v2.pdf')

doc = MyDoc(OUT, pagesize=A4,
            leftMargin=45, rightMargin=45, topMargin=55, bottomMargin=45)

story = []

# ── 封面 ──
story.append(Spacer(1, 80 * mm))
story.append(Paragraph('PDFlow', styles['title']))
story.append(Paragraph('Logo 品牌应用手册', styles['title']))
story.append(Spacer(1, 15 * mm))
story.append(HRFlowable(width='60%', thickness=2, color=HexColor(ACCENT), spaceBefore=10, spaceAfter=10))
story.append(Spacer(1, 10 * mm))
story.append(Paragraph('版本：V1.0  |  日期：2026年4月', styles['meta']))
story.append(Paragraph('PDF 处理工具 · 设计师专用', styles['meta']))

# ── Logo 大图页 ──
logo_path = os.path.join(BASE, 'pdflow-logo.png')
if os.path.exists(logo_path):
    story.append(PageBreak())
    img = RLImage(logo_path, width=120 * mm, height=120 * mm)
    img.hAlign = 'CENTER'
    story.append(img)
    story.append(Paragraph('PDFlow 品牌标志 — 官方标准版', styles['caption']))

# ═══ 第一章：品牌概述 ═══
story.append(PageBreak())
story.append(Paragraph('一、品牌概述', styles['h1']))
story.append(HRFlowable(width='100%', thickness=1.5, color=HexColor(ACCENT), spaceBefore=2, spaceAfter=12))

story.append(Paragraph('<b>1.1 品牌定位</b>', styles['h3']))
story.append(Paragraph(
    'PDFlow 是一款面向专业设计师的 PDF 处理桌面工具，集成 PDF 编辑、格式转换、'
    '批量处理、设计素材导出等核心功能。目标用户为平面设计师、电商美工、印刷从业者，'
    '强调高效、精准、美观的文件处理体验。',
    styles['body']
))

story.append(Paragraph('<b>1.2 核心价值</b>', styles['h3']))
for v in ['<b>高效</b> — 批量处理、一键转换，减少重复劳动',
          '<b>精准</b> — 保留原始设计质量，CMYK/RGB 色彩管理',
          '<b>美观</b> — Notion 风格极简 UI，蓝白配色，Mica 毛玻璃效果',
          '<b>轻量</b> — 本地运行，无需登录，离线可用，体积小巧']:
    story.append(Paragraph(f'• {v}', styles['bullet']))

story.append(Spacer(1, 6))
story.append(CalloutBox(
    '<b>品牌口号：</b>印流 — 让 PDF 如水流般顺畅',
    styles['callout'], ACCENT, BG_LIGHT
))
story.append(Spacer(1, 8))

story.append(Paragraph('<b>1.3 命名释义</b>', styles['h3']))
story.append(Paragraph(
    '<b>PDFlow = PDF + Flow</b><br/>'
    '"PD" 代表 PDF（Portable Document Format），"Flow" 表达工作流（Workflow）如行云流水般顺畅。'
    '中文名"印流"寓意：印刷/打印之流，亦指工作流程的流畅无阻。',
    styles['body']
))

# ═══ 第二章：Logo 设计规范 ═══
story.append(Paragraph('二、Logo 设计规范', styles['h1']))
story.append(HRFlowable(width='100%', thickness=1.5, color=HexColor(ACCENT), spaceBefore=2, spaceAfter=12))

story.append(Paragraph('<b>2.1 设计理念</b>', styles['h3']))
story.append(Paragraph(
    'Logo 以"S 形流动曲线"为核心视觉元素，融合文档折角与钢笔笔尖三个符号：',
    styles['body']
))
for e in ['<b>S 形曲线</b> — 象征 "Flow" 工作流，代表文件处理的连贯性与流畅感',
          '<b>文档折角</b> — 右上角翻页效果，直接关联 PDF 文档属性',
          '<b>钢笔笔尖</b> — 右下角编辑符号，暗示设计编辑与创意输出能力']:
    story.append(Paragraph(f'• {e}', styles['bullet']))

story.append(Paragraph('<b>2.2 配色方案</b>', styles['h3']))
color_data = [
    ['颜色名称', '色值', '用途'],
    ['主蓝色 (Primary)', '#165DFF', 'Logo 主体、按钮、链接、重点强调'],
    ['亮蓝色 (Light)', '#4080FF', '渐变过渡、悬停状态、辅助元素'],
    ['深蓝色 (Dark)', '#092E85', '文字标题、深色背景模式'],
    ['背景蓝 (Bg Light)', '#EEF4FF', '卡片背景、Callout 高亮块'],
    ['文字色 (Text)', '#1A1A2E', '正文文字、主要信息'],
    ['辅助灰 (Muted)', '#888888', '次要信息、说明文字、页脚'],
]
ct = Table(color_data, colWidths=[35*mm, 30*mm, 75*mm])
ct.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor(ACCENT)),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#DDDDDD')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#FAFBFC')]),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(ct)
story.append(Spacer(1, 10))

story.append(Paragraph('<b>2.3 字体规范</b>', styles['h3']))
ft_data = [
    ['使用场景', '字体', '字重'],
    ['品牌名称 / 标题', 'Microsoft YaHei (微软雅黑) / Inter', 'Bold (700)'],
    ['正文内容', 'Microsoft YaHei (微软雅黑) / Inter', 'Regular (400)'],
    ['数据表格 / 代码', 'Consolas / JetBrains Mono', 'Regular (400)'],
]
ft = Table(ft_data, colWidths=[45*mm, 55*mm, 40*mm])
ft.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor(ACCENT)),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#DDDDDD')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#FAFBFC')]),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(ft)

# ═══ 第三章：尺寸规格 ═══
story.append(PageBreak())
story.append(Paragraph('三、Logo 尺寸规格', styles['h1']))
story.append(HRFlowable(width='100%', thickness=1.5, color=HexColor(ACCENT), spaceBefore=2, spaceAfter=12))

size_data = [
    ['文件名', '尺寸 (px)', '适用场景'],
    ['pdflow-logo.png', '1024 × 1024', '原始高清版 / 印刷源文件 / 大屏展示'],
    ['pdflow-logo-256.png', '256 × 256', 'Windows/macOS 应用图标 / 启动器'],
    ['pdflow-logo-128.png', '128 × 128', '资源管理器图标 / 网站 favicon 大尺寸'],
    ['pdflow-logo-64.png', '64 × 64', '工具栏图标 / Dock 图标 / 任务栏预览'],
    ['pdflow-logo-48.png', '48 × 48', 'macOS Finder 图标 / 对话框图标'],
    ['pdflow-logo-32.png', '32 × 32', 'Windows 任务栏 / 系统托盘'],
    ['pdflow-logo-16.png', '16 × 16', '浏览器 Favicon 最小尺寸 / 标题栏'],
]
st = Table(size_data, colWidths=[42*mm, 30*mm, 68*mm])
st.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor(ACCENT)),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#DDDDDD')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#FAFBFC')]),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(st)
story.append(Spacer(1, 8))
story.append(Paragraph('* 所有尺寸均为等比例缩放，保持 1:1 宽高比。最小安全使用尺寸为 16×16px。', styles['caption']))

# ═══ 第四章：应用场景 ═══
story.append(Paragraph('四、应用场景指南', styles['h1']))
story.append(HRFlowable(width='100%', thickness=1.5, color=HexColor(ACCENT), spaceBefore=2, spaceAfter=12))

story.append(Paragraph('<b>4.1 桌面应用</b>', styles['h3']))
story.append(Paragraph(
    '• 应用程序图标 (.ico)：使用 256px 版本生成多尺寸 ICO 文件<br/>'
    '• 安装向导 / 关于页面：1024px 居中展示，下方配品牌名称<br/>'
    '• Windows 开始菜单 / macOS Launchpad：保持圆角正方形裁切<br/>'
    '• 任务栏 / Dock：使用 32px 或 64px 版本，确保小尺寸清晰可辨',
    styles['body']
))

story.append(Paragraph('<b>4.2 界面内嵌</b>', styles['h3']))
story.append(Paragraph(
    '• 工具栏按钮：64px 版本，四周保留至少 4px 安全边距<br/>'
    '• 导航标签 / 侧栏：配合文字使用时建议 24~32px<br/>'
    '• 加载动画：基于 S 曲线元素做旋转或流动动效<br/>'
    '• 空状态插图：浅色背景 + 半透明 Logo 作为占位提示',
    styles['body']
))

story.append(Paragraph('<b>4.3 数字媒体</b>', styles['h3']))
story.append(Paragraph(
    '• 网站 Favicon：16px 和 32px 双尺寸，生成 .ico 多分辨率文件<br/>'
    '• 社交媒体头像：1024px 圆形裁切（微信、微博、Twitter 等）<br/>'
    '• 邮件签名：64px 配合品牌名称横向排列<br/>'
    '• 文档水印：降低透明度至 10%~15%，铺满页面平铺',
    styles['body']
))

story.append(Paragraph('<b>4.4 印刷品</b>', styles['h3']))
story.append(Paragraph(
    '• 名片：使用矢量 SVG 源文件或 300dpi 以上 PNG<br/>'
    '• 产品包装盒：主色调 #165DFF 背景 + 白色反色 Logo<br/>'
    '• 宣传册封面：居中放置，四周留白不少于 Logo 高度的 50%',
    styles['body']
))

# ═══ 第五章：保护与禁忌 ═══
story.append(PageBreak())
story.append(Paragraph('五、使用禁忌与保护', styles['h1']))
story.append(HRFlowable(width='100%', thickness=1.5, color=HexColor(ACCENT), spaceBefore=2, spaceAfter=12))

story.append(Paragraph('<b>[禁止] 禁止事项</b>', styles['h3']))
for d in ['禁止拉伸变形 — 必须保持 1:1 等比例缩放',
          '禁止修改颜色 — 不允许更改 Logo 的蓝渐变配色方案',
          '禁止添加特效 — 不得添加阴影、发光、浮雕等额外效果',
          '禁止局部裁切 — 不得只使用 Logo 的部分元素（如只用 S 曲线）',
          '禁止低质使用 — 印刷场景必须使用 300dpi 以上或矢量源文件']:
    story.append(Paragraph(f'• {d}', styles['bullet']))

story.append(Spacer(1, 10))
story.append(Paragraph('<b>[注意] 特殊情况处理</b>', styles['h3']))
story.append(CalloutBox(
    '<b>深色背景：</b>使用白色或浅蓝色 Logo 反色版本，保持足够对比度（WCAG AA 级以上）<br/><br/>'
    '<b>单色限制：</b>仅允许使用纯色 #165DFF 或纯黑/纯白三种单色模式<br/><br/>'
    '<b>超小尺寸：</b>16px 以下仅显示 S 曲线核心图形，去除细节元素',
    styles['callout'], ACCENT, BG_LIGHT
))

story.append(Spacer(1, 20))
story.append(HRFlowable(width='100%', thickness=0.5, color=MUTED, spaceBefore=10, spaceAfter=10))
story.append(Paragraph('© 2026 PDFlow Design Team. 本手册为内部品牌规范文件，未经授权不得外传。', styles['meta']))
story.append(Paragraph('如有品牌使用疑问，请联系设计团队。', styles['meta']))

doc.build(story)
print(f'OK: PDF generated at {OUT}')
