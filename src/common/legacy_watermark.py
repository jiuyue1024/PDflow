"""
legacy_watermark.py — 从旧版 api/__init__.py 完整提取的水印功能
严格按照旧版还原，不使用简化版
"""

import os
import math
import base64
import io
import time
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

# ===================================================================
# 公共函数：计算水印平铺的行列数（旧版完整逻辑）
# ===================================================================

def calc_tile_counts(page_width, page_height, grid_w, grid_h):
    """公共函数：计算水印平铺的行列数

    核心逻辑：页面尺寸 / 格子尺寸，向下取整。
    只有当余量 > 0 时才 +1（补半个格子到边缘），
    绝不做无条件的 +1（那会导致最右列/最下行重复）。

    前后端统一调用此函数，杜绝计算偏差。

    Args:
        page_width:  页面宽度
        page_height: 页面高度
        grid_w:      水印格子宽度（水印宽 + 间距）
        grid_h:      水印格子高度（水印高 + 间距）

    Returns:
        (cols, rows) 行列数元组
    """
    if page_width <= 0 or page_height <= 0 or grid_w <= 0 or grid_h <= 0:
        return 4, 5  # 安全兜底

    # 向下取整得到完整格子数
    base_cols = int(page_width / grid_w)
    base_rows = int(page_height / grid_h)

    # 如果有余量（页面没有被完整格子恰好铺满），则多加 1 行/列以覆盖边缘
    # 但绝不多加 2 —— 原来的 +1 是无条件加，导致最后一行/列完全超出页面还画了一次
    has_x_remainder = (page_width % grid_w) > 0
    has_y_remainder = (page_height % grid_h) > 0

    cols = max(1, base_cols + (1 if has_x_remainder else 0))
    rows = max(1, base_rows + (1 if has_y_remainder else 0))

    return cols, rows


# ===================================================================
# 统一水印参数标准化函数（旧版完整逻辑）
# ===================================================================

