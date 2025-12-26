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
from icon_manager import get_icon_for_item, load_icons_list, preload_icons

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
    config = load_data(wf)
    
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
        # 预加载图标列表
        icons_list = load_icons_list()
        category_names = list(categories.keys())
        preload_icons(wf, category_names, icons_list)
        
        for cat1 in categories.keys():
            sub_categories = categories.get(cat1, [])
            sub_count = len(sub_categories)
            # 获取匹配的图标
            icon_path = get_icon_for_item(wf, cat1, icons_list)
            
            wf.add_item(
                title=f"{cat1}",
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
                icon=icon_path,
                valid=True
            )
    
    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
