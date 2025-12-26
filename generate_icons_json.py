#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 icons.json 文件
扫描 icons 目录下的所有图标文件，将文件名写入 src/icons.json
"""

import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(SCRIPT_DIR, "icons")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "src", "icons.json")


def main():
    """扫描 icons 目录并生成 icons.json"""
    if not os.path.exists(ICONS_DIR):
        print(f"错误: icons 目录不存在: {ICONS_DIR}")
        return
    
    # 获取所有图标文件名
    icons = []
    for filename in os.listdir(ICONS_DIR):
        # 只处理图片文件
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.icns')):
            icons.append(filename)
    
    # 按文件名排序
    icons.sort()
    
    # 写入 JSON 文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(icons, f, ensure_ascii=False, indent=2)
    
    print(f"已生成 {OUTPUT_FILE}")
    print(f"共找到 {len(icons)} 个图标文件")


if __name__ == "__main__":
    main()