def normalize_watermark_params(watermark_type='text', text='', font_size=48,
                               opacity=30, rotation=-45, position='center',
                               scale=30, color='#888888', image_path='',
                               page_width=0, page_height=0,
                               opacity_is_0_100=True):
    """
    统一水印参数标准化函数（预览和导出共用）
    
    参数:
        opacity_is_0_100: 前端传入的透明度是否为0-100范围
                              - True: 前端传的是 0-100，需要转换 (如 generateWatermarkPreview)
                              - False: 前端/内部已传 0-1 浮点数 (如 doWatermark 导出)
    
    返回: 完整的水印参数字典（与 _calc_watermark_params 格式一致）
    
    此函数消除前端传参不一致导致的问题：
        - 预览时前端传 0-100 (如 30)
        - 导出时前端传 0-1 (如 0.3)
        - 内部统一转为 0-1 浮点数
    """
    # 1. 透明度标准化（关键修复：消除前端传参不一致问题）
    if opacity_is_0_100:
        # 前端传入的是 0-100 范围 (如 30)
        opacity = float(opacity) / 100.0 if opacity is not None else 0.3
    else:
        # 前端/内部已传 0-1 浮点数 (如 0.3)
        opacity = float(opacity) if opacity is not None else 0.3
    opacity = max(0.0, min(1.0, opacity))
    
    # 2. 旋转角度标准化
    rotation = int(float(rotation)) if rotation is not None else -45
    
    # 3. 缩放因子标准化
    scale = int(float(scale)) if scale is not None else 30
    scale = max(1, min(200, scale))
    scale_factor = scale / 100.0
    
    # 4. 字号标准化
    font_size = int(float(font_size)) if font_size is not None else 48
    font_size = max(12, min(200, font_size))
    actual_font_size = int(font_size * scale_factor)
    actual_font_size = max(8, min(300, actual_font_size))
    
    # 5. 解析颜色
    try:
        r_int = int(color[1:3], 16)
        g_int = int(color[3:5], 16)
        b_int = int(color[5:7], 16)
    except:
        r_int, g_int, b_int = 136, 136, 136
    
    color_rgb = (r_int / 255.0, g_int / 255.0, b_int / 255.0)
    color_int = (r_int, g_int, b_int)
    
    # 6. 估算文字尺寸
    text_len = len(text) if text else 0
    text_width = text_len * actual_font_size * 0.6
    text_height = actual_font_size * 1.2
    
    # 7. 图片尺寸计算（页面相对：scale% 表示水印占页面短边的百分比）
    image_size = (0, 0)
    if image_path and os.path.exists(image_path):
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                if page_width > 0 and page_height > 0:
                    page_short = min(page_width, page_height)
                    target = page_short * scale_factor
                    ratio = target / max(img.width, img.height)
                    image_size = (max(1, int(img.width * ratio)),
                                  max(1, int(img.height * ratio)))
                else:
                    image_size = (int(img.width * scale_factor),
                                  int(img.height * scale_factor))
        except Exception as e:
            print(f"[watermark] 读取图片尺寸失败: {e}")
    
    # 8. 平铺行列数计算
    if watermark_type == 'text':
        padding_x = text_width * 0.5
        padding_y = text_height * 0.5
        grid_w = text_width + padding_x
        grid_h = text_height + padding_y
    else:
        if image_size[0] > 0 and image_size[1] > 0:
            padding_x = image_size[0] * 0.5
            padding_y = image_size[1] * 0.5
            grid_w = image_size[0] + padding_x
            grid_h = image_size[1] + padding_y
        else:
            grid_w = grid_h = 100
            padding_x = padding_y = 50
    
    if page_width > 0 and page_height > 0:
        tile_cols, tile_rows = calc_tile_counts(page_width, page_height, grid_w, grid_h)
    else:
        tile_cols = 4
        tile_rows = 5
    
    # 9. 返回标准化参数字典
    return {
        'watermark_type': watermark_type,
        'font_size': font_size,
        'actual_font_size': actual_font_size,
        'opacity': opacity,              # 统一为 0-1 浮点数
        'rotation': rotation,
        'position': position,
        'scale': scale,
        'scale_factor': scale_factor,
        'color_rgb': color_rgb,
        'color_int': color_int,
        'text': text or '',
        'image_path': image_path or '',
        'page_width': page_width,
        'page_height': page_height,
        'text_width': text_width,
        'text_height': text_height,
        'image_size': image_size,
        'tile_cols': tile_cols,
        'tile_rows': tile_rows,
        'tile_padding_x': padding_x,
        'tile_padding_y': padding_y,
        'tile_grid_w': grid_w,
        'tile_grid_h': grid_h,
    }


# ===================================================================
# 添加水印主函数（旧版完整逻辑）
# ===================================================================

