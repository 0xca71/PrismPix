# -*- coding: utf-8 -*-
"""
Prompt 本地缓存 — 线程安全的 JSON 文件缓存
"""

from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Any, Optional

from ecom_image_gen.logging_setup import LOG


class PromptCache:
    """线程安全的本地 JSON 缓存, 以 (model, messages) 的 hash 为 key。

    用于避免重复调用 LLM, 支持断点续跑和 prompt 复用。
    """

    def __init__(self, path: Path, enabled: bool = True):
        """初始化缓存。

        Args:
            path: 缓存 JSON 文件路径。
            enabled: 是否启用缓存; False 时所有操作为空操作。
        """
        self.path = path
        self.enabled = enabled
        self._lock = threading.Lock()
        self._data: dict[str, Any] = {}

        if enabled and path.exists():
            try:
                self._data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                LOG.warning("缓存文件损坏, 重新初始化: %s", path)
                self._data = {}

    @staticmethod
    def key(model: str, messages: list, extra: str = "") -> str:
        """为 (model, messages, extra) 三元组生成稳定的 SHA-256 缓存键。

        Args:
            model: 模型名称。
            messages: chat messages 列表。
            extra: 额外标识信息。

        Returns:
            64 字符的十六进制 hash 字符串。
        """
        blob = json.dumps(
            {"m": model, "msg": messages, "x": extra},
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """从缓存读取。

        Args:
            key: 缓存键 (由 PromptCache.key() 生成)。

        Returns:
            缓存的值, 未命中返回 None。
        """
        if not self.enabled:
            return None
        with self._lock:
            return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        """写入缓存 (线程安全, 立即落盘)。

        Args:
            key: 缓存键。
            value: 任意可 JSON 序列化的值。
        """
        if not self.enabled:
            return
        with self._lock:
            self._data[key] = value
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
