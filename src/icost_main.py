#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 主入口脚本
支持消费(expense)和收入(income)记账
"""

import json
import sys
import os

# 获取脚本所在目录
WORKFLOW_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(WORKFLOW_DIR, "icost_data.json")

def load_data():
    """加载分类和账户数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "accounts": ["微信", "支付宝", "现金", "银行卡"],
        "expense_categories": {
            "餐饮": ["早餐", "午餐", "晚餐", "零食", "饮料"],
            "交通": ["公交", "地铁", "打车", "加油"],
            "购物": ["日用品", "服饰", "数码", "其他"],
            "娱乐": ["电影", "游戏", "运动", "其他"]
        },
        "income_categories": {
            "工资": ["基本工资", "奖金", "加班费"],
            "投资": ["股票", "基金", "理财"],
            "其他": ["红包", "报销", "兼职"]
        }
    }

def main():
    # 获取用户输入
    query = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    
    items = []
    
    # 解析输入，支持格式：金额 或 金额 备注
    parts = query.split(None, 1)
    amount = parts[0] if parts else ""
    remark = parts[1] if len(parts) > 1 else ""
    
    # 验证金额是否为有效数字
    try:
        if amount:
            float(amount)
            valid_amount = True
        else:
            valid_amount = False
    except ValueError:
        valid_amount = False
    
    if valid_amount:
        # 金额有效，显示消费和收入选项
        items.append({
            "uid": "expense",
            "title": f"💸 消费 ¥{amount}",
            "subtitle": f"记录一笔支出" + (f" - 备注: {remark}" if remark else ""),
            "arg": json.dumps({
                "action": "select_account",
                "type": "expense",
                "amount": amount,
                "remark": remark
            }),
            "icon": {"path": "icon.png"},
            "valid": True
        })
        
        items.append({
            "uid": "income",
            "title": f"💰 收入 ¥{amount}",
            "subtitle": f"记录一笔收入" + (f" - 备注: {remark}" if remark else ""),
            "arg": json.dumps({
                "action": "select_account",
                "type": "income",
                "amount": amount,
                "remark": remark
            }),
            "icon": {"path": "icon.png"},
            "valid": True
        })
    else:
        # 显示使用说明
        items.append({
            "uid": "help",
            "title": "输入金额开始记账",
            "subtitle": "格式: 金额 [备注] 例如: 50 午餐",
            "valid": False,
            "icon": {"path": "icon.png"}
        })
    
    output = {"items": items}
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
