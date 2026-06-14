#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
印流 PDflow V1.1 公众号文章配图生成脚本
- 使用火山方舟接入点（Access Point）调用 Seedream 4.5
- 一次生成 4 张配图，并保存到 06-内容运营/ 目录
"""

import asyncio
import os
import httpx

# === 配置（已由用户授权使用）===
API_KEY = "ark-8229107f-922f-4448-8eb1-4cd6856e0b61-cea54"
MODEL_ID = "ep-20260613205419-kzxbm"   # 接入点 ID（用户在火山方舟控制台创建）
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "配图")

# === 4 张配图的 Prompt ===
IMAGES = [
    {
        "name": "01_前后对比_标题封面",
        "size": "2560x1440",
        "prompt": (
            "Split-screen comparison illustration: left side shows a low-quality blurry "
            "invoice PDF rendered as pixelated image with distorted unreadable text and "
            "broken table lines, right side shows a crisp high-quality text-based invoice "
            "PDF with sharp typography and clean aligned table rows. Modern minimalist tech "
            "illustration style, dark navy background #0B0E11 with subtle blue accent "
            "#4D7CFE, professional design, no text, no logo, no watermark."
        ),
    },
    {
        "name": "02_四项修复_四宫格",
        "size": "2560x1600",
        "prompt": (
            "2x2 grid of four flat modern feature icons on dark background #0B0E11: "
            "top-left is a dark/light mode toggle with moon and sun symbols, top-right "
            "is a contract document with checkmarks and signature seal, bottom-left is "
            "an invoice table with multiple aligned rows, bottom-right is a PDF export "
            "icon with downward arrow. All icons use blue accent color #4D7CFE, clean "
            "minimalist professional design, no text, no logo."
        ),
    },
    {
        "name": "03_截图vs文档_放大镜",
        "size": "2048x2048",
        "prompt": (
            "Close-up square illustration of a magnifying glass examining a split document: "
            "left half under the lens shows pixelated blurry bitmap text magnified into "
            "visible square pixels with jagged edges, right half shows crisp vector text "
            "with smooth sharp edges at the same magnification. Professional tech "
            "illustration, dark background with blue accent #4D7CFE, no text, no logo."
        ),
    },
    {
        "name": "04_三大功能_横向图标",
        "size": "2560x1440",
        "prompt": (
            "Three feature icons arranged horizontally on dark navy background #0B0E11: "
            "left is a template document icon with grid lines and form fields, middle is "
            "a layout/canvas icon with geometric shapes and grid, right is an export/"
            "download icon with downward arrow. Modern flat minimalist design, blue "
            "accent color #4D7CFE, professional tech style, no text, no logo. Leave clean "
            "space on the left side for product logo overlay."
        ),
    },
]


async def generate_one(client: httpx.AsyncClient, item: dict) -> dict:
    """调用 Seedream 4.5 接入点，生成单张图片并下载保存"""
    body = {
        "model": MODEL_ID,
        "prompt": item["prompt"],
        "size": item["size"],
        "response_format": "url",
        "watermark": False,
    }
    print(f"\n>>> 开始生成：{item['name']} ({item['size']})")
    resp = await client.post(
        "https://ark.cn-beijing.volces.com/api/v3/images/generations",
        json=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )
    result = resp.json()
    if resp.status_code != 200 or not result.get("data"):
        print(f"❌ 生成失败 [{resp.status_code}]: {result}")
        return {"name": item["name"], "ok": False, "error": result}

    image_url = result["data"][0].get("url")
    if not image_url:
        print(f"❌ 返回数据无 url: {result}")
        return {"name": item["name"], "ok": False, "error": "no url"}

    # 下载图片
    save_path = os.path.join(OUTPUT_DIR, f"{item['name']}.jpg")
    img_resp = await client.get(image_url)
    with open(save_path, "wb") as f:
        f.write(img_resp.content)
    print(f"✅ 已保存：{save_path}  ({len(img_resp.content) // 1024} KB)")
    return {"name": item["name"], "ok": True, "path": save_path, "url": image_url}


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"输出目录：{OUTPUT_DIR}")
    print(f"接入点：{MODEL_ID}")
    print(f"配图数量：{len(IMAGES)}")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=300) as client:
        results = []
        for item in IMAGES:
            r = await generate_one(client, item)
            results.append(r)

    # 汇总
    print("\n" + "=" * 60)
    print("生成结果汇总：")
    ok_count = sum(1 for r in results if r["ok"])
    for r in results:
        status = "✅" if r["ok"] else "❌"
        print(f"  {status} {r['name']}")
    print(f"\n成功 {ok_count}/{len(IMAGES)} 张")


if __name__ == "__main__":
    asyncio.run(main())
