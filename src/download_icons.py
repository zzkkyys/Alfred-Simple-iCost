#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 图标下载脚本
用于在后台下载图标文件

用法: python download_icons.py <url> <cache_path>
"""

import os
import sys
import urllib.request
import urllib.error


def download(url: str, filepath: str):
    """
    下载文件到指定路径
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 下载文件
        urllib.request.urlretrieve(url, filepath)
    except Exception as e:
        # 记录错误日志到 Alfred debug console
        sys.stderr.write(f"Download failed: {e}\n")


if __name__ == "__main__":
    # 接收命令行参数
    # sys.argv[1] 是 URL
    # sys.argv[2] 是 目标保存路径
    if len(sys.argv) > 2:
        download(sys.argv[1], sys.argv[2])