def add_watermark(filepath, output_path, watermark_type='text',
                 text='', font_size=48, color='#888888', opacity=0.3,
                 rotation=-45, position='center', layer='under',
                 image_path='', scale=30):
    """添加水印（旧版完整逻辑）
    
    watermark_type: text | image
    text: 文字水印内容
    font_size: 字号
    color: 颜色（十六进制）
    opacity: 透明度 0-1
    rotation: 旋转角度
    position: center | tile | top-left | top-right | bottom-left | bottom-right
    layer: over | under（覆盖/底层）
    image_path: 图片水印路径
    scale: 图片缩放比例 (10-200)
    """
    try:
        print(f"[add_watermark] 开始处理: {filepath}")
        
        doc = fitz.open(filepath)
        page = doc.load_page(0)
        rect = page.rect
        
        # 使用统一参数计算（key fix: use normalize_watermark_params）
        # 导出时 opacity 已传 0-1 浮点数，所以 opacity_is_0_100=False
        params = normalize_watermark_params(
            watermark_type=watermark_type,
            text=text,
            font_size=font_size,
            opacity=opacity,
            rotation=rotation,
            position=position,
            scale=scale,
            color=color,
            image_path=image_path,
            page_width=rect.width,
            page_height=rect.height,
            opacity_is_0_100=False
        )
        
        # 将 layer 参数添加到 params（normalize_watermark_params 不处理此参数）
        params['layer'] = layer
        
        print(f"[add_watermark] 统一参数: type={params['watermark_type']}, text={params['text']}, font_size={params['font_size']}, scale={params['scale']}%, actual_font_size={params['actual_font_size']}, opacity={params['opacity']}, rotation={params['rotation']}, position={params['position']}, image_size={params['image_size']}, tile={params['tile_cols']}x{params['tile_rows']}, layer={params['layer']}")
        
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            rect = page.rect
            
            if params['watermark_type'] == 'image' and params['image_path'] and os.path.exists(params['image_path']):
                # 图片水印
                _add_image_watermark(page, rect, params)
            else:
                # 文字水印（使用缩放后的实际字号）
                _add_text_watermark(page, rect, params)

        page_count = doc.page_count

        print(f"[add_watermark] 保存到: {output_path}")
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()

        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"[add_watermark] 成功! 文件大小: {file_size} bytes")
            return {"success": True, "output_path": output_path, "pages": page_count}
        else:
            return {"success": False, "error": "文件保存失败"}
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[add_watermark] 错误: {str(e)}")
        print(f"[add_watermark] 详细错误:\n{error_detail}")
        return {"success": False, "error": str(e)}


def _add_text_watermark(page, rect, params):
    """添加文字水印（使用统一参数）"""
    try:
        text = params['text']
        font_size = params['actual_font_size']
        color_rgb = params['color_rgb']
        opacity = params['opacity']
        rotation = params['rotation']
        position = params['position']
        layer = params.get('layer', 'under')
        
        r, g, b = color_rgb
        
        if position == 'tile':
            # 平铺水印 - 使用统一计算的行列数
            cols = params['tile_cols']
            rows = params['tile_rows']
            grid_w = params['tile_grid_w']
            grid_h = params['tile_grid_h']
            text_width = params['text_width']
            text_height = params['text_height']
            
            print(f"[_add_text_watermark] 平铺模式: cols={cols}, rows={rows}, grid={grid_w:.1f}x{grid_h:.1f}")
            
            for row in range(rows):
                for col in range(cols):
                    # 计算格子中心点（作为 _draw_text_watermark 的旋转中心）
                    center_x = col * grid_w + grid_w / 2
                    center_y = row * grid_h + grid_h / 2
                    # 跳过超出页面的格子，避免钳制到边缘导致与相邻格重叠
                    if center_x > rect.width or center_y > rect.height:
                        continue
                    print(f"[_add_text_watermark] [tile] 正在绘制 第{row}行第{col}列: center=({center_x:.1f},{center_y:.1f})")
                    _draw_text_watermark(page, center_x, center_y, text, font_size, (r, g, b), opacity, rotation, layer)
        else:
            # 单个水印
            x, y = _get_position(rect, position, font_size, len(text))
            _draw_text_watermark(page, x, y, text, font_size, (r, g, b), opacity, rotation, layer)
            
    except Exception as e:
        print(f"[_add_text_watermark] 错误: {e}")
        import traceback
        print(traceback.format_exc())


