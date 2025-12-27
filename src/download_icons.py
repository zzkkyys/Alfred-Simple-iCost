#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 图标下载脚本
用于在后台下载图标文件并转换为圆角矩形

用法: python download_icons.py <url> <cache_path>
"""

import os
import sys
import urllib.request
import urllib.error
import tempfile


def make_rounded_corners(image_path: str, radius: int = 20) -> bool:
    """
    将图标转换为圆角矩形
    
    Args:
        image_path: 图片文件路径
        radius: 圆角半径（默认20像素）
    
    Returns:
        是否成功转换
    """
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.stderr.write("PIL not installed, skipping rounded corners\n")
        return False
    
    try:
        # 打开图片
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        
        # 根据图片大小调整圆角半径（取宽高最小值的 1/5）
        auto_radius = min(width, height) // 5
        radius = min(radius, auto_radius) if auto_radius > 0 else radius
        
        # 创建圆角遮罩
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        # 绘制圆角矩形遮罩（白色区域会保留）
        draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=radius,
            fill=255
        )
        
        # 创建透明背景的新图片
        output = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # 应用遮罩
        output.paste(img, (0, 0), mask)
        
        # 保存为 PNG（支持透明）
        output.save(image_path, "PNG")
        return True
        
    except Exception as e:
        sys.stderr.write(f"Failed to apply rounded corners: {e}\n")
        return False


def download(url: str, filepath: str):
    """
    下载文件到指定路径，并转换为圆角矩形
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 下载文件到临时位置
        temp_path = filepath + ".tmp"
        urllib.request.urlretrieve(url, temp_path)
        
        # 转换为圆角矩形
        make_rounded_corners(temp_path)
        
        # 移动到最终位置
        os.rename(temp_path, filepath)
        
    except Exception as e:
        # 清理临时文件
        temp_path = filepath + ".tmp"
        if os.path.exists(temp_path):
            os.remove(temp_path)
        # 记录错误日志到 Alfred debug console
        sys.stderr.write(f"Download failed: {e}\n")


if __name__ == "__main__":
    # 支持两种模式：
    # 1. 单个下载: python download_icons.py <url> <cache_path>
    # 2. 批量下载: python download_icons.py --batch <json_file>
    
    if len(sys.argv) > 2:
        if sys.argv[1] == "--batch":
            # 批量下载模式
            import json
            tasks_file = sys.argv[2]
            
            if os.path.exists(tasks_file):
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                
                # 删除任务文件
                os.unlink(tasks_file)
                
                # 下载所有图标
                for task in tasks:
                    url = task.get("url")
                    path = task.get("path")
                    if url and path and not os.path.exists(path):
                        download(url, path)
        else:
            # 单个下载模式
            download(sys.argv[1], sys.argv[2])
