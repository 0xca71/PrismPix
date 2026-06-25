# -*- coding: utf-8 -*-
"""
工作区管理 — SKU 隔离目录 + 产物落盘

输出目录结构:
    output/
      SKU_NAME/
        product.json
        campaign.json
        prompts.json
        prompts.md
        H1.png ... D9.png
"""

from __future__ import annotations

import re
from pathlib import Path

from ecom_image_gen.config import Config
from ecom_image_gen.json_utils import write_json
from ecom_image_gen.logging_setup import LOG
from ecom_image_gen.prompt_templates import render_prompts_markdown


def build_sku_workspace(cfg: Config, sku: str) -> Path:
    """创建并返回单个 SKU 的隔离工作目录。

    使用安全的目录名 (清洗特殊字符), 自动创建父目录。

    Args:
        cfg: 全局配置 (提供 output_root)。
        sku: SKU 名称 (可为任意字符串, 会被清洗)。

    Returns:
        SKU 工作目录的 Path。
    """
    safe = re.sub(r"[^\w.\-]+", "_", sku).strip("_") or "SKU"
    ws = Path(cfg.output_root) / safe
    ws.mkdir(parents=True, exist_ok=True)
    LOG.debug("SKU 工作区: %s", ws)
    return ws


def save_outputs(
    ws: Path,
    product: dict,
    campaign: dict,
    prompts: dict,
    sku: str,
) -> None:
    """保存所有文本产物到 SKU 工作区。

    写入 product.json / campaign.json / prompts.json / prompts.md。

    Args:
        ws: SKU 工作区目录。
        product: product.json 内容。
        campaign: campaign.json 内容。
        prompts: prompts.json 内容。
        sku: SKU 名称 (用于 Markdown 渲染)。
    """
    write_json(ws / "product.json", product)
    write_json(ws / "campaign.json", campaign)
    write_json(ws / "prompts.json", prompts)

    # 提取 Style Lock (从 H1 prompt 的 style_lock 字段)
    style_lock = ""
    h1 = prompts.get("H1", {})
    if isinstance(h1, dict):
        style_lock = h1.get("style_lock", "")

    md_content = render_prompts_markdown(sku, product, campaign, prompts, style_lock)
    (ws / "prompts.md").write_text(md_content, encoding="utf-8")

    LOG.info("文本产物已写入: %s", ws)
