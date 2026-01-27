#!/usr/bin/env python3
"""
测试 Telegram Bot 连接
"""

import os
import sys

# 添加 src 目录到路径
sys.path.insert(0, str(os.path.dirname(os.path.dirname(__file__))))

from src.telegram_bot import TelegramBot

def main():
    print("=" * 60)
    print("Telegram Bot 连接测试")
    print("=" * 60)

    # 从环境变量读取配置
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token:
        print("❌ 错误: 未设置 TELEGRAM_BOT_TOKEN 环境变量")
        print("\n请运行:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token'")
        return 1

    if not chat_id:
        print("❌ 错误: 未设置 TELEGRAM_CHAT_ID 环境变量")
        print("\n请运行:")
        print("export TELEGRAM_CHAT_ID='your_chat_id'")
        return 1

    print(f"\n✅ 配置加载成功")
    print(f"Bot Token: {bot_token[:20]}...")
    print(f"Chat ID: {chat_id}")

    # 初始化 Bot
    print("\n📡 正在连接 Telegram...")
    bot = TelegramBot(bot_token=bot_token, default_chat_id=chat_id)

    # 测试连接
    if bot.test_connection():
        print("✅ Bot 连接成功！")

        # 发送测试消息
        print("\n📤 发送测试消息...")
        test_message = """📊 *BTC 动能分析服务*

✅ Bot 连接测试成功！

这是一个测试消息，用于验证 Telegram Bot 配置。

如果你看到这条消息，说明 Bot 已正确配置。

下一步:
1. 运行完整分析: `python scripts/run_analysis.py`
2. 部署到 GitHub Actions
"""

        result = bot.send_message(text=test_message)

        if result.get("status") == "success":
            print("✅ 测试消息发送成功！")
            print("   请检查你的 Telegram 接收消息。")
            return 0
        else:
            print(f"❌ 消息发送失败: {result}")
            return 1
    else:
        print("❌ Bot 连接失败")
        print("   请检查:")
        print("   1. Bot Token 是否正确")
        print("   2. 网络连接是否正常")
        return 1

if __name__ == "__main__":
    sys.exit(main())
