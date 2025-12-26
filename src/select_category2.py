#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 二级分类选择脚本
选择后生成 URL Scheme 并执行
"""

import json
import sys
import os
import urllib.parse

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

def build_url(record_type, amount, account, category, remark=""):
    """构建 iCost URL Scheme"""
    base_url = f"iCost://{record_type}"
    
    params = {
        "amount": amount,
        "account": account,
        "category": category
    }
    
    if remark:
        params["remark"] = remark
    
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"

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
    category1 = data.get("category1", "")
    
    # 加载分类数据
    config = load_data()
    
    if record_type == "expense":
        categories = config.get("expense_categories", {})
        type_label = "消费"
    else:
        categories = config.get("income_categories", {})
        type_label = "收入"
    
    # 获取二级分类
    sub_categories = categories.get(category1, [])
    
    items = []
    
    if not sub_categories:
        # 如果没有二级分类，直接使用一级分类
        url = build_url(record_type, amount, account, category1, remark)
        items.append({
            "uid": f"cat2_direct",
            "title": f"✅ 直接记账: {category1}",
            "subtitle": f"{type_label} ¥{amount} | 账户: {account}",
            "arg": url,
            "icon": {"path": "icon.png"},
            "valid": True
        })
    else:
        for cat2 in sub_categories:
            # 使用二级分类名称（iCost 的 category 参数用二级分类）
            url = build_url(record_type, amount, account, cat2, remark)
            items.append({
                "uid": f"cat2_{cat2}",
                "title": f"📝 {cat2}",
                "subtitle": f"{type_label} ¥{amount} | {account} > {category1} > {cat2}",
                "arg": url,
                "icon": {"path": "icon.png"},
                "valid": True
            })
    
    output = {"items": items}
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
