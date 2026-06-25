# -*- coding: utf-8 -*-
"""
Campaign Style Lock — 整套图的视觉合同

GPT-Image-2 铁律要求: 多图任务必须先锁定色板/冷暖调/字体/背景/光线/布局,
每张图 Prompt 首段必须复用同一段 Style Lock, 禁止单张图漂移。
"""

from __future__ import annotations

from ecom_image_gen.module_template_map import resolve_category

# ── 按品类预设色板 ──
_CATEGORY_PALETTES: dict[str, dict] = {
    "beauty": {
        "bg": "#FFFFFF",
        "text": "#2D2D2D",
        "accent": "#C9A88C",
        "secondary": "#F5F1E8",
        "tone": "warm neutral, 5000K",
    },
    "skincare": {
        "bg": "#FAF7F2",
        "text": "#2D2D2D",
        "accent": "#7A9E7E",
        "secondary": "#E8E0D5",
        "tone": "warm, 4800K",
    },
    "fashion": {
        "bg": "#FFFFFF",
        "text": "#1A1A1A",
        "accent": "#8B6F47",
        "secondary": "#F5F0EB",
        "tone": "neutral-cool, 5500K",
    },
    "jewelry": {
        "bg": "#1A1A1A",
        "text": "#F5F0EB",
        "accent": "#D4AF37",
        "secondary": "#2D2D2D",
        "tone": "warm, 4500K, dramatic",
    },
    "electronics": {
        "bg": "#F5F5F5",
        "text": "#1A1A1A",
        "accent": "#0066CC",
        "secondary": "#E8E8E8",
        "tone": "cool, 5600K",
    },
    "food": {
        "bg": "#FAFAF5",
        "text": "#3D2B1F",
        "accent": "#D4A574",
        "secondary": "#F0E6D3",
        "tone": "warm, 4500K",
    },
    "home": {
        "bg": "#F7F5F2",
        "text": "#2D2D2D",
        "accent": "#A89F91",
        "secondary": "#E8E3DC",
        "tone": "warm neutral, 5000K",
    },
    "sports": {
        "bg": "#FFFFFF",
        "text": "#1A1A1A",
        "accent": "#FF4444",
        "secondary": "#F0F0F0",
        "tone": "cool, 5600K, high contrast",
    },
    # 默认
    "_default": {
        "bg": "#FFFFFF",
        "text": "#2D2D2D",
        "accent": "#7A9E7E",
        "secondary": "#F5F1E8",
        "tone": "neutral-cool, 5500K",
    },
}


def get_palette(category_raw: str) -> dict:
    """根据品类获取预设色板。"""
    cat = resolve_category(category_raw)
    return _CATEGORY_PALETTES.get(cat, _CATEGORY_PALETTES["_default"])


def generate_style_lock(
    category: str = "",
    style: str = "",
    product_name: str = "",
) -> dict:
    """生成 Campaign Style Lock (整套图的视觉合同)。

    包含 10 个必填字段:
        visual_direction, palette, tone, font_system, background_system,
        lighting_system, layout_system, icon_system, product_presentation,
        no_drift_items

    Args:
        category: 产品类目。
        style: 风格标签。
        product_name: 产品名。

    Returns:
        Style Lock dict, 字段见上面列表。
    """
    p = get_palette(category)
    style_lower = (style or "").lower()

    # 根据风格微调
    if "luxury" in style_lower or "奢华" in style_lower or "高端" in style_lower:
        p = {**p, "tone": "warm, 4500K, cinematic", "accent": p.get("accent", "#D4AF37")}
    elif "简约" in style_lower or "极简" in style_lower:
        p = {**p, "bg": "#FFFFFF", "tone": "neutral-cool, 5600K"}

    lock = {
        "visual_direction": f"premium {category or 'product'} ecommerce",
        "palette": {
            "background": p["bg"],
            "text": p["text"],
            "accent": p["accent"],
            "secondary_accent": p["secondary"],
        },
        "tone": p["tone"],
        "font_system": "headlines: Didot serif; body/labels: SF Pro Display sans-serif; no third font family",
        "background_system": f"primary: {p['bg']} clean studio; alternate 1: {p['secondary']}; alternate 2: {p['bg']}; strict rotation across images",
        "lighting_system": f"{p['tone']} studio lighting; consistent shadow softness and direction across all images",
        "layout_system": (
            "generous whitespace (45-50%+); rounded rectangular info labels "
            "(8px corner radius); clean grid-based layouts; "
            "consistent margin/padding across all screens"
        ),
        "icon_system": (
            "thin-line icons, 2px stroke weight, consistent style; "
            f"color: {p['accent']}; no filled icons, no mixed icon styles"
        ),
        "product_presentation": (
            "stable product scale and placement; "
            "product material and finish consistently rendered; "
            "product angle varies per screen per multi-angle rules"
        ),
        "no_drift_items": [
            "no color palette changes",
            "no mixed font families",
            "no random backgrounds",
            "no inconsistent lighting direction or color temperature",
            "no mismatched icon styles",
            "no decoration style drift",
            "no product proportion changes",
        ],
    }
    return lock


def render_style_lock_text(lock: dict) -> str:
    """将 Style Lock dict 渲染为一段英文文本 (每张图 Prompt 首段)。

    Args:
        lock: generate_style_lock() 的返回 dict。

    Returns:
        可嵌入 Prompt 首段的 Campaign Style Lock 文本。
    """
    p = lock["palette"]
    parts = [
        "Campaign Style Lock:",
        f"consistent {lock['visual_direction']} visual system across entire set;",
        f"fixed palette: bg {p['background']}, text {p['text']}, "
        f"accent {p['accent']}, secondary {p['secondary_accent']};",
        f"tone: {lock['tone']};",
        f"fonts: {lock['font_system']};",
        f"backgrounds: {lock['background_system']};",
        f"lighting: {lock['lighting_system']};",
        f"layout: {lock['layout_system']};",
        f"icons: {lock['icon_system']};",
        f"product: {lock['product_presentation']};",
        "STRICTLY NO: " + "; ".join(lock["no_drift_items"]) + ".",
    ]
    return " ".join(parts)
