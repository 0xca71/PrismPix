# -*- coding: utf-8 -*-
"""
日志系统 — setup_logging() + 全局 LOG 实例
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

# 全局日志实例, 各模块通过 from ecom_image_gen.logging_setup import LOG 引用
LOG = logging.getLogger("ecom_image_gen")


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """初始化全局 logging 系统 (控制台 + 可选文件)。

    Args:
        level: 日志级别, 如 logging.INFO / logging.DEBUG。
        log_file: 可选的文件路径, 指定后同时输出到该文件。
    """
    LOG.setLevel(level)
    LOG.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(threadName)-10s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # 控制台 handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    LOG.addHandler(sh)

    # 可选文件 handler
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        LOG.addHandler(fh)

    LOG.propagate = False
