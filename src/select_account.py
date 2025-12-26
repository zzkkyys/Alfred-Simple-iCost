#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 账户选择脚本
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
    # 1. 从命令行参数获取
    # 2. 从标准输入获取
    # 3. 从环境变量获取
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
    
    # 加载账户列表
    config = load_data()
    accounts = config.get("accounts", ["微信", "支付宝", "现金", "银行卡"])
    
    type_label = "消费" if record_type == "expense" else "收入"
    
    for account in accounts:
        wf.add_item(
            title=f"📱 {account}",
            subtitle=f"使用 {account} 进行{type_label} ¥{amount}",
            arg=json.dumps({
                "action": "select_category1",
                "type": record_type,
                "amount": amount,
                "remark": remark,
                "account": account
            }),
            uid=f"account_{account}",
            icon="icon.png",
            valid=True
        )
    
    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
