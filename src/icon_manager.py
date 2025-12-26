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
from typing import Optional

from workflow.background import run_in_background

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


def find_icon_for_item(item_name: str, icons_list: Optional[list] = None) -> Optional[str]:
    """
    为给定的 item 名称查找匹配的图标文件名
    
    匹配规则：
    1. 文件名包含 item 名称（不区分大小写）
    2. 优先匹配完全包含的
    3. 优先选择带 color_ 前缀的彩色图标
    
    Args:
        item_name: 要匹配的名称（如账户名、分类名）
        icons_list: 图标列表，如果为 None 则从文件加载
    
    Returns:
        匹配的图标文件名，如果没有找到则返回 None
    """
    if icons_list is None:
        icons_list = load_icons_list()
    
    if not icons_list or not item_name:
        return None
    
    # 规范化名称：去掉末尾数字（如"餐饮1" -> "餐饮"）
    normalized_name = normalize_item_name(item_name)
    item_lower = normalized_name.lower()
    matches = []
    
    for icon_name in icons_list:
        # 从文件名中提取关键词（去除后缀和 _Normal@2x 等标记）
        base_name = icon_name.lower()
        # 移除常见后缀
        for suffix in ['_normal@3x.png', '_normal@2x.png', '_normal.png', '.png', '.jpg', '.icns']:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        
        # 检查是否匹配
        if item_lower in base_name or base_name in item_lower:
            matches.append(icon_name)
    
    if not matches:
        return None
    
    # 优先选择带 color_ 前缀的彩色图标
    color_matches = [m for m in matches if m.lower().startswith('color_')]
    if color_matches:
        # 优先选择更短的匹配（更精确）
        color_matches.sort(key=len)
        return color_matches[0]
    
    # 其次选择带 account_ 前缀的账户图标
    account_matches = [m for m in matches if m.lower().startswith('account_')]
    if account_matches:
        account_matches.sort(key=len)
        return account_matches[0]
    
    # 返回最短的匹配
    matches.sort(key=len)
    return matches[0]


def get_icon_cache_path(wf, icon_filename: str) -> str:
    """获取图标在缓存目录中的路径"""
    return os.path.join(wf.cachedir, "icons", icon_filename)


def get_icon_url(icon_filename: str) -> str:
    """获取图标的 GitHub 原始文件 URL"""
    encoded_filename = urllib.parse.quote(icon_filename)
    return f"{GITHUB_RAW_URL}/{encoded_filename}"


def start_icon_download(wf, icon_filename: str, cache_path: str):
    """
    启动单个图标的后台下载任务
    
    Args:
        wf: Workflow3 实例
        icon_filename: 图标文件名
        cache_path: 缓存路径
    """
    # 使用图标文件名作为任务名（确保唯一性）
    # 移除特殊字符避免问题
    task_name = f"dl_{icon_filename.replace('/', '_').replace(' ', '_')}"
    
    # 构建下载 URL
    icon_url = get_icon_url(icon_filename)
    
    # 使用 run_in_background 启动下载脚本
    cmd = [sys.executable, DOWNLOAD_SCRIPT, icon_url, cache_path]
    run_in_background(task_name, cmd)


def get_icon_for_item(wf, item_name: str, icons_list: Optional[list] = None) -> str:
    """
    获取 item 对应的图标路径
    
    如果缓存中存在则直接返回缓存路径
    如果不存在则触发后台下载并返回默认图标
    
    Args:
        wf: Workflow3 实例
        item_name: 要匹配的名称
        icons_list: 图标列表
    
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
    
    # 触发后台下载
    start_icon_download(wf, icon_filename, cache_path)
    
    # 设置 1 秒后自动重新运行，以便显示下载好的图标
    wf.rerun = 1.0
    
    # 返回默认图标
    return DEFAULT_ICON


def preload_icons(wf, item_names: list, icons_list: Optional[list] = None):
    """
    预加载多个 item 的图标
    为每个需要下载的图标启动独立的后台任务
    
    Args:
        wf: Workflow3 实例
        item_names: 要预加载的 item 名称列表
        icons_list: 图标列表
    """
    if icons_list is None:
        icons_list = load_icons_list()
    
    has_pending_downloads = False
    
    for item_name in item_names:
        icon_filename = find_icon_for_item(item_name, icons_list)
        
        if icon_filename:
            cache_path = get_icon_cache_path(wf, icon_filename)
            
            if not os.path.exists(cache_path):
                start_icon_download(wf, icon_filename, cache_path)
                has_pending_downloads = True
    
    # 如果有待下载的图标，设置自动重新运行
    if has_pending_downloads:
        wf.rerun = 1.0
