# -*- coding: utf-8 -*-
"""
模块-模板映射 — 将 14 个 H/D 模块映射到 25 个场景模板

每个模块有:
    - template: 默认模板 ID
    - variant: 默认变体 (可选)
    - category_map: 按品类的替代模板 { category: {template, variant} }
    - style_variants: 风格 → variant 的快速映射 (可选, 用于通用模块)

由 TemplateEngine 调用, 生成 Stage3 的模板上下文。
"""

from __future__ import annotations

# ── 风格 → variant (跨模块复用) ──────────────────────────────────
STYLE_TO_VARIANT: dict[str, str] = {
    "luxury": "luxury",
    "奢华": "luxury",
    "高端": "luxury",
    "高级": "luxury",
    "简约": "minimal",
    "极简": "minimal",
    "清新": "fresh",
    "自然": "natural",
    "科技": "tech",
    "运动": "athlete-action",
    "健身": "gym-power",
    "街头": "candid",
    "复古": "ccd-retro",
    "温馨": "cozy",
    "华丽": "golden-luxe",
    "节日": "festive",
}

# ── 品类映射 (中文类目 → 英文 category_tips key) ─────────────
_CATEGORY_ALIAS: dict[str, str] = {
    "女装": "fashion", "男装": "fashion", "服装": "fashion",
    "连衣裙": "fashion", "衬衫": "shirts", "外套": "coats",
    "针织": "knitwear", "t恤": "tshirts", "运动服": "activewear",
    "鞋": "shoes", "靴": "shoes", "运动鞋": "running_shoes",
    "包": "accessories", "配饰": "accessories",
    "美妆": "beauty", "护肤": "skincare", "香水": "fragrance",
    "彩妆": "makeup", "美发": "haircare",
    "珠宝": "jewelry", "首饰": "jewelry", "手表": "watch",
    "数码": "electronics", "电子": "electronics", "手机": "electronics",
    "电脑": "laptop", "耳机": "audio",
    "食品": "food", "零食": "food", "酒": "wine", "巧克力": "chocolate",
    "家居": "home", "家具": "furniture", "香薰": "candles",
    "运动": "sports", "健身": "fitness_equipment",
    "家电": "home_appliance",
}


def resolve_category(category_raw: str) -> str:
    """将中文类目解析为模板 category_tips 键。"""
    c = category_raw.strip().lower()
    for kw, key in _CATEGORY_ALIAS.items():
        if kw in c:
            return key
    # 回退: 尝试直接匹配模板中的 key
    return c or "fashion"


def resolve_variant(style_raw: str) -> str | None:
    """从风格文本解析 variant key。"""
    s = style_raw.strip().lower()
    for kw, vk in STYLE_TO_VARIANT.items():
        if kw in s:
            return vk
    return None


