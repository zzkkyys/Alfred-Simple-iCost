#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 使用频率记录模块
记录账户和分类的使用频率，用于智能排序
"""

import json
import os
import sys
import urllib.parse
from typing import Dict, List, Optional

# 添加 workflow 包路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow import Workflow3

# 频率数据文件名
FREQUENCY_FILENAME = "usage_frequency.json"


def get_frequency_file_path(wf) -> str:
    """获取频率数据文件路径"""
    return wf.cachefile(FREQUENCY_FILENAME)


def load_frequency_data(wf) -> Dict:
    """
    加载使用频率数据
    
    Returns:
        {
            "accounts": {"微信": 10, "支付宝": 5, ...},
            "categories": {"餐饮": 20, "交通": 15, ...}
        }
    """
    freq_file = get_frequency_file_path(wf)
    if os.path.exists(freq_file):
        try:
            with open(freq_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    return {
        "accounts": {},
        "categories": {}
    }


def save_frequency_data(wf, data: Dict):
    """保存使用频率数据"""
    freq_file = get_frequency_file_path(wf)
    with open(freq_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_usage(wf, account: str, category: str):
    """
    记录一次使用
    
    Args:
        wf: Workflow3 实例
        account: 账户名
        category: 分类名（二级分类）
    """
    data = load_frequency_data(wf)
    
    # 更新账户频率
    if account:
        data["accounts"][account] = data["accounts"].get(account, 0) + 1
    
    # 更新分类频率
    if category:
        data["categories"][category] = data["categories"].get(category, 0) + 1
    
    save_frequency_data(wf, data)


def parse_icost_url(url: str) -> Dict[str, str]:
    """
    解析 iCost x-callback-url，提取账户和分类
    
    URL 格式: iCost://expense?amount=100&account=微信&category=餐饮&x-success=...
    
    Args:
        url: iCost URL Scheme
    
    Returns:
        {"account": "微信", "category": "餐饮", ...}
    """
    result = {}
    
    try:
        # 解析 URL
        parsed = urllib.parse.urlparse(url)
        
        # 获取查询参数
        params = urllib.parse.parse_qs(parsed.query)
        
        # 提取账户和分类（parse_qs 返回列表，取第一个值）
        if "account" in params:
            result["account"] = params["account"][0]
        if "category" in params:
            result["category"] = params["category"][0]
        if "amount" in params:
            result["amount"] = params["amount"][0]
        
        # 记录类型（expense/income）
        result["type"] = parsed.netloc or parsed.path.strip("/")
        
    except Exception as e:
        sys.stderr.write(f"Failed to parse URL: {e}\n")
    
    return result


def record_from_url(wf, url: str):
    """
    从 iCost URL 解析并记录使用频率
    
    Args:
        wf: Workflow3 实例
        url: iCost x-callback-url
    """
    parsed = parse_icost_url(url)
    account = parsed.get("account", "")
    category = parsed.get("category", "")
    
    if account or category:
        record_usage(wf, account, category)
        wf.logger.info(f"Recorded usage: account={account}, category={category}")


def sort_by_frequency(wf, items: List[str], item_type: str = "accounts") -> List[str]:
    """
    按使用频率排序列表
    
    Args:
        wf: Workflow3 实例
        items: 要排序的项目列表
        item_type: 类型 ("accounts" 或 "categories")
    
    Returns:
        按频率降序排列的列表
    """
    data = load_frequency_data(wf)
    freq_dict = data.get(item_type, {})
    
    # 按频率降序排序，频率相同则保持原顺序
    return sorted(items, key=lambda x: freq_dict.get(x, 0), reverse=True)


def main(wf):
    """
    主入口 - 接收 URL 并记录使用频率
    
    用法: 在 Alfred 中配置 Run Script，将选中的 URL 传入
    """
    if not wf.args:
        print("❌ 未提供 URL")
        return
    
    url = wf.args[0].strip()
    
    if url:
        record_from_url(wf, url)
        print("✅ 已记录使用频率")
    else:
        print("❌ URL 为空")


if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
