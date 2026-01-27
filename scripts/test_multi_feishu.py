#!/usr/bin/env python3
"""
测试飞书多币种合并消息
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.feishu_bot import FeishuBot


def create_mock_results():
    """创建模拟的多币种结果"""
    currencies = [
        {
            "currency": "BTC",
            "analysis_result": {
                'currency': 'BTC',
                'currency_price': {
                    'price': '98,456.78',
                    'change_24h': 1234.56,
                    'change_24h_pct': 1.27,
                    'exchange': 'OKX'
                },
                'timestamp': '2026-01-27T21:00:00',
                'status': 'success'
            },
            "report_path": "reports/btc_analysis.html"
        },
        {
            "currency": "SUI",
            "analysis_result": {
                'currency': 'SUI',
                'currency_price': {
                    'price': '1.50',
                    'change_24h': 0.02,
                    'change_24h_pct': 1.35,
                    'exchange': 'OKX'
                },
                'timestamp': '2026-01-27T21:00:00',
                'status': 'success'
            },
            "report_path": "reports/sui_analysis.html"
        },
        {
            "currency": "SOL",
            "analysis_result": {
                'currency': 'SOL',
                'currency_price': {
                    'price': '150.25',
                    'change_24h': -3.50,
                    'change_24h_pct': -2.28,
                    'exchange': 'OKX'
                },
                'timestamp': '2026-01-27T21:00:00',
                'status': 'success'
            },
            "report_path": "reports/sol_analysis.html"
        }
    ]
    return currencies


def test_multi_currency_format():
    """测试多币种格式化"""
    print("="*60)
    print("飞书多币种合并消息 - 格式预览")
    print("="*60)

    from src.feishu_multi_formatter import format_multi_currency_card

    all_results = create_mock_results()

    print(f"\n币种数量: {len(all_results)}")
    print(f"币种列表: {', '.join([r['currency'] for r in all_results])}")

    # 生成富文本卡片
    card_data = format_multi_currency_card(all_results, index_url="https://example.com/")

    print(f"\n标题: {card_data['title']}")
    print(f"\n卡片元素数量: {len(card_data['elements'])}")

    print("\n" + "-"*60)
    print("卡片内容预览:")
    print("-"*60)

    for i, element in enumerate(card_data['elements'], 1):
        if element.get('tag') == 'div':
            content = element.get('text', {}).get('content', '')
            # 只显示前100个字符
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"\n[{i}] DIV 元素:")
            print(f"    {preview}")
        elif element.get('tag') == 'hr':
            print(f"\n[{i}] 分隔线")
        elif element.get('tag') == 'action':
            actions = element.get('actions', [])
            print(f"\n[{i}] 操作按钮:")
            for action in actions:
                text = action.get('text', {}).get('content', '')
                print(f"    - {text}")


def test_send_to_feishu():
    """测试发送到飞书"""
    print("\n" + "="*60)
    print("发送到飞书测试")
    print("="*60)

    webhook_url = os.environ.get("FEISHU_WEBHOOK_URL")

    if not webhook_url:
        print("\n⚠️  未设置 FEISHU_WEBHOOK_URL 环境变量")
        print("只显示格式预览，不实际发送\n")
        return False

    print(f"\n✅ Webhook URL: {webhook_url[:50]}...")

    bot = FeishuBot(webhook_url=webhook_url)
    all_results = create_mock_results()

    print(f"\n准备发送 {len(all_results)} 个币种的合并消息...")
    print("币种: " + ", ".join([r['currency'] for r in all_results]))

    # 发送富文本卡片
    result = bot.send_multi_currency_report(
        all_results=all_results,
        index_url="https://yxw839841231.github.io/btc-momentum-service/",
        style="rich"
    )

    if result.get("status") == "success":
        print("\n✅ 飞书推送成功！")
        print("请检查飞书群查看合并消息效果")
        return True
    else:
        print(f"\n❌ 飞书推送失败")
        print(f"错误: {result.get('error')}")
        return False


def test_compact_format():
    """测试紧凑表格格式"""
    print("\n" + "="*60)
    print("紧凑表格格式预览")
    print("="*60)

    from src.feishu_multi_formatter import format_multi_currency_compact

    all_results = create_mock_results()
    card_data = format_multi_currency_compact(all_results, index_url="https://example.com/")

    print(f"\n标题: {card_data['title']}")
    print("\n内容:")
    print("-"*60)
    print(card_data['content'])
    print("-"*60)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("飞书多币种合并消息测试")
    print("="*60)

    # 测试1: 格式预览
    test_multi_currency_format()

    # 测试2: 紧凑格式
    test_compact_format()

    # 测试3: 实际发送（如果设置了环境变量）
    send_success = test_send_to_feishu()

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

    if send_success:
        print("\n✅ 消息已发送到飞书")
        print("请查看飞书群中的效果")
    else:
        print("\n💡 提示:")
        print("  - 设置 FEISHU_WEBHOOK_URL 环境变量可实际发送测试消息")
        print("  - 格式预览已显示在上面")

    print("\n可用的消息样式:")
    print("  1. rich - 富文本卡片（推荐，支持更多元素）")
    print("  2. compact - 紧凑表格（简洁，适合大量币种）")
    print("="*60)
