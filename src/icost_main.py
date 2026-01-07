#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 主入口脚本
支持消费(expense)和收入(income)记账
"""

import json
import sys
import os
import re

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

    def parse_amounts_and_remark(text: str) -> tuple[list[str], str]:
        """Parse leading amounts (space/Chinese-comma separated) and optional remark."""
        text = (text or "").strip()
        if not text:
            return [], ""

        # Normalize delimiters: Chinese comma and normal comma both act as separators
        normalized = text.replace("，", " ").replace(",", " ")
        tokens = [t for t in normalized.split() if t]

        amounts: list[str] = []
        remark_tokens: list[str] = []

        number_re = re.compile(r"^\d+(?:\.\d+)?$")

        for i, token in enumerate(tokens):
            if number_re.match(token):
                amounts.append(token)
            else:
                remark_tokens = tokens[i:]
                break

        remark = " ".join(remark_tokens).strip()
        return amounts, remark

    amounts, remark = parse_amounts_and_remark(query)
    amount = amounts[0] if amounts else ""

    # 验证金额是否为有效数字（支持多个）
    valid_amount = False
    if amounts:
        try:
            for a in amounts:
                float(a)
            valid_amount = True
            wf.setvar("last_amount", amount)
        except ValueError:
            valid_amount = False
    
    if valid_amount:
        # 金额有效，显示消费和收入选项
        wf.add_item(
            title=f"💸 消费 ¥{amount}" + (f" (共{len(amounts)}笔)" if len(amounts) > 1 else ""),
            subtitle=f"记录一笔支出" + (f" - 备注: {remark}" if remark else ""),
            arg=json.dumps({
                "action": "select_account",
                "type": "expense",
                "amount": amount,
                "amounts": amounts,
                "remark": remark
            }),
            uid="expense",
            icon="icon.png",
            valid=True
        )
        
        wf.add_item(
            title=f"💰 收入 ¥{amount}" + (f" (共{len(amounts)}笔)" if len(amounts) > 1 else ""),
            subtitle=f"记录一笔收入" + (f" - 备注: {remark}" if remark else ""),
            arg=json.dumps({
                "action": "select_account",
                "type": "income",
                "amount": amount,
                "amounts": amounts,
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
