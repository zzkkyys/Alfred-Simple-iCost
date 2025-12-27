#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 图标管理模块
负责搜索匹配图标并从 GitHub 异步下载到缓存目录
"""

import os
import json
import sys
import re
import urllib.parse
from typing import Optional, Dict

from workflow.background import run_in_background, is_running

# GitHub 仓库信息
GITHUB_REPO = "zzkkyys/Alfred-Simple-iCost"
GITHUB_BRANCH = "main"
GITHUB_ICONS_PATH = "icons"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_ICONS_PATH}"

# 模块目录
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_JSON_PATH = os.path.join(MODULE_DIR, "icons.json")
DOWNLOAD_SCRIPT = os.path.join(MODULE_DIR, "download_icons.py")

# 默认图标
DEFAULT_ICON = "icon.png"

# 缓存：图标索引（避免每次都遍历）
_icons_index: Optional[Dict[str, str]] = None


def normalize_item_name(item_name: str) -> str:
    """
    规范化 item 名称
    如果名称是"中文+数字"的格式，去掉末尾的数字
    例如: "餐饮1" -> "餐饮", "交通123" -> "交通"
    
    Args:
        item_name: 原始名称
    
    Returns:
        规范化后的名称
    """
    if not item_name:
        return item_name
    
    # 匹配: 开头是中文，末尾是数字的情况
    # 使用正则表达式: 中文字符后面跟着数字结尾
    match = re.match(r'^([\u4e00-\u9fff]+)\d+$', item_name)
    if match:
        return match.group(1)
    
    return item_name


def load_icons_list() -> list:
    """加载图标列表"""
    if os.path.exists(ICONS_JSON_PATH):
        with open(ICONS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def build_icons_index(icons_list: list) -> Dict[str, str]:
    """
    构建图标索引，将关键词映射到图标文件名
    只在首次调用时构建，后续使用缓存
    
    Returns:
        Dict[关键词, 图标文件名]
    """
    index = {}
    
    for icon_name in icons_list:
        # 从文件名中提取关键词
        base_name = icon_name.lower()
        # 移除常见后缀
        for suffix in ['_normal@3x.png', '_normal@2x.png', '_normal.png', '.png', '.jpg', '.icns']:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        
        # 提取关键词（移除前缀如 color_, account_）
        keyword = base_name
        for prefix in ['color_', 'account_', 'icon_']:
            if keyword.startswith(prefix):
                keyword = keyword[len(prefix):]
                break
        
        # 存储到索引（优先 color_ 前缀）
        if keyword not in index:
            index[keyword] = icon_name
        elif icon_name.lower().startswith('color_') and not index[keyword].lower().startswith('color_'):
            # 优先使用 color_ 前缀的图标
            index[keyword] = icon_name
    
    return index


def get_icons_index() -> Dict[str, str]:
    """获取图标索引（使用缓存）"""
    global _icons_index
    if _icons_index is None:
        icons_list = load_icons_list()
        _icons_index = build_icons_index(icons_list)
    return _icons_index


def find_icon_for_item(item_name: str, icons_list: Optional[list] = None) -> Optional[str]:
    """
    为给定的 item 名称查找匹配的图标文件名（使用索引快速查找）
    
    Args:
        item_name: 要匹配的名称（如账户名、分类名）
        icons_list: 图标列表（已弃用，保留兼容性）
    
    Returns:
        匹配的图标文件名，如果没有找到则返回 None
    """
    if not item_name:
        return None
    
    # 规范化名称：去掉末尾数字（如"餐饮1" -> "餐饮"）
    normalized_name = normalize_item_name(item_name)
    item_lower = normalized_name.lower()
    
    # 使用索引快速查找
    index = get_icons_index()
    
    # 精确匹配
    if item_lower in index:
        return index[item_lower]
    
    # 部分匹配（关键词包含在 item 中，或 item 包含在关键词中）
    for keyword, icon_name in index.items():
        if item_lower in keyword or keyword in item_lower:
            return icon_name
    
    return None


def get_icon_cache_path(wf, icon_filename: str) -> str:
    """获取图标在缓存目录中的路径"""
    return os.path.join(wf.cachedir, "icons", icon_filename)


def get_icon_url(icon_filename: str) -> str:
    """获取图标的 GitHub 原始文件 URL"""
    encoded_filename = urllib.parse.quote(icon_filename)
    return f"{GITHUB_RAW_URL}/{encoded_filename}"


# 待下载队列（收集本次运行需要下载的图标）
_pending_downloads: list = []


def queue_icon_download(wf, icon_filename: str, cache_path: str):
    """
    将图标加入下载队列（不立即下载）
    
    Args:
        wf: Workflow3 实例
        icon_filename: 图标文件名
        cache_path: 缓存路径
    """
    global _pending_downloads
    icon_url = get_icon_url(icon_filename)
    _pending_downloads.append((icon_url, cache_path))


def flush_download_queue(wf):
    """
    启动后台任务下载所有队列中的图标（批量下载）
    """
    global _pending_downloads
    
    if not _pending_downloads:
        return
    
    # 检查是否已有下载任务在运行
    if is_running("icon_batch_download"):
        return
    
    # 将下载任务写入临时文件
    tasks_file = wf.cachefile("icon_download_tasks.json")
    tasks = [{"url": url, "path": path} for url, path in _pending_downloads]
    
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False)
    
    # 启动批量下载脚本
    cmd = [sys.executable, DOWNLOAD_SCRIPT, "--batch", tasks_file]
    run_in_background("icon_batch_download", cmd)
    
    # 清空队列
    _pending_downloads = []
    
    # 设置自动重新运行
    wf.rerun = 1.0


def get_icon_for_item(wf, item_name: str, icons_list: Optional[list] = None) -> str:
    """
    获取 item 对应的图标路径
    
    如果缓存中存在则直接返回缓存路径
    如果不存在则加入下载队列并返回默认图标
    
    Args:
        wf: Workflow3 实例
        item_name: 要匹配的名称
        icons_list: 图标列表（已弃用）
    
    Returns:
        图标路径（缓存路径或默认图标）
    """
    # 查找匹配的图标
    icon_filename = find_icon_for_item(item_name, icons_list)
    
    if not icon_filename:
        return DEFAULT_ICON
    
    # 检查缓存
    cache_path = get_icon_cache_path(wf, icon_filename)
    
    if os.path.exists(cache_path):
        return cache_path
    
    # 加入下载队列（不立即下载）
    queue_icon_download(wf, icon_filename, cache_path)
    
    # 返回默认图标
    return DEFAULT_ICON


def preload_icons(wf, item_names: list, icons_list: Optional[list] = None):
    """
    预加载多个 item 的图标
    收集所有需要下载的图标，最后批量启动下载
    
    Args:
        wf: Workflow3 实例
        item_names: 要预加载的 item 名称列表
        icons_list: 图标列表（已弃用）
    """
    for item_name in item_names:
        icon_filename = find_icon_for_item(item_name)
        
        if icon_filename:
            cache_path = get_icon_cache_path(wf, icon_filename)
            
            if not os.path.exists(cache_path):
                queue_icon_download(wf, icon_filename, cache_path)
    
    # 批量启动下载
    flush_download_queue(wf)