def _draw_text_watermark(page, x, y, text, font_size, color, opacity, rotation, layer):
    """绘制单个文字水印（支持透明度、旋转、置顶叠加）

    核心思路：
    - 直接用 insert_text() 在页面上写水印
    - 使用 morph 参数实现任意角度旋转
    - fill_opacity 控制透明度，overlay=True 保证显示在最上层
    """
    try:
        # 转换颜色为 0-1 范围
        if color[0] > 1:
            r, g, b = color[0] / 255, color[1] / 255, color[2] / 255
        else:
            r, g, b = color

        print(f"[_draw_text_watermark] 开始绘制: text='{text}', font_size={font_size}, opacity={opacity}, rotation={rotation}")

        # 估算文字尺寸（中文字符按0.6em宽度，高度1.2倍字号）
        text_len = len(text)
        text_width = text_len * font_size * 0.6
        text_height = font_size * 1.2

        # 基线起点（insert_text 的坐标是基线左下角）
        base_x = x - text_width / 2
        base_y = y + text_height / 4

        print(f"[_draw_text_watermark] 文字尺寸: {text_width:.1f}x{text_height:.1f}, 基线起点: ({base_x:.1f},{base_y:.1f})")

        # ========== 直接使用 insert_text + morph 旋转方案 ==========
        # 构建旋转矩阵（绕中心点旋转）
        if rotation != 0:
            angle_rad = rotation * math.pi / 180.0
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            # 使用与 PIL Image.rotate() 一致的旋转方向：正值=逆时针，负值=顺时针
            # 矩阵 [a, b, c, d] 在 PyMuPDF 中变换为: x'=a*x+c*y, y'=b*x+d*y
            # [cos, sin, -sin, cos] = CW by θ, [cos, -sin, sin, cos] = CCW by θ
            # PIL rotate(): 正=CCW, 负=CW → 使用 [cos, sin, -sin, cos] 即 CW 旋转
            rotate_matrix = fitz.Matrix(cos_a, sin_a, -sin_a, cos_a, 0, 0)
            print(f"[_draw_text_watermark] 旋转矩阵: [{cos_a:.4f}, {sin_a:.4f}, {-sin_a:.4f}, {cos_a:.4f}], 中心: ({x:.1f},{y:.1f})")
            morph = (fitz.Point(x, y), rotate_matrix)
        else:
            morph = None

        # 使用 insert_font + fontname 方案，比 fontfile 参数更可靠
        # 先尝试注册系统字体，失败则回退到内置中文字体
        fontname = "china-s"
        font_loaded = False

        # 字体配置：(路径, 自定义fontname, 是否为ttc, ttc索引)
        font_configs = [
            ("C:/Windows/Fonts/simhei.ttf", "pdflow-simhei", False, 0),
            ("C:/Windows/Fonts/msyh.ttc", "pdflow-msyh", True, 0),
            ("C:/Windows/Fonts/simsun.ttc", "pdflow-simsun", True, 0),
            ("C:/Windows/Fonts/msyhbd.ttc", "pdflow-msyhbd", True, 0),
        ]

        for fp, custom_name, is_ttc, ttc_idx in font_configs:
            if not os.path.exists(fp):
                continue
            try:
                if is_ttc:
                    font = fitz.Font(fontfile=fp, fontbuffer=None)
                else:
                    font = fitz.Font(fontfile=fp)
                if font.is_writable:
                    page.insert_font(fontname=custom_name, fontfile=fp)
                    fontname = custom_name
                    font_loaded = True
                    print(f"[_draw_text_watermark] 注册系统字体: {fp} -> {custom_name}")
                    break
            except Exception as fe:
                print(f"[_draw_text_watermark] 字体 {fp} 注册失败: {fe}")
                continue

        if not font_loaded:
            print(f"[_draw_text_watermark] 未找到可用系统字体，使用内置中文字体: china-s")

        page.insert_text(
            fitz.Point(base_x, base_y),
            text,
            fontsize=font_size,
            fontname=fontname,
            color=(r, g, b),
            fill_opacity=opacity,
            morph=morph,
            overlay=True
        )

        print(f"[_draw_text_watermark] 绘制完成: 位置=({x:.1f},{y:.1f}), 透明度={opacity}, 旋转={rotation}")

    except Exception as e:
        print(f"[_draw_text_watermark] 错误: {e}")
        import traceback
        print(traceback.format_exc())


