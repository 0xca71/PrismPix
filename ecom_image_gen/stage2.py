# -*- coding: utf-8 -*-
"""
Stage 2: 营销策略生成

输入: product.json
输出: campaign.json — 高转化营销策略
"""

from __future__ import annotations

import json
from typing import Optional

from ecom_image_gen.cache import PromptCache
from ecom_image_gen.client import call_json_model, hash_key
from ecom_image_gen.config import Config
from ecom_image_gen.logging_setup import LOG

STAGE2_SYSTEM = (
    "你是资深电商营销策划。基于产品分析 JSON 产出高转化营销策略。"
    "只输出 JSON, 不要解释或 markdown。"
)

STAGE2_SCHEMA_KEYS = [
    "core_selling_point",
    "pain_points",
    "benefits",
    "usage_scenarios",
    "steps",
    "comparison_points",
    "trust_elements",
]


def stage2_generate_campaign(
    client,
    cfg: Config,
    product: dict,
    cache: Optional[PromptCache] = None,
) -> dict:
    """Stage 2: 由 product.json 生成 campaign.json。

    生成电商营销策略, 包含:
        - 核心卖点
        - 痛点/利益点
        - 使用场景
        - 使用步骤
        - 竞品对比点
        - 信任元素

    Args:
        client: openai.OpenAI 实例。
        cfg: 全局配置 (提供 text_model)。
        product: Stage1 产出的 product.json 内容。
        cache: 可选的 PromptCache。

    Returns:
        campaign.json 内容 dict。
    """
    LOG.info("Stage2: 营销策略生成中 ...")

    user_text = (
        "基于以下产品分析 JSON, 生成营销策略, 严格输出 JSON, 字段:\n"
        '{\n'
        '  "core_selling_point": "",\n'
        '  "pain_points": [],\n'
        '  "benefits": [],\n'
        '  "usage_scenarios": [],\n'
        '  "steps": [],\n'
        '  "comparison_points": [],\n'
        '  "trust_elements": []\n'
        '}\n\n'
        "产品分析 JSON:\n"
        + json.dumps(product, ensure_ascii=False, indent=2)
    )

    messages = [
        {"role": "system", "content": STAGE2_SYSTEM},
        {"role": "user", "content": user_text},
    ]

    data = call_json_model(
        client,
        cfg,
        cfg.text_model,
        messages,
        desc="Stage2 campaign",
        cache=cache,
        cache_key=f"stage2:{hash_key(json.dumps(product, sort_keys=True))}",
    )

    # 字段补全
    for k in STAGE2_SCHEMA_KEYS:
        if k not in data:
            data[k] = "" if k == "core_selling_point" else []

    LOG.info("Stage2 完成: %s", data.get("core_selling_point") or "(无卖点)")
    return data
