#!/usr/bin/env python3
"""
订阅管理测试脚本
测试订阅管理的各项功能
"""

import sys
import os
import json
import logging
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.subscription_manager import SubscriptionManager, AlertFilter
from src.command_parser import CommandParser
from src.currency_config import CurrencyConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_subscription_manager():
    """测试订阅管理器"""
    print("=" * 60)
    print("测试 1: 订阅管理器")
    print("=" * 60)

    # 创建测试数据库
    test_db = "data/test_subscriptions.db"
    manager = SubscriptionManager(db_path=test_db)

    # 测试用户
    test_user_id = 999999
    test_chat_id = "999999"
    platform = "telegram"

    # 1. 创建订阅
    print("\n1.1 创建订阅")
    subscription = manager.get_or_create_subscription(test_user_id, test_chat_id, platform)
    print(f"✅ 创建订阅: {json.dumps(subscription, indent=2, ensure_ascii=False)}")

    # 2. 订阅时间级别
    print("\n1.2 订阅时间级别")
    result = manager.subscribe_timeframes(test_user_id, test_chat_id, platform, ["1d", "4h", "1h"])
    print(f"✅ 订阅结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 3. 订阅币种
    print("\n1.3 订阅币种")
    result = manager.subscribe_currencies(test_user_id, test_chat_id, platform, ["BTC", "ETH", "SOL"])
    print(f"✅ 订阅结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 4. 订阅信号类型
    print("\n1.4 订阅信号类型")
    result = manager.subscribe_signals(test_user_id, test_chat_id, platform, ["divergence", "buy_signal"])
    print(f"✅ 订阅结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 5. 设置推送频率
    print("\n1.5 设置推送频率")
    result = manager.set_frequency(test_user_id, test_chat_id, platform, "alerts")
    print(f"✅ 设置结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 6. 查询订阅
    print("\n1.6 查询订阅")
    subscription = manager.get_or_create_subscription(test_user_id, test_chat_id, platform)
    print(f"✅ 当前订阅: {json.dumps(subscription, indent=2, ensure_ascii=False)}")

    # 7. 取消订阅时间级别
    print("\n1.7 取消订阅时间级别")
    result = manager.unsubscribe_timeframes(test_user_id, test_chat_id, platform, ["1h"])
    print(f"✅ 取消结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 8. 获取所有订阅者
    print("\n1.8 获取所有订阅者")
    subscribers = manager.get_all_subscribers(platform)
    print(f"✅ 订阅者数量: {len(subscribers)}")
    if subscribers:
        print(f"第一个订阅者: {json.dumps(subscribers[0], indent=2, ensure_ascii=False)}")

    # 9. 获取币种订阅者
    print("\n1.9 获取 BTC 订阅者")
    btc_subscribers = manager.get_subscribers_for_currency("BTC", platform)
    print(f"✅ BTC 订阅者数量: {len(btc_subscribers)}")

    # 10. 获取时间级别订阅者
    print("\n1.10 获取 1d 订阅者")
    timeframe_subscribers = manager.get_subscribers_for_timeframe("1d", platform)
    print(f"✅ 1d 订阅者数量: {len(timeframe_subscribers)}")


def test_command_parser():
    """测试命令解析器"""
    print("\n" + "=" * 60)
    print("测试 2: 命令解析器")
    print("=" * 60)

    parser = CommandParser()

    test_commands = [
        "/subscribe 1d 4h",
        "/unsubscribe 30m",
        "/subscribe_signal divergence buy_signal",
        "/subscribe_currency btc eth sol",
        "/frequency alerts",
        "/mysubscriptions",
        "/help"
    ]

    for cmd in test_commands:
        print(f"\n解析命令: {cmd}")
        result = parser.parse_command(cmd)
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")


def test_alert_filter():
    """测试告警过滤器"""
    print("\n" + "=" * 60)
    print("测试 3: 告警过滤器")
    print("=" * 60)

    test_db = "data/test_subscriptions.db"
    manager = SubscriptionManager(db_path=test_db)
    alert_filter = AlertFilter(manager)

    test_user_id = 999999
    test_chat_id = "999999"
    platform = "telegram"

    # 测试报告推送检查
    print("\n3.1 测试报告推送检查")
    should_send = alert_filter.should_send_report(
        user_id=test_user_id,
        chat_id=test_chat_id,
        platform=platform,
        currency="BTC",
        timeframe="1d"
    )
    print(f"✅ 应该发送 BTC 1d 报告: {should_send}")

    should_send = alert_filter.should_send_report(
        user_id=test_user_id,
        chat_id=test_chat_id,
        platform=platform,
        currency="ETH",
        timeframe="1d"
    )
    print(f"✅ 应该发送 ETH 1d 报告: {should_send}")

    should_send = alert_filter.should_send_report(
        user_id=test_user_id,
        chat_id=test_chat_id,
        platform=platform,
        currency="BTC",
        timeframe="1h"
    )
    print(f"✅ 应该发送 BTC 1h 报告: {should_send}")

    # 测试告警推送检查
    print("\n3.2 测试告警推送检查")
    should_send = alert_filter.should_send_alert(
        user_id=test_user_id,
        chat_id=test_chat_id,
        platform=platform,
        signal_type="divergence",
        timeframe="4h",
        currency="BTC"
    )
    print(f"✅ 应该发送 BTC 4h 背离告警: {should_send}")

    should_send = alert_filter.should_send_alert(
        user_id=test_user_id,
        chat_id=test_chat_id,
        platform=platform,
        signal_type="sell_signal",
        timeframe="4h",
        currency="BTC"
    )
    print(f"✅ 应该发送 BTC 4h 卖点告警: {should_send}")

    # 测试信号哈希生成
    print("\n3.3 测试信号哈希生成")
    hash1 = alert_filter.generate_signal_hash("divergence", "4h", "BTC")
    hash2 = alert_filter.generate_signal_hash("divergence", "4h", "BTC")
    hash3 = alert_filter.generate_signal_hash("divergence", "1h", "BTC")
    print(f"✅ 信号哈希 1: {hash1}")
    print(f"✅ 信号哈希 2: {hash2} (相同: {hash1 == hash2})")
    print(f"✅ 信号哈希 3: {hash3} (与1相同: {hash1 == hash3})")

    # 测试告警记录
    print("\n3.4 测试告警记录")
    success = manager.record_alert_sent(
        signal_hash=hash1,
        signal_type="divergence",
        timeframe="4h",
        currency="BTC",
        content="测试背离信号"
    )
    print(f"✅ 记录告警: {success}")

    was_sent = manager.is_alert_sent_recently(hash1, hours=1)
    print(f"✅ 最近已发送: {was_sent}")


def test_currency_config():
    """测试币种配置"""
    print("\n" + "=" * 60)
    print("测试 4: 币种配置")
    print("=" * 60)

    config = CurrencyConfig()

    # 测试支持的币种
    print("\n4.1 测试支持的币种")
    for symbol in ["BTC", "ETH", "SOL", "XYZ"]:
        supported = config.is_supported(symbol)
        print(f"  {symbol}: {'✅ 支持' if supported else '❌ 不支持'}")

    # 测试获取交易对符号
    print("\n4.2 测试获取交易对符号")
    for symbol in ["BTC", "ETH", "SOL"]:
        exchange_symbol = config.get_exchange_symbol(symbol)
        print(f"  {symbol} -> {exchange_symbol}")

    # 测试获取币种信息
    print("\n4.3 测试获取币种信息")
    currencies = config.get_all_currencies_info()
    print(f"✅ 支持的币种数量: {len(currencies)}")
    for currency in currencies[:3]:
        print(f"  • {currency['symbol']}: {currency['name']} ({currency['color']})")

    # 测试格式化币种列表
    print("\n4.4 测试格式化币种列表")
    list_text = config.format_currencies_list()
    print(list_text)


def test_telegram_bot_commands():
    """测试 Telegram Bot 命令处理"""
    print("\n" + "=" * 60)
    print("测试 5: Telegram Bot 命令处理")
    print("=" * 60)

    # 注意：此测试需要实际的 Telegram Bot Token
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("⚠️ 跳过测试（未设置 TELEGRAM_BOT_TOKEN）")
        return

    from src.telegram_bot import TelegramBot

    test_db = "data/test_subscriptions.db"
    bot = TelegramBot(bot_token=bot_token, db_path=test_db)

    test_user_id = 999999
    test_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "999999")

    # 测试命令处理
    print("\n5.1 测试命令处理")

    commands = [
        ("/subscribe 1d 4h", "订阅时间级别"),
        ("/subscribe_currency btc eth", "订阅币种"),
        ("/mysubscriptions", "查看订阅"),
        ("/help", "帮助")
    ]

    for cmd, desc in commands:
        print(f"\n测试: {desc} ({cmd})")
        result = bot.handle_command(test_chat_id, cmd, test_user_id)
        print(f"结果: {result.get('status', 'unknown')}")


def cleanup():
    """清理测试数据"""
    print("\n" + "=" * 60)
    print("清理测试数据")
    print("=" * 60)

    test_db = "data/test_subscriptions.db"
    if os.path.exists(test_db):
        os.remove(test_db)
        print(f"✅ 删除测试数据库: {test_db}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("订阅管理功能测试")
    print("=" * 60)

    try:
        # 运行测试
        test_subscription_manager()
        test_command_parser()
        test_alert_filter()
        test_currency_config()
        test_telegram_bot_commands()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成")
        print("=" * 60)

        # 询问是否清理
        print("\n是否删除测试数据库? (y/n): ", end="")
        # 在脚本中默认不清理，让用户决定
        print("n (保留测试数据供检查)")
        print("提示: 手动删除请运行: rm data/test_subscriptions.db")

        return 0

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)
        cleanup()
        return 1


if __name__ == "__main__":
    sys.exit(main())
