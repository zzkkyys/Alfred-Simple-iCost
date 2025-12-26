# iCost 记账 Alfred Workflow

使用 iCost 的 URL Scheme 快速记账，支持消费和收入。

## 功能特点

- 💸 **消费记账**：快速记录支出
- 💰 **收入记账**：快速记录收入
- 📱 **账户选择**：选择付款/收款账户
- 📁 **分类选择**：支持一级分类和二级分类
- 📥 **Excel 导入**：从 iCost 导出的账单导入分类

## 使用方法

### 1. 记账（关键词：`ic`）

```
ic 金额 [备注]
```

**示例：**
- `ic 50` - 记录 50 元
- `ic 35.5 午餐` - 记录 35.5 元，备注"午餐"

**流程：**
1. 输入金额后回车
2. 选择"消费"或"收入"
3. 选择付款/收款账户
4. 选择一级分类
5. 选择二级分类
6. 自动打开 iCost 完成记账

### 2. 导入分类（关键词：`icost:import`）

```
icost:import /path/to/your/icost_export.xlsx
```

**说明：**
- 从 iCost 导出的 Excel 账单文件中读取分类
- Excel 文件需包含以下列：类型、一级分类、二级分类、账户
- 导入后会自动合并到现有分类数据库

## 文件结构

| 文件 | 说明 |
|------|------|
| `icost_main.py` | 主入口脚本 |
| `select_account.py` | 账户选择 |
| `select_category1.py` | 一级分类选择 |
| `select_category2.py` | 二级分类选择 |
| `import_categories.py` | 导入分类界面 |
| `do_import.py` | 执行导入操作 |
| `icost_data.json` | 分类和账户数据 |

## iCost URL Scheme 格式

### 支出
```
iCost://expense?amount=金额&account=账户&category=分类&remark=备注
```

### 收入
```
iCost://income?amount=金额&account=账户&category=分类&remark=备注
```

## 依赖

- Python 3
- openpyxl（仅导入 Excel 时需要）

安装 openpyxl：
```bash
pip3 install openpyxl
```

## 自定义分类

编辑 `icost_data.json` 文件可手动添加或修改分类和账户：

```json
{
  "accounts": ["微信", "支付宝", "现金"],
  "expense_categories": {
    "餐饮": ["早餐", "午餐", "晚餐"],
    "交通": ["公交", "地铁", "打车"]
  },
  "income_categories": {
    "工资": ["基本工资", "奖金"],
    "其他": ["红包", "报销"]
  }
}
```