def _add_image_watermark(page, rect, params):
    """添加图片水印（支持透明度、旋转，使用统一参数）"""
    try:
        from PIL import Image
        import os
        
        image_path = params['image_path']
        opacity = params['opacity']
        position = params['position']
        rotation = params.get('rotation', 0)  # 获取旋转角度
        scale = params['scale']
        layer = params.get('layer', 'under')
        
        print(f"[_add_image_watermark] 开始处理: {image_path}, position={position}, scale={scale}, opacity={opacity}, rotation={rotation}")
        
        # 打开原图
        pil_img = Image.open(image_path)
        print(f"[_add_image_watermark] 原图尺寸: {pil_img.size}, 模式: {pil_img.mode}")
        
        # 转换为RGBA模式（确保有Alpha通道）
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
            print(f"[_add_image_watermark] 已转换为RGBA模式")
        
        # 应用透明度 - 修改Alpha通道
        if opacity < 1.0:
            # 获取Alpha通道并应用透明度
            r, g, b, alpha = pil_img.split()
            alpha = alpha.point(lambda p: int(p * opacity))
            pil_img = Image.merge('RGBA', (r, g, b, alpha))
            print(f"[_add_image_watermark] 已应用透明度: {opacity}")
        
        # 使用页面相对尺寸（normalize_watermark_params 已根据页面大小计算）
        new_width = params['image_size'][0]
        new_height = params['image_size'][1]
        
        if new_width < 1 or new_height < 1:
            print(f"[_add_image_watermark] 图片尺寸过小: {new_width}x{new_height}")
            return
        
        # 缩放图片
        pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"[_add_image_watermark] 缩放后尺寸: {new_width}x{new_height}")
        
        # 旋转图片（与预览一致）
        if rotation != 0:
            pil_img = pil_img.rotate(rotation, expand=True, fillcolor=(0, 0, 0, 0))
            print(f"[_add_image_watermark] 已旋转: rotation={rotation}, 旋转后尺寸: {pil_img.size}")
        
        # 保存为PNG内存流（保留Alpha通道）
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        png_data = img_bytes.getvalue()
        print(f"[_add_image_watermark] PNG数据大小: {len(png_data)} bytes")
        
        # 更新实际尺寸（旋转后可能改变）
        final_width, final_height = pil_img.size
        
        # 计算位置
        if position == 'center':
            x = (rect.width - final_width) / 2
            y = (rect.height - final_height) / 2
        elif position == 'tile':
            # 平铺图片水印 - 使用统一计算的行列数
            cols = params['tile_cols']
            rows = params['tile_rows']
            grid_w = params['tile_grid_w']
            grid_h = params['tile_grid_h']
            
            print(f"[_add_image_watermark] 平铺模式: cols={cols}, rows={rows}, grid={grid_w:.1f}x{grid_h:.1f}")
            
            for row in range(rows):
                for col in range(cols):
                    # 计算格子中心点，然后偏移到左上角
                    center_x = col * grid_w + grid_w / 2
                    center_y = row * grid_h + grid_h / 2
                    # 跳过超出页面的格子，避免钳制到边缘导致与相邻格重叠
                    if center_x > rect.width or center_y > rect.height:
                        continue
                    tx = center_x - final_width / 2
                    ty = center_y - final_height / 2
                    print(f"[_add_image_watermark] [tile] 正在绘制 第{row}行第{col}列: tx={tx:.1f}, ty={ty:.1f}")
                    dest_rect = fitz.Rect(tx, ty, tx + final_width, ty + final_height)
                    page.insert_image(dest_rect, stream=png_data, overlay=True)
            print(f"[_add_image_watermark] 平铺完成: {cols}x{rows}")
            return
        elif position == 'top-left':
            x, y = 20, 20
        elif position == 'top-right':
            x = rect.width - final_width - 20
            y = 20
        elif position == 'bottom-left':
            x = 20
            y = rect.height - final_height - 20
        elif position == 'bottom-right':
            x = rect.width - final_width - 20
            y = rect.height - final_height - 20
        else:
            x = (rect.width - final_width) / 2
            y = (rect.height - final_height) / 2
        
        # 插入单个图片
        dest_rect = fitz.Rect(x, y, x + final_width, y + final_height)
        page.insert_image(dest_rect, stream=png_data, overlay=True)
        print(f"[_add_image_watermark] 已插入图片: 位置={position}, 坐标=({x:.1f},{y:.1f}), 尺寸={final_width}x{final_height}")
        
    except Exception as e:
        print(f"[_add_image_watermark] 错误: {e}")
        import traceback
        print(traceback.format_exc())


