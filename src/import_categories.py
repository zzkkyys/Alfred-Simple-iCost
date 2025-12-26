#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCost Alfred Workflow - 从 Excel 导入分类
从 iCost 导出的账单 Excel 文件中读取分类信息
"""

import json
import sys
import os

WORKFLOW_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(WORKFLOW_DIR, "icost_data.json")

def load_data():
    """加载现有数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "accounts": [],
        "expense_categories": {},
        "income_categories": {}
    }

def save_data(data):
    """保存数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def import_from_excel(file_path):
    """从 Excel 文件导入分类"""
    try:
        import openpyxl
    except ImportError:
        return None, "请先安装 openpyxl: pip3 install openpyxl"
    
    if not os.path.exists(file_path):
        return None, f"文件不存在: {file_path}"
    
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        sheet = wb.active
        
        # 读取表头，找到对应列
        headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
        
        # 查找列索引
        type_col = None
        cat1_col = None
        cat2_col = None
        account_col = None
        
        for idx, header in enumerate(headers):
            if header:
                header_lower = str(header).lower()
                if '类型' in header_lower or 'type' in header_lower:
                    type_col = idx
                elif '一级分类' in header_lower or '分类' == header_lower:
                    cat1_col = idx
                elif '二级分类' in header_lower or '子分类' in header_lower:
                    cat2_col = idx
                elif '账户' in header_lower or 'account' in header_lower:
                    account_col = idx
        
        if cat1_col is None:
            # 尝试更宽松的匹配
            for idx, header in enumerate(headers):
                if header and '分类' in str(header):
                    if cat1_col is None:
                        cat1_col = idx
                    elif cat2_col is None:
                        cat2_col = idx
        
        # 读取数据
        expense_categories = {}
        income_categories = {}
        accounts = set()
        
        for row in sheet.iter_rows(min_row=2):
            # 获取类型（支出/收入）
            record_type = ""
            if type_col is not None and row[type_col].value:
                record_type = str(row[type_col].value).strip()
            
            # 获取一级分类
            cat1 = ""
            if cat1_col is not None and row[cat1_col].value:
                cat1 = str(row[cat1_col].value).strip()
            
            # 获取二级分类
            cat2 = ""
            if cat2_col is not None and row[cat2_col].value:
                cat2 = str(row[cat2_col].value).strip()
            
            # 获取账户
            if account_col is not None and row[account_col].value:
                accounts.add(str(row[account_col].value).strip())
            
            if not cat1:
                continue
            
            # 根据类型分类
            if '收入' in record_type or 'income' in record_type.lower():
                if cat1 not in income_categories:
                    income_categories[cat1] = []
                if cat2 and cat2 not in income_categories[cat1]:
                    income_categories[cat1].append(cat2)
            else:
                # 默认为支出
                if cat1 not in expense_categories:
                    expense_categories[cat1] = []
                if cat2 and cat2 not in expense_categories[cat1]:
                    expense_categories[cat1].append(cat2)
        
        wb.close()
        
        # 合并现有数据
        existing_data = load_data()
        
        # 合并账户
        all_accounts = list(set(list(existing_data.get("accounts", [])) + list(accounts)))
        
        # 合并分类
        for cat1, cat2_list in expense_categories.items():
            if cat1 in existing_data.get("expense_categories", {}):
                existing_data["expense_categories"][cat1] = list(set(
                    existing_data["expense_categories"][cat1] + cat2_list
                ))
            else:
                if "expense_categories" not in existing_data:
                    existing_data["expense_categories"] = {}
                existing_data["expense_categories"][cat1] = cat2_list
        
        for cat1, cat2_list in income_categories.items():
            if cat1 in existing_data.get("income_categories", {}):
                existing_data["income_categories"][cat1] = list(set(
                    existing_data["income_categories"][cat1] + cat2_list
                ))
            else:
                if "income_categories" not in existing_data:
                    existing_data["income_categories"] = {}
                existing_data["income_categories"][cat1] = cat2_list
        
        existing_data["accounts"] = all_accounts
        
        # 保存数据
        save_data(existing_data)
        
        expense_count = sum(len(v) for v in expense_categories.values())
        income_count = sum(len(v) for v in income_categories.values())
        
        return existing_data, f"导入成功！支出分类: {len(expense_categories)} 个一级分类，{expense_count} 个二级分类；收入分类: {len(income_categories)} 个一级分类，{income_count} 个二级分类；账户: {len(accounts)} 个"
        
    except Exception as e:
        return None, f"导入失败: {str(e)}"

def main():
    # 获取用户输入的文件路径
    query = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    
    items = []
    
    if query:
        # 用户提供了文件路径
        file_path = query
        
        # 处理路径中的 ~ 和空格
        file_path = os.path.expanduser(file_path)
        
        if os.path.exists(file_path):
            items.append({
                "uid": "import",
                "title": f"📥 导入分类: {os.path.basename(file_path)}",
                "subtitle": f"从 Excel 文件导入分类数据",
                "arg": file_path,
                "icon": {"path": "icon.png"},
                "valid": True
            })
        else:
            items.append({
                "uid": "not_found",
                "title": "⚠️ 文件不存在",
                "subtitle": f"请检查路径: {file_path}",
                "valid": False,
                "icon": {"path": "icon.png"}
            })
    else:
        # 显示使用说明
        items.append({
            "uid": "help",
            "title": "📥 导入 iCost 分类",
            "subtitle": "请输入 Excel 文件路径，或将文件拖拽到这里",
            "valid": False,
            "icon": {"path": "icon.png"}
        })
        
        items.append({
            "uid": "tip",
            "title": "💡 提示",
            "subtitle": "Excel 文件需包含: 类型、一级分类、二级分类 列",
            "valid": False,
            "icon": {"path": "icon.png"}
        })
    
    output = {"items": items}
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
