#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 主入口脚本
支持消费(expense)和收入(income)记账
"""

import json
import sys
import os

# 添加 workflow 包路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow import Workflow3

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
    # 获取用户输入
    query = wf.args[0].strip() if wf.args else ""
    
    # 解析输入，支持格式：金额 或 金额 备注
    parts = query.split(None, 1)
    amount = parts[0] if parts else ""
    remark = parts[1] if len(parts) > 1 else ""
    
    # 验证金额是否为有效数字
    try:
        if amount:
            float(amount)
            valid_amount = True
            wf.setvar("last_amount", amount)
        else:
            valid_amount = False
    except ValueError:
        valid_amount = False
    
    if valid_amount:
        # 金额有效，显示消费和收入选项
        wf.add_item(
            title=f"💸 消费 ¥{amount}",
            subtitle=f"记录一笔支出" + (f" - 备注: {remark}" if remark else ""),
            arg=json.dumps({
                "action": "select_account",
                "type": "expense",
                "amount": amount,
                "remark": remark
            }),
            uid="expense",
            icon="icon.png",
            valid=True
        )
        
        wf.add_item(
            title=f"💰 收入 ¥{amount}",
            subtitle=f"记录一笔收入" + (f" - 备注: {remark}" if remark else ""),
            arg=json.dumps({
                "action": "select_account",
                "type": "income",
                "amount": amount,
                "remark": remark
            }),
            uid="income",
            icon="icon.png",
            valid=True
        )
    else:
        # 显示使用说明
        wf.add_item(
            title="输入金额开始记账",
            subtitle="格式: 金额 [备注] 例如: 50 午餐",
            uid="help",
            icon="icon.png",
            valid=False
        )
    
    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