def _get_position(rect, position, font_size, text_len):
    """计算水印位置"""
    text_width = text_len * font_size * 0.6  # 估算文字宽度
    text_height = font_size * 1.2  # 估算文字高度
    
    # 返回文字中心点坐标（_draw_text_watermark 以此为旋转中心）
    if position == 'center':
        return rect.width / 2, rect.height / 2
    elif position == 'top-left':
        return 50 + text_width / 2, font_size + 20 + text_height / 2
    elif position == 'top-right':
        return rect.width - 50 - text_width / 2, font_size + 20 + text_height / 2
    elif position == 'bottom-left':
        return 50 + text_width / 2, rect.height - 20 - text_height / 2
    elif position == 'bottom-right':
        return rect.width - 50 - text_width / 2, rect.height - 20 - text_height / 2
    else:
        return rect.width / 2, rect.height / 2


# ===================================================================
# PIL 快速预览引擎（像素合成，比 PyMuPDF 内容流操作快 10-100 倍）
# ===================================================================

def _pil_render_text_stamp(draw_target, cx, cy, text, font, font_size, color, opacity, rotation):
    """渲染单个文字水印 stamp 并粘贴到目标 RGBA 图像"""
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    if tw < 1 or th < 1:
        return

    padding = max(4, font_size // 4)
    stamp_w = int(tw + padding * 2)
    stamp_h = int(th + padding * 2)

    stamp = Image.new("RGBA", (stamp_w, stamp_h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stamp)

    alpha = int(255 * opacity)
    r, g, b = color
    sdraw.text((padding - bbox[0], padding - bbox[1]), text, font=font, fill=(r, g, b, alpha))

    if rotation != 0:
        stamp = stamp.rotate(rotation, expand=True, center=(stamp_w // 2, stamp_h // 2),
                             fillcolor=(0, 0, 0, 0))

    px = int(cx - stamp.width / 2)
    py = int(cy - stamp.height / 2)
    draw_target.paste(stamp, (px, py), stamp)


def _pil_add_text_watermark(overlay, params, zoom):
    """在 PIL 叠加层上绘制文字水印
    
    Args:
        overlay: RGBA PIL Image（叠加目标）
        params: 标准化水印参数字典
        zoom: 缩放比例（相对于原始页面）
    """
    text = params['text']
    font_size = max(8, int(params['actual_font_size'] * zoom))
    r, g, b = params['color_int']
    opacity = params['opacity']
    rotation = params['rotation']
    position = params['position']

    # 加载字体（与导出逻辑保持一致）
    font = None
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except Exception as e:
                print(f"[watermark] 字体加载失败 {fp}: {e}")
                continue
    if font is None:
        font = ImageFont.load_default()

    if position == 'tile':
        cols = params['tile_cols']
        rows = params['tile_rows']
        grid_w = params['tile_grid_w'] * zoom
        grid_h = params['tile_grid_h'] * zoom

        for row in range(rows):
            for col in range(cols):
                cx = col * grid_w + grid_w / 2
                cy = row * grid_h + grid_h / 2
                if cx > overlay.width or cy > overlay.height:
                    continue
                _pil_render_text_stamp(overlay, cx, cy, text, font, font_size,
                                       (r, g, b), opacity, rotation)
    else:
        # 单个位置
        bbox = font.getbbox(text)
        tw = (bbox[2] - bbox[0]) * zoom
        th = (bbox[3] - bbox[1]) * zoom
        margin = max(10, int(20 * zoom))

        if position == 'center':
            cx, cy = overlay.width / 2, overlay.height / 2
        elif position == 'top-left':
            cx, cy = margin + tw / 2, margin + th / 2
        elif position == 'top-right':
            cx, cy = overlay.width - margin - tw / 2, margin + th / 2
        elif position == 'bottom-left':
            cx, cy = margin + tw / 2, overlay.height - margin - th / 2
        elif position == 'bottom-right':
            cx, cy = overlay.width - margin - tw / 2, overlay.height - margin - th / 2
        else:
            cx, cy = overlay.width / 2, overlay.height / 2

        _pil_render_text_stamp(overlay, cx, cy, text, font, font_size,
                               (r, g, b), opacity, rotation)


def _pil_add_image_watermark(overlay, params, zoom):
    """在 PIL 叠加层上绘制图片水印"""
    image_path = params['image_path']
    opacity = params['opacity']
    rotation = params['rotation']
    position = params['position']
    scale_factor = params['scale_factor']
    
    print(f"[_pil_add_image_watermark] rotation={rotation}°, opacity={opacity:.2f}, scale_factor={scale_factor:.2f}, position={position}, image={image_path}")

    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"[_pil_add_image_watermark] 图片加载失败: {e}")
        return

    # 缩放：使用页面相对尺寸 × zoom（normalize 已根据页面大小计算）
    new_w = max(1, int(params['image_size'][0] * zoom))
    new_h = max(1, int(params['image_size'][1] * zoom))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 应用透明度
    if opacity < 1.0:
        r_ch, g_ch, b_ch, a_ch = img.split()
        a_ch = a_ch.point(lambda p: int(p * opacity))
        img = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch))

    # 旋转
    if rotation != 0:
        img = img.rotate(rotation, expand=True, fillcolor=(0, 0, 0, 0))

    if position == 'tile':
        cols = params['tile_cols']
        rows = params['tile_rows']
        grid_w = params['tile_grid_w'] * zoom
        grid_h = params['tile_grid_h'] * zoom

        for row in range(rows):
            for col in range(cols):
                cx = col * grid_w + grid_w / 2
                cy = row * grid_h + grid_h / 2
                if cx > overlay.width or cy > overlay.height:
                    continue
                px = int(cx - img.width / 2)
                py = int(cy - img.height / 2)
                overlay.paste(img, (px, py), img)
    else:
        margin = int(20 * zoom)
        if position == 'center':
            px = overlay.width // 2 - img.width // 2
            py = overlay.height // 2 - img.height // 2
        elif position == 'top-left':
            px = py = margin
        elif position == 'top-right':
            px = overlay.width - img.width - margin
            py = margin
        elif position == 'bottom-left':
            px = margin
            py = overlay.height - img.height - margin
        elif position == 'bottom-right':
            px = overlay.width - img.width - margin
            py = overlay.height - img.height - margin
        else:
            px = overlay.width // 2 - img.width // 2
            py = overlay.height // 2 - img.height // 2
        overlay.paste(img, (px, py), img)


