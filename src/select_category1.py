#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 一级分类选择脚本
"""

import json
import sys
import os

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
    # 接收前一步传来的数据
    input_data = sys.argv[1] if len(sys.argv) > 1 else "{}"
    
    try:
        data = json.loads(input_data)
    except json.JSONDecodeError:
        data = {}
    
    record_type = data.get("type", "expense")
    amount = data.get("amount", "0")
    remark = data.get("remark", "")
    account = data.get("account", "")
    
    # 加载分类数据
    config = load_data()
    
    if record_type == "expense":
        categories = config.get("expense_categories", {})
        type_label = "消费"
    else:
        categories = config.get("income_categories", {})
        type_label = "收入"
    
    items = []
    
    if not categories:
        items.append({
            "uid": "no_category",
            "title": "⚠️ 暂无分类数据",
            "subtitle": "请先使用 icost:import 命令导入分类",
            "valid": False,
            "icon": {"path": "icon.png"}
        })
    else:
        for cat1 in categories.keys():
            sub_categories = categories.get(cat1, [])
            sub_count = len(sub_categories)
            items.append({
                "uid": f"cat1_{cat1}",
                "title": f"📁 {cat1}",
                "subtitle": f"{type_label} ¥{amount} | 账户: {account} | 包含 {sub_count} 个子分类",
                "arg": json.dumps({
                    "action": "select_category2",
                    "type": record_type,
                    "amount": amount,
                    "remark": remark,
                    "account": account,
                    "category1": cat1
                }),
                "icon": {"path": "icon.png"},
                "valid": True
            })
    
    output = {"items": items}
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