def get_module_map(category_raw: str = "", style_raw: str = "") -> dict[str, dict]:
    """获取 14 个模块的完整模板映射。

    Args:
        category_raw: 用户输入的类目 (中文/英文)。
        style_raw: 用户输入的风格标签 (中文/英文)。

    Returns:
        { module_code: {template, variant, category_key} }
    """
    cat = resolve_category(category_raw)
    style_variant = resolve_variant(style_raw)

    # ── 14 模块映射 ──────────────────────────────────────────
    base_map: dict[str, dict] = {

        # ============ H1-H5 主图 ============

        "H1": {
            "template": "hero-image",
            "variant": style_variant or "fresh",
            "category_map": {
                "jewelry": {"template": "luxury-atmospherics", "variant": "golden-luxe"},
                "fragrance": {"template": "luxury-atmospherics", "variant": "smoke-mystique"},
            },
        },

        "H2": {
            "template": "multi-angle-grid",
            "variant": "angle-view",
            "category_map": {
                "fashion": {"template": "ghost-mannequin", "variant": "white-clean"},
                "shirts": {"template": "ghost-mannequin", "variant": "editorial"},
                "dresses": {"template": "ghost-mannequin", "variant": "white-clean"},
            },
        },

        "H3": {
            "template": "model-showcase",
            "variant": style_variant or "fashion-full",
            "category_map": {
                "beauty": {"template": "model-showcase", "variant": "beauty-closeup"},
                "skincare": {"template": "model-showcase", "variant": "beauty-closeup"},
                "home": {"template": "lifestyle-scene", "variant": style_variant or "cozy"},
                "electronics": {"template": "lifestyle-scene", "variant": "outdoor"},
                "furniture": {"template": "try-on-virtual", "variant": "interior-luxury"},
                "sports": {"template": "sports-campaign", "variant": "athlete-action"},
                "food": {"template": "lifestyle-scene", "variant": "cozy"},
            },
        },

        "H4": {
            "template": "detail-macro",
            "variant": style_variant or "texture",
            "category_map": {
                "beauty": {"template": "detail-macro", "variant": "formula"},
                "skincare": {"template": "detail-macro", "variant": "formula"},
                "electronics": {"template": "exploded-view", "variant": "apple-style"},
                "fashion": {"template": "detail-macro", "variant": "craftsmanship"},
            },
        },

        "H5": {
            "template": "multi-angle-grid",
            "variant": "colorway",
            "category_map": {
                "beauty": {"template": "flat-lay", "variant": style_variant or "luxury"},
                "food": {"template": "flat-lay", "variant": "seasonal"},
                "fashion": {"template": "multi-angle-grid", "variant": "comparison"},
                "home": {"template": "flat-lay", "variant": "minimal"},
            },
        },

        # ============ D1-D9 详情图 ============

        "D1": {
            "template": "magazine-editorial",
            "variant": style_variant or "beauty-cover",
            "category_map": {
                "fashion": {"template": "magazine-editorial", "variant": "fashion-cover"},
                "fragrance": {"template": "luxury-atmospherics", "variant": "smoke-mystique"},
                "home": {"template": "lifestyle-scene", "variant": "luxury"},
                "sports": {"template": "sports-campaign", "variant": "product-hero"},
            },
        },

        "D2": {
            "template": "infographic",
            "variant": "feature-grid",
            "category_map": {
                "beauty": {"template": "detail-macro", "variant": "texture"},
                "fashion": {"template": "creative-concept", "variant": "minimal-art"},
                "electronics": {"template": "exploded-view", "variant": "blueprint"},
                "jewelry": {"template": "detail-macro", "variant": "craftsmanship"},
            },
        },

        "D3": {
            "template": "detail-macro",
            "variant": "craftsmanship",
            "category_map": {
                "beauty": {"template": "detail-macro", "variant": "formula"},
                "skincare": {"template": "detail-macro", "variant": "formula"},
                "electronics": {"template": "exploded-view", "variant": "editorial"},
                "fashion": {"template": "detail-macro", "variant": "texture"},
            },
        },

        "D4": {
            "template": "exploded-view",
            "variant": "apple-style",
            "category_map": {
                "fashion": {"template": "ghost-mannequin", "variant": "editorial-detail"},
                "beauty": {"template": "size-spec", "variant": "ritual-guide"},
                "food": {"template": "size-spec", "variant": "ritual-guide"},
                "home": {"template": "size-spec", "variant": "premium-editorial"},
            },
        },

        "D5": {
            "template": "lifestyle-scene",
            "variant": style_variant or "outdoor",
            "category_map": {
                "beauty": {"template": "lifestyle-scene", "variant": "morning"},
                "fashion": {"template": "model-showcase", "variant": "candid"},
                "electronics": {"template": "lifestyle-scene", "variant": "outdoor"},
                "sports": {"template": "sports-campaign", "variant": "athlete-action"},
                "food": {"template": "lifestyle-scene", "variant": "cozy"},
                "home": {"template": "lifestyle-scene", "variant": "cozy"},
            },
        },

        "D6": {
            "template": "lifestyle-scene",
            "variant": style_variant or "luxury",
            "category_map": {
                "fashion": {"template": "magazine-editorial", "variant": "minimal-editorial"},
                "beauty": {"template": "ugc-style", "variant": "grwm"},
                "food": {"template": "storefront", "variant": "interior"},
                "sports": {"template": "sports-campaign", "variant": "gym-power"},
            },
        },

        "D7": {
            "template": "before-after",
            "variant": style_variant or "simple",
            "category_map": {
                "beauty": {"template": "before-after", "variant": "clinical"},
                "fashion": {"template": "multi-angle-grid", "variant": "comparison"},
                "electronics": {"template": "size-spec", "variant": "technical"},
                "home": {"template": "size-spec", "variant": "premium-editorial"},
            },
        },

        "D8": {
            "template": "packaging",
            "variant": style_variant or "luxury-gift",
            "category_map": {
                "fashion": {"template": "ugc-style", "variant": "unboxing"},
                "electronics": {"template": "packaging", "variant": "unboxing"},
                "beauty": {"template": "packaging", "variant": "luxury-gift"},
                "food": {"template": "packaging", "variant": "minimal-eco"},
            },
        },

        "D9": {
            "template": "poster-banner",
            "variant": style_variant or "luxury",
            "category_map": {
                "beauty": {"template": "flat-lay", "variant": "luxury"},
                "fashion": {"template": "multi-product", "variant": "lineup"},
                "food": {"template": "flat-lay", "variant": "seasonal"},
                "home": {"template": "multi-product", "variant": "routine-set"},
                "sports": {"template": "sports-campaign", "variant": "triptych"},
            },
        },
    }

    # ── 应用品类覆盖 ──────────────────────────────────────────
    result: dict[str, dict] = {}
    for code, default_info in base_map.items():
        info = dict(default_info)  # 浅拷贝
        cat_map = info.pop("category_map", {})
        # 查找品类匹配
        cat_override = cat_map.get(cat, {})
        info["template"] = cat_override.get("template", info["template"])
        info["variant"] = cat_override.get("variant", info.get("variant"))
        info["category_key"] = cat
        result[code] = info

    return result