def _render_preview_with_pil(pdf_path, params):
    """使用 PIL 叠加合成水印预览，比 PyMuPDF 逐 tile 绘制快 10-100 倍
    
    Args:
        pdf_path: PDF 文件路径
        params: 标准化水印参数字典（来自 normalize_watermark_params）
    
    Returns:
        {"success": True, "preview": "data:image/png;base64,..."}
    """
    try:
        t0 = time.time()

        # 1. 打开 PDF 并渲染第一页为 PIL Image（0.5x 分辨率）
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        zoom = 0.5
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        pil_page = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        doc.close()

        print(f"[_render_preview_with_pil] PDF页面已渲染为 {pix.width}x{pix.height} PIL图像")

        # 2. 创建透明叠加层
        overlay = Image.new("RGBA", (pix.width, pix.height), (0, 0, 0, 0))

        # 3. 应用水印
        wm_type = params['watermark_type']
        if wm_type == 'text' and params['text']:
            _pil_add_text_watermark(overlay, params, zoom)
        elif wm_type == 'image' and params['image_path'] and os.path.exists(params['image_path']):
            _pil_add_image_watermark(overlay, params, zoom)

        # 4. 合成
        pil_page_rgba = pil_page.convert("RGBA")
        result = Image.alpha_composite(pil_page_rgba, overlay)
        result = result.convert("RGB")

        # 5. 编码为 base64
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        t_elapsed = time.time() - t0
        print(f"[_render_preview_with_pil] 完成，耗时={t_elapsed:.2f}s")
        return {
            "success": True,
            "preview": f"data:image/png;base64,{b64}"
        }

    except Exception as e:
        import traceback
        print(f"[_render_preview_with_pil] 错误: {e}")
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}


