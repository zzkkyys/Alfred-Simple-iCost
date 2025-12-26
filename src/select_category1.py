#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 一级分类选择脚本
"""

import json
import sys
import os

# 添加 workflow 包路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow import Workflow3

WORKFLOW_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(WORKFLOW_DIR, "icost_data.json")


def load_data():
    """加载分类和账户数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    with open("default_icost_data.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def main(wf):
    # 接收前一步传来的数据（支持多种方式）
    input_data = ""
    
    if wf.args:
        input_data = wf.args[0]
    elif not sys.stdin.isatty():
        input_data = sys.stdin.read().strip()
    
    wf.logger.debug(f"Received input: {input_data}")
    
    try:
        data = json.loads(input_data) if input_data else {}
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
    
    if not categories:
        wf.add_item(
            title="⚠️ 暂无分类数据",
            subtitle="请先使用 icost:import 命令导入分类",
            uid="no_category",
            icon="icon.png",
            valid=False
        )
    else:
        for cat1 in categories.keys():
            sub_categories = categories.get(cat1, [])
            sub_count = len(sub_categories)
            wf.add_item(
                title=f"📁 {cat1}",
                subtitle=f"{type_label} ¥{amount} | 账户: {account} | 包含 {sub_count} 个子分类",
                arg=json.dumps({
                    "action": "select_category2",
                    "type": record_type,
                    "amount": amount,
                    "remark": remark,
                    "account": account,
                    "category1": cat1
                }),
                uid=f"cat1_{cat1}",
                icon="icon.png",
                valid=True
            )
    
    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
