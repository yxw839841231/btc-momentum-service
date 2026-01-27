#!/usr/bin/env python3
"""
测试多币种消息格式
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.telegram_bot import TelegramBot
from src.feishu_bot import FeishuBot

def create_mock_analysis_data(currency):
    """创建模拟分析数据"""
    return {
        'currency': currency,
        'currency_price': {
            'price': '100.00' if currency != 'BTC' else '98000.00',
            'change_24h': 2.5,
            'change_24h_pct': 2.5,
            'exchange': 'OKX'
        },
        'timestamp': '2026-01-27T21:00:00',
        'status': 'success'
    }

def test_telegram_message_format():
    """测试 Telegram 消息格式"""
    print("="*60)
    print("Telegram 消息格式测试")
    print("="*60)

    bot = TelegramBot(bot_token="test_token")
    currencies = ["BTC", "SUI", "SOL"]

    for currency in currencies:
        print(f"\n{'-'*60}")
        print(f"{currency} 消息:")
        print(f"{'-'*60}")

        analysis_data = create_mock_analysis_data(currency)
        message = bot.format_analysis_summary(
            analysis_data,
            report_url="https://example.com/report",
            index_url="https://example.com/"
        )

        # 只显示前几行
        lines = message.split('\n')
        for i, line in enumerate(lines[:8], 1):
            print(f"{i}: {line}")

        print("...")

def test_feishu_message_format():
    """测试飞书消息格式"""
    print("\n" + "="*60)
    print("飞书消息格式测试")
    print("="*60)

    bot = FeishuBot(webhook_url="https://example.com/webhook")
    currencies = ["BTC", "SUI", "SOL"]

    for currency in currencies:
        print(f"\n{'-'*60}")
        print(f"{currency} 消息:")
        print(f"{'-'*60}")

        analysis_data = create_mock_analysis_data(currency)
        card_data = bot.format_analysis_card(
            analysis_data,
            report_url="https://example.com/report",
            index_url="https://example.com/"
        )

        print(f"标题: {card_data['title']}")
        print(f"内容预览:")
        lines = card_data['content'].split('\n')
        for i, line in enumerate(lines[:5], 1):
            print(f"  {i}: {line}")
        print("  ...")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("多币种消息格式测试")
    print("="*60)

    test_telegram_message_format()
    test_feishu_message_format()

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    print("\n✅ 检查点:")
    print("  1. 标题中显示币种名称 (如 'BTC 动能分析')")
    print("  2. 价格前显示币种图标 (如 '₿ BTC 价格')")
    print("  3. 每个币种的消息格式一致")
    print("="*60)
