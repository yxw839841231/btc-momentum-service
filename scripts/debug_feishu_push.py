#!/usr/bin/env python3
"""
飞书推送调试脚本
用于测试多币种推送和诊断问题
"""

import os
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

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

def test_feishu_multi_currency():
    """测试飞书多币种推送"""
    print("="*60)
    print("飞书多币种推送测试")
    print("="*60)

    # 获取飞书 webhook
    webhook_url = os.environ.get("FEISHU_WEBHOOK_URL")

    if not webhook_url:
        print("\n❌ 错误: 未设置 FEISHU_WEBHOOK_URL 环境变量")
        print("\n请设置环境变量:")
        print("  export FEISHU_WEBHOOK_URL='your_webhook_url'")
        return False

    print(f"\n✅ Webhook URL: {webhook_url[:50]}...")

    # 创建飞书 Bot
    bot = FeishuBot(webhook_url=webhook_url)

    # 测试币种
    currencies = ["BTC", "SUI", "SOL"]

    print(f"\n准备推送 {len(currencies)} 个币种到飞书...")
    print(f"币种: {', '.join(currencies)}")
    print("\n" + "="*60)

    success_count = 0
    failed_count = 0

    for i, currency in enumerate(currencies, 1):
        print(f"\n[{i}/{len(currencies)}] 推送 {currency}...")

        # 添加延迟避免限流
        if i > 1:
            print(f"  等待 2 秒...")
            time.sleep(2)

        # 创建模拟数据
        analysis_data = create_mock_analysis_data(currency)
        report_url = f"https://example.com/report_{currency.lower()}"
        index_url = "https://example.com/"

        # 发送消息
        result = bot.send_analysis_report(
            analysis_data=analysis_data,
            report_url=report_url,
            index_url=index_url
        )

        # 检查结果
        if result.get("status") == "success":
            print(f"  ✅ {currency} 推送成功")
            success_count += 1
        else:
            print(f"  ❌ {currency} 推送失败")
            print(f"  错误: {result.get('error')}")
            if 'details' in result:
                print(f"  详情: {result['details']}")
            failed_count += 1

    # 总结
    print("\n" + "="*60)
    print("测试结果")
    print("="*60)
    print(f"成功: {success_count}/{len(currencies)}")
    print(f"失败: {failed_count}/{len(currencies)}")

    if failed_count > 0:
        print("\n⚠️  部分币种推送失败！")
        print("\n可能的原因:")
        print("  1. 飞书 Webhook 频率限制（短时间内发送太多消息）")
        print("  2. 消息内容格式问题")
        print("  3. 网络连接问题")
        print("\n建议:")
        print("  - 增加发送间隔（当前为 2 秒）")
        print("  - 检查飞书群设置，确认 Webhook 正常工作")
        print("  - 查看飞书群是否收到了部分消息")
    else:
        print("\n✅ 所有币种推送成功！")

    print("="*60)

    return failed_count == 0

if __name__ == "__main__":
    print("\n" + "="*60)
    print("飞书推送调试工具")
    print("="*60)
    print("\n此脚本将测试多币种推送功能")
    print("模拟 BTC、SUI、SOL 三个币种的分析报告推送\n")

    success = test_feishu_multi_currency()

    if success:
        print("\n✅ 测试通过")
        sys.exit(0)
    else:
        print("\n❌ 测试失败，请检查上述错误信息")
        sys.exit(1)
