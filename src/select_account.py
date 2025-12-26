#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 账户选择脚本
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
        "expense_categories": {},
        "income_categories": {}
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
    
    # 加载账户列表
    config = load_data()
    accounts = config.get("accounts", ["微信", "支付宝", "现金", "银行卡"])
    
    items = []
    type_label = "消费" if record_type == "expense" else "收入"
    
    for account in accounts:
        items.append({
            "uid": f"account_{account}",
            "title": f"📱 {account}",
            "subtitle": f"使用 {account} 进行{type_label} ¥{amount}",
            "arg": json.dumps({
                "action": "select_category1",
                "type": record_type,
                "amount": amount,
                "remark": remark,
                "account": account
            }),
            "icon": {"path": "icon.png"},
            "valid": True
        })
    
    output = {"items": items}
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
