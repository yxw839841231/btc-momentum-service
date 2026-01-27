"""
飞书多币种消息格式化器
创建富文本卡片，合并显示所有币种的分析信息
"""

from typing import List, Dict
from datetime import datetime


def format_multi_currency_card(all_results: List[Dict], index_url: str = "") -> Dict:
    """
    格式化多币种合并消息（飞书富文本卡片）

    Args:
        all_results: 所有币种的分析结果列表
        index_url: 索引页面链接

    Returns:
        飞书卡片数据
    """
    if not all_results:
        return {
            "title": "📊 动能分析报告",
            "content": "暂无分析数据",
            "btn_text": "",
            "btn_url": ""
        }

    # 提取时间戳
    timestamp = all_results[0]["analysis_result"].get("timestamp", "")
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass

    # 币种图标映射
    currency_icons = {
        'BTC': '₿', 'ETH': 'Ξ', 'SOL': '◎',
        'SUI': '◆', 'BNB': '◆', 'XRP': '✕',
        'ADA': '◆', 'DOGE': 'Ð', 'DOT': '◆',
        'MATIC': '◆', 'AVAX': '◆'
    }

    # 币种颜色映射（用于卡片元素）
    currency_colors = {
        'BTC': 'orange', 'ETH': 'blue', 'SOL': 'purple',
        'SUI': 'green', 'BNB': 'yellow', 'XRP': 'grey',
        'ADA': 'blue', 'DOGE': 'yellow', 'DOT': 'pink',
        'MATIC': 'purple', 'AVAX': 'red'
    }

    # 构建卡片元素
    card_elements = []

    # 1. 添加标题和时间
    card_elements.append({
        "tag": "div",
        "text": {
            "content": f"**📊 多币种动能分析报告**\n\n*更新时间: {timestamp}*\n\n---\n",
            "tag": "lark_md"
        }
    })

    # 2. 为每个币种创建一个区块
    for result in all_results:
        currency = result["currency"].upper()
        price_data = result["analysis_result"].get('currency_price', {}) or result["analysis_result"].get('btc_price', {})

        current_price = price_data.get('price', 'N/A')
        price_change = price_data.get('change_24h', 0)
        price_change_pct = price_data.get('change_24h_pct', 0)
        price_indicator = "📈" if price_change >= 0 else "📉"

        icon = currency_icons.get(currency, '●')
        color = currency_colors.get(currency, 'blue')

        # 币种区块
        currency_section = f"""
**{price_indicator} {icon} {currency}**

**当前价格**: ${current_price}
**24h 涨跌**: {price_change:+.2f} ({price_change_pct:+.2f}%)
"""

        card_elements.append({
            "tag": "div",
            "text": {
                "content": currency_section,
                "tag": "lark_md"
            }
        })

        # 添加分隔线（除了最后一个币种）
        if result != all_results[-1]:
            card_elements.append({
                "tag": "hr"
            })

    # 3. 添加操作按钮
    if index_url:
        card_elements.append({
            "tag": "div",
            "text": {
                "content": "\n---\n",
                "tag": "lark_md"
            }
        })

        card_elements.append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "content": "📈 查看所有报告",
                        "tag": "plain_text"
                    },
                    "url": index_url,
                    "type": "primary"
                }
            ]
        })

    # 4. 添加底部信息
    card_elements.append({
        "tag": "div",
        "text": {
            "content": "\n\n---\n*数据来源: OKX API | 动能分析服务*",
            "tag": "lark_md"
        }
    })

    return {
        "title": f"📊 多币种分析 ({len(all_results)} 个)",
        "elements": card_elements
    }


def format_multi_currency_compact(all_results: List[Dict], index_url: str = "") -> Dict:
    """
    格式化多币种紧凑版消息（表格形式）

    Args:
        all_results: 所有币种的分析结果列表
        index_url: 索引页面链接

    Returns:
        飞书卡片数据
    """
    if not all_results:
        return {
            "title": "📊 动能分析报告",
            "content": "暂无分析数据",
            "btn_text": "",
            "btn_url": ""
        }

    # 提取时间戳
    timestamp = all_results[0]["analysis_result"].get("timestamp", "")
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass

    currency_icons = {
        'BTC': '₿', 'ETH': 'Ξ', 'SOL': '◎',
        'SUI': '◆', 'BNB': '◆', 'XRP': '✕',
        'ADA': '◆', 'DOGE': 'Ð', 'DOT': '◆',
        'MATIC': '◆', 'AVAX': '◆'
    }

    # 构建表格
    table_header = "| 币种 | 价格 | 24h 涨跌 | 涨跌幅 |\n|------|------|---------|--------|\n"
    table_rows = ""

    for result in all_results:
        currency = result["currency"].upper()
        price_data = result["analysis_result"].get('currency_price', {}) or result["analysis_result"].get('btc_price', {})

        current_price = price_data.get('price', 'N/A')
        price_change = price_data.get('change_24h', 0)
        price_change_pct = price_data.get('change_24h_pct', 0)

        icon = currency_icons.get(currency, '●')
        indicator = "📈" if price_change >= 0 else "📉"

        table_rows += f"| {indicator} {icon} **{currency}** | ${current_price} | {price_change:+.2f} | {price_change_pct:+.2f}% |\n"

    # 构建完整内容
    content = f"""**📊 多币种动能分析**

*更新时间: {timestamp}*

{table_header}{table_rows}

---

"""

    if index_url:
        content += f"[📈 查看完整报告]({index_url})\n\n"

    content += "---\n*数据来源: OKX API | 动能分析服务*"

    return {
        "title": f"📊 多币种分析 ({len(all_results)} 个)",
        "content": content
    }
