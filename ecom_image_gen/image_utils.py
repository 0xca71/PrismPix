# -*- coding: utf-8 -*-
"""
图片工具 — encode_image / to_image_ref / prepare_image_for_edit
"""

from __future__ import annotations

import base64
import mimetypes
import tempfile
from pathlib import Path


def encode_image(path: str) -> str:
    """把本地图片编码为 data URL (base64), 供 vision 模型使用。

    Args:
        path: 本地图片文件路径。

    Returns:
        形如 "data:image/jpeg;base64,<b64>" 的 data URL。

    Raises:
        FileNotFoundError: 图片文件不存在。
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"图片不存在: {path}")

    mime, _ = mimetypes.guess_type(str(p))
    mime = mime or "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def to_image_ref(image: str) -> str:
    """将图片引用统一为可传给 vision API 的格式。

    支持:
        - http(s) URL (原样返回)
        - data: URL (原样返回)
        - 本地文件路径 (自动编码为 base64 data URL)

    Args:
        image: 图片引用字符串。

    Returns:
        可直接用于 vision API image_url 字段的字符串。
    """
    if image.startswith(("http://", "https://", "data:")):
        return image
    return encode_image(image)


def prepare_image_for_edit(image: str) -> Path:
    """为 images.edit API 准备图片文件。

    本地文件直接返回路径; http(s) URL 先下载到临时文件。

    Args:
        image: 本地文件路径或 http(s) URL。

    Returns:
        本地文件 Path, 可直接传给 images.edit(image=open(path, "rb"))。

    Raises:
        FileNotFoundError: 本地文件不存在。
    """
    p = Path(image) if not image.startswith(("http://", "https://")) else None

    if p is not None:
        if not p.exists():
            raise FileNotFoundError(f"图片不存在: {image}")
        return p.resolve()

    # 下载远程图片到临时文件
    import requests

    suffix = ".png"
    # 尝试从 URL path 推断后缀
    url_path = image.split("?")[0]
    if "." in url_path.rsplit("/", 1)[-1]:
        ext = url_path.rsplit(".", 1)[-1].lower()
        if ext in ("jpg", "jpeg", "png", "webp", "gif"):
            suffix = f".{ext}"

    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        resp = requests.get(image, timeout=120)
        resp.raise_for_status()
        tmp.write(resp.content)
        tmp.close()
        return Path(tmp.name)
    except Exception:
        tmp.close()
        Path(tmp.name).unlink(missing_ok=True)
        raise
