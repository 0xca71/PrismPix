# -*- coding: utf-8 -*-
"""
模板引擎 — 加载 prompt_templates/ 目录下 25 个场景模板 JSON

提供:
    - 按 ID 查询模板
    - 按 variant key 获取变体覆盖
    - 按 category 获取品类提示
    - 构建注入 Stage3 的模板上下文 (examples, anti_ai_tips, defaults)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ecom_image_gen.logging_setup import LOG

# 模板目录 (相对于项目根目录)
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "prompt_templates"


class TemplateEngine:
    """加载并管理 25 个电商场景模板。

    用法:
        engine = TemplateEngine()
        tpl = engine.get("hero-image")
        ctx = engine.build_context("H1", category="fashion")
    """

    def __init__(self, templates_dir: str | Path | None = None):
        """初始化并加载所有模板。

        Args:
            templates_dir: 模板目录路径, 默认自动探测。
        """
        self._dir = Path(templates_dir) if templates_dir else _TEMPLATES_DIR
        self._templates: dict[str, dict] = {}
        self._loaded = False
        self._load_all()

    # ------------------------------------------------------------------
    # 加载
    # ------------------------------------------------------------------

    def _load_all(self) -> None:
        """加载目录下所有 .json 文件。"""
        if not self._dir.exists():
            LOG.warning("模板目录不存在: %s", self._dir)
            return
        for fp in sorted(self._dir.glob("*.json")):
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                tid = data.get("id", fp.stem)
                self._templates[tid] = data
            except Exception as exc:
                LOG.warning("跳过损坏模板 %s: %s", fp.name, exc)
        self._loaded = True
        LOG.info("模板引擎: 已加载 %d 个场景模板", len(self._templates))

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    def list_ids(self) -> list[str]:
        """返回所有模板 ID。"""
        return sorted(self._templates.keys())

    def get(self, template_id: str) -> dict | None:
        """按 ID 获取完整模板。"""
        return self._templates.get(template_id)

    def get_variant(self, template_id: str, variant_key: str) -> dict | None:
        """获取指定变体的 overrides dict。"""
        tpl = self.get(template_id)
        if not tpl:
            return None
        return tpl.get("variants", {}).get(variant_key)

    def get_category_tips(self, template_id: str, category: str) -> str | None:
        """获取某品类在该模板下的提示文本。"""
        tpl = self.get(template_id)
        if not tpl:
            return None
        tips = tpl.get("category_tips", {})
        # 模糊匹配: "女装连衣裙" -> 尝试 "fashion", "dresses" 等
        return tips.get(category, None)

    def get_examples(self, template_id: str) -> list[str]:
        """获取模板中的示例 prompt。"""
        tpl = self.get(template_id)
        if not tpl:
            return []
        return tpl.get("examples", [])

    def get_anti_ai_tips(self, template_id: str) -> str:
        """获取反 AI 痕迹提示。"""
        tpl = self.get(template_id)
        if not tpl:
            return ""
        return tpl.get("anti_ai_tips", "") or ""

    # ------------------------------------------------------------------
    # 构建上下文 (注入 Stage3)
    # ------------------------------------------------------------------

    def build_context(
        self,
        template_id: str,
        variant_key: str | None = None,
        category: str = "",
        product_name: str = "",
    ) -> str:
        """为 Stage3 构建单个模板的注入上下文。

        将模板的 prompt_template / defaults / examples / anti_ai_tips / variant
        编译为一段结构化的参考文本, 帮助 Stage3 模型生成高质量 prompt。

        Args:
            template_id: 模板 ID (如 "hero-image")。
            variant_key: 可选变体 key。
            category: 产品类目 (用于匹配 category_tips)。
            product_name: 产品名。

        Returns:
            可嵌入 LLM user message 的文本块。
        """
        tpl = self.get(template_id)
        if not tpl:
            return ""

        parts: list[str] = []
        parts.append(f"【{tpl.get('name', template_id)}】")

        # 变体覆盖 (合并为一行)
        if variant_key:
            variant = self.get_variant(template_id, variant_key)
            if variant:
                overrides = variant.get("overrides", {})
                if overrides:
                    ov_text = ", ".join(f"{k}={v}" for k, v in overrides.items())
                    parts.append(f"  variant[{variant.get('description', variant_key)}]: {ov_text}")

        # 品类提示 (一句)
        cat_tip = self.get_category_tips(template_id, category)
        if cat_tip:
            parts.append(f"  {category} tip: {cat_tip}")

        # 示例 prompt (最多 1 条, 截断)
        examples = self.get_examples(template_id)
        if examples:
            ex = examples[0]
            if len(ex) > 200:
                ex = ex[:200] + "..."
            parts.append(f"  example: {ex}")

        # 反 AI 痕迹 (仅保留关键模板, 且截断)
        anti_templates = {"model-showcase", "ugc-style", "magazine-editorial", "livestream"}
        if template_id in anti_templates:
            anti = self.get_anti_ai_tips(template_id)
            if anti:
                if len(anti) > 150:
                    anti = anti[:150] + "..."
                parts.append(f"  anti-AI: {anti}")

        return "\n".join(parts)

    def build_all_context(
        self,
        module_map: dict[str, dict],
        category: str = "",
        style: str = "",
        product_name: str = "",
    ) -> str:
        """为所有 14 个模块构建完整的模板上下文。

        Args:
            module_map: module_template_map 模块返回的映射 dict,
                        { "H1": {"template": "hero-image", "variant": "luxury"}, ... }
            category: 产品类目。
            style: 风格标签。
            product_name: 产品名。

        Returns:
            可嵌入 Stage3 user message 的完整上下文。
        """
        blocks: list[str] = []
        for code, info in module_map.items():
            tid = info.get("template", "")
            if not tid:
                continue
            # 风格可能映射到 variant
            variant = info.get("variant")
            if not variant and style:
                variant = self._resolve_variant(tid, style)
            ctx = self.build_context(tid, variant, category, product_name)
            if ctx:
                blocks.append(f"## 模块 {code}\n{ctx}")
        return "\n\n".join(blocks)

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------

    def _resolve_variant(self, template_id: str, style: str) -> str | None:
        """根据风格标签自动匹配最合适的 variant。"""
        tpl = self.get(template_id)
        if not tpl:
            return None
        variants = tpl.get("variants", {})
        style_lower = style.lower()
        # 直接匹配
        for vk in variants:
            if vk in style_lower or style_lower in vk:
                return vk
        # 模糊匹配 (中英文)
        style_map = {
            "luxury": "luxury", "奢华": "luxury", "高端": "luxury", "高级": "luxury",
            "简约": "minimal", "极简": "minimal", "清新": "fresh", "自然": "fresh",
            "科技": "tech", "运动": "athlete-action", "街头": "candid",
            "复古": "ccd-retro",
        }
        for tag, vk in style_map.items():
            if tag in style_lower:
                return vk
        return None
