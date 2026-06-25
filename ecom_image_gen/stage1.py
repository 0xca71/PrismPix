# -*- coding: utf-8 -*-
"""
Stage 1: 产品视觉分析 (vision model)

输入: 产品图片 (base64 data URL 或 http URL)
输出: product.json — 严格结构的产品分析结果
"""

from __future__ import annotations

import json
from typing import Optional

from ecom_image_gen.cache import PromptCache
from ecom_image_gen.client import call_json_model, hash_key
from ecom_image_gen.config import Config, ProductInput
from ecom_image_gen.image_utils import to_image_ref
from ecom_image_gen.logging_setup import LOG

STAGE1_SYSTEM = (
    "你是资深电商产品视觉分析师。只能依据用户提供的图片进行客观描述, "
    "严禁臆造/幻想图片中不存在的结构、材质、颜色或配件。"
    "如某字段无法从图片确定, 用空数组或空字符串, 不要编造。"
    "只输出 JSON, 不要任何解释或 markdown 代码块。"
)

STAGE1_SCHEMA_KEYS = [
    "product_name",
    "category",
    "materials",
    "colors",
    "structure",
    "visible_features",
    "constraints",
]


def stage1_analyze_image(
    client,
    cfg: Config,
    image: str,
    product_hint: ProductInput,
    cache: Optional[PromptCache] = None,
) -> dict:
    """Stage 1: 基于图片产出严格结构的 product.json。

    使用 vision model 分析产品图片, 提取:
        - 产品名称、类目
        - 材质、颜色 (含 HEX 估计)
        - 结构特征、可见属性
        - 产品锁定约束 (不可修改形状/颜色)

    Args:
        client: openai.OpenAI 实例。
        cfg: 全局配置 (提供 vision_model, max_retries 等)。
        image: 图片路径或 URL。
        product_hint: 用户提供的补充信息 (类目/风格/模特属性)。
        cache: 可选的 PromptCache。

    Returns:
        product.json 内容 dict。
    """
    LOG.info("Stage1: 产品视觉分析中 ...")

    image_ref = to_image_ref(image)

    user_text = (
        "请分析这张产品图片, 输出严格 JSON, 字段如下:\n"
        '{\n'
        '  "product_name": "",\n'
        '  "category": "",\n'
        '  "materials": [],\n'
        '  "colors": [],\n'
        '  "structure": [],\n'
        '  "visible_features": [],\n'
        '  "constraints": ["do not modify product shape", "do not change colors"]\n'
        '}\n\n'
        "已知补充信息 (仅作参考, 不得与图片冲突):\n"
        f"- 类目: {product_hint.category or '未提供'}\n"
        f"- 风格: {product_hint.style or '未提供'}\n"
        f"- 模特属性: {product_hint.model_attrs or '未提供'}\n"
        f"- 额外需求: {product_hint.additional_requirements or '无'}\n"
        "colors 中尽量给出 HEX 估计值。如果额外需求中提到了色彩/材质/场景约束, "
        "请在 constraints 和 colors 字段中体现。constraints 必须保留产品锁定规则。"
    )

    messages = [
        {"role": "system", "content": STAGE1_SYSTEM},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_text},
                {"type": "image_url", "image_url": {"url": image_ref}},
            ],
        },
    ]

    data = call_json_model(
        client,
        cfg,
        cfg.vision_model,
        messages,
        desc="Stage1 product analysis",
        cache=cache,
        cache_key=f"stage1:{hash_key(image_ref, user_text)}",
    )

    # 字段补全 + constraints 强制存在
    for k in STAGE1_SCHEMA_KEYS:
        if k not in data:
            data[k] = [] if k != "product_name" and k != "category" else ""

    if not data.get("constraints"):
        data["constraints"] = [
            "do not modify product shape",
            "do not change colors",
        ]

    LOG.info("Stage1 完成: %s", data.get("product_name") or "(未命名)")
    return data
