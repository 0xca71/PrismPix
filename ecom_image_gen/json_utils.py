# -*- coding: utf-8 -*-
"""
JSON 工具 — 鲁棒解析 / Schema 校验 / 文件读写
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ecom_image_gen.logging_setup import LOG


def extract_json(text: str) -> Any:
    """从模型输出里鲁棒地抽取 JSON 对象。

    处理 ```json fenced``` 包裹、前后多余文字、单引号等常见脏数据。

    Args:
        text: 模型原始输出文本。

    Returns:
        解析后的 Python 对象 (通常为 dict)。

    Raises:
        ValueError: 无法从中解析出 JSON。
    """
    if text is None:
        raise ValueError("empty model output")

    s = text.strip()

    # 去掉 markdown 代码围栏
    fence = re.search(r"```(?:json)?\s*(.*?)```", s, re.DOTALL | re.IGNORECASE)
    if fence:
        s = fence.group(1).strip()

    # 直接尝试
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    # 截取第一个 { 到最后一个 } 之间的内容
    start, end = s.find("{"), s.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = s[start: end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # 末尾多余逗号修复
            cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
            return json.loads(cleaned)

    raise ValueError(f"无法从模型输出解析 JSON: {text[:200]!r}")


def validate_schema(obj: dict, required_keys: list[str], name: str) -> dict:
    """校验 dict 含必需键; 缺失键补默认空值并告警。

    Args:
        obj: 待校验的 dict。
        required_keys: 必须存在的键列表。
        name: 用于日志标识的名称 (如 "product.json")。

    Returns:
        校验并补全后的 dict。
    """
    if not isinstance(obj, dict):
        raise ValueError(f"{name} 不是 JSON 对象: {type(obj)}")

    for key in required_keys:
        if key not in obj:
            LOG.warning("[%s] 缺失字段 '%s', 自动补默认值", name, key)
            # 以 s / points / elements / features / scenarios / rules / constraints
            # 结尾的字段默认补空列表, 其他补空字符串
            obj[key] = (
                []
                if key.endswith(("s", "points", "elements", "features",
                                 "scenarios", "rules", "constraints"))
                else ""
            )
    return obj


def write_json(path: Path, obj: Any) -> None:
    """将对象以格式化 JSON 写入文件 (自动创建父目录)。

    Args:
        path: 目标文件路径。
        obj: 可 JSON 序列化的对象。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    """从文件读取 JSON。

    Args:
        path: JSON 文件路径。

    Returns:
        解析后的 Python 对象。
    """
    return json.loads(path.read_text(encoding="utf-8"))
