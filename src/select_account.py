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
from icon_manager import get_icon_for_item, preload_icons, flush_download_queue

DATA_FILENAME = "icost_data.json"


def load_data(wf):
    """加载分类和账户数据（从 cache 目录）"""
    data_file = wf.cachefile(DATA_FILENAME)
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 返回默认数据
    return {
        "accounts": ["微信", "支付宝", "现金", "银行卡"],
        "expense_categories": {},
        "income_categories": {}
    }


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
    config = load_data(wf)
    accounts = config.get("accounts", ["微信", "支付宝", "现金", "银行卡"])
    
    # 预加载所有账户的图标
    preload_icons(wf, accounts)
    
    type_label = "消费" if record_type == "expense" else "收入"
    
    for account in accounts:
        # 获取匹配的图标
        icon_path = get_icon_for_item(wf, account)
        
        wf.add_item(
            title=f"{account}",
            subtitle=f"使用 {account} 进行{type_label} ¥{amount}",
            arg=json.dumps({
                "action": "select_category1",
                "type": record_type,
                "amount": amount,
                "remark": remark,
                "account": account
            }),
            uid=f"account_{account}",
            icon=icon_path,
            valid=True
        )
    
    # 启动批量下载
    flush_download_queue(wf)
    
    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