# ===================================================================
# 生成水印预览（使用 PIL 快速像素合成引擎）
# ===================================================================

def generate_watermark_preview(pdf_path, watermark_type='text', text='印流PDflow', 
                               font_size=48, color='#888888', opacity=30, rotation=-45,
                               position='center', image_path='', scale=30, layer='over',
                               preview_mode=True):
    """生成带水印的预览图片（使用 PIL 像素合成引擎，速度比 PyMuPDF 快 10-100 倍）
    
    现在使用 PIL 引擎进行快速像素合成预览，与导出效果视觉一致。
    preview_mode 参数保留以兼容旧调用，但内部已改用了 PIL 引擎，
    不再降低密度，始终完整平铺。
    """
    try:
        t_start = time.time()

        # 1. 打开原始 PDF 获取页面尺寸
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        rect = page.rect
        doc.close()

        # 2. 使用统一参数标准化函数
        params = normalize_watermark_params(
            watermark_type=watermark_type,
            font_size=font_size,
            opacity=opacity,
            rotation=rotation,
            position=position,
            scale=scale,
            color=color,
            text=text,
            image_path=image_path,
            page_width=rect.width,
            page_height=rect.height,
            opacity_is_0_100=True
        )
        params['layer'] = layer

        # 3. 使用 PIL 引擎快速渲染预览
        result = _render_preview_with_pil(pdf_path, params)

        t_elapsed = time.time() - t_start
        print(f"[generate_watermark_preview] 完成，总耗时={t_elapsed:.2f}s")
        return result

    except Exception as e:
        import traceback
        print(f"[generate_watermark_preview] 错误: {e}")
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}


# ===================================================================
# 执行添加水印（旧版完整逻辑）
# ===================================================================

def do_watermark(pdf_path, output_path=None, watermark_type='text',
                 text='印流PDflow', font_size=48, color='#888888', opacity=0.3,
                 rotation=-45, position='center', layer='under',
                 image_path='', scale=30):
    """执行添加水印 - 接收完整参数对象
    
    支持两种调用方式:
    1. 对象方式: do_watermark(pdf_path, output_path, **params)
    2. 兼容方式: do_watermark(pdf_path, output_path, watermark_type=..., ...)
    """
    try:
        print(f"[do_watermark] 接收参数: pdf={pdf_path}, type={watermark_type}, opacity={opacity}, rotation={rotation}, position={position}, layer={layer}, scale={scale}")
        
        if not pdf_path:
            return {"success": False, "error": "请先选择PDF文件"}
        
        # 如果没有指定输出路径，则自动生成
        if not output_path:
            import os
            base_dir = os.path.dirname(pdf_path)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = os.path.join(base_dir, f"watermarked_{base_name}.pdf")
        
        # 调用添加水印方法
        result = add_watermark(
            filepath=pdf_path,
            output_path=output_path,
            watermark_type=watermark_type,
            text=text,
            font_size=font_size,
            color=color,
            opacity=opacity,
            rotation=rotation,
            position=position,
            layer=layer,
            image_path=image_path,
            scale=scale
        )
        
        return result
        
    except Exception as e:
        import traceback
        print(f"[do_watermark] 错误: {e}")
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}
