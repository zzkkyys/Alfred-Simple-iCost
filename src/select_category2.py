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

# 添加 workflow 包路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow import Workflow3
from icon_manager import get_icon_for_item, preload_icons, flush_download_queue
from habbit import sort_by_frequency

DATA_FILENAME = "icost_data.json"

# 记账成功后的回调 URL（调用快捷指令"记账提醒"）
X_SUCCESS_URL = "shortcuts://run-shortcut?name=iCostNotify"
X_ERROR_URL = "shortcuts://run-shortcut?name=iCostError&"


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


def build_url(record_type, amount, account, category, remark=""):
    """构建 iCost x-callback-url Scheme（进行 URL 编码）"""
    base_url = f"iCost://{record_type}"
    
    params = {
        "amount": amount,
        "account": account,
        "category": category,
        "x-success": X_SUCCESS_URL,
        "x-error": X_ERROR_URL
    }
    
    if remark:
        params["remark"] = remark
    
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"


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
    category1 = data.get("category1", "")
    
    # 加载分类数据
    config = load_data(wf)
    
    if record_type == "expense":
        categories = config.get("expense_categories", {})
        type_label = "消费"
    else:
        categories = config.get("income_categories", {})
        type_label = "收入"
    
    # 获取二级分类
    sub_categories = categories.get(category1, [])
    
    if not sub_categories:
        # 如果没有二级分类，直接使用一级分类
        url = build_url(record_type, amount, account, category1, remark)
        icon_path = get_icon_for_item(wf, category1)
        
        wf.add_item(
            title=f"✅ 直接记账: {category1}",
            subtitle=f"{type_label} ¥{amount} | 账户: {account}",
            arg=url,
            uid="cat2_direct",
            icon=icon_path,
            valid=True
        )
    else:
        # 按使用频率排序
        sub_categories = sort_by_frequency(wf, sub_categories, "categories")
        
        # 预加载所有二级分类的图标
        preload_icons(wf, sub_categories)
        
        for cat2 in sub_categories:
            # 使用二级分类名称（iCost 的 category 参数用二级分类）
            url = build_url(record_type, amount, account, cat2, remark)
            icon_path = get_icon_for_item(wf, cat2)
            
            wf.add_item(
                title=f"{cat2}",
                subtitle=f"{type_label} ¥{amount} | {account} > {category1} > {cat2}",
                arg=url,
                uid=f"cat2_{cat2}",
                icon=icon_path,
                valid=True
            )
    
    # 启动批量下载
    flush_download_queue(wf)
    
    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
