#!/usr/bin/env python3
"""
获取正确的 Chat ID
使用 Telegram Bot API 的 getUpdates 方法
"""

import os
import sys
import requests
import json

bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

if not bot_token:
    print("❌ 请设置环境变量: export TELEGRAM_BOT_TOKEN='your_token'")
    sys.exit(1)

print("=" * 70)
print("获取 Telegram Chat ID")
print("=" * 70)

url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

print("\n步骤 1: 给 Bot 发送消息")
print("-" * 70)
print("请在 Telegram 中完成以下操作：")
print("1. 搜索你的 Bot（通过用户名或 Bot Token 中的数字部分）")
print("2. 点击 Bot 名称进入对话")
print("3. 发送 /start 命令")
print("4. 发送任意一条消息（如：'hello'）")
print("\n完成后按回车继续...")
input()

print("\n步骤 2: 获取更新")
print("-" * 70)

try:
    response = requests.get(url, timeout=15)

    if response.status_code == 200:
        data = response.json()

        if data.get("ok"):
            updates = data.get("result", [])

            if not updates:
                print("❌ 没有找到任何更新")
                print("\n可能的原因：")
                print("1. 你还没有给 Bot 发送消息")
                print("2. Bot Token 不正确")
                print("3. 网络问题")
                print("\n请确认：")
                print("- 你已经给 Bot 发送了 /start 命令")
                print(f"- Bot Token: {bot_token[:20]}...")
            else:
                print(f"✅ 找到 {len(updates)} 条更新\n")

                # 收集所有唯一的 Chat ID
                chat_ids = {}
                for update in updates:
                    message = update.get("message", {})
                    if not message:
                        continue

                    chat = message.get("chat", {})
                    chat_id = chat.get("id")
                    chat_type = chat.get("type")
                    chat_title = chat.get("title") or chat.get("first_name") or chat.get("username")

                    if chat_id not in chat_ids:
                        chat_ids[chat_id] = {
                            "type": chat_type,
                            "title": chat_title,
                            "message_count": 1
                        }
                    else:
                        chat_ids[chat_id]["message_count"] += 1

                print("发现的 Chat ID：")
                print("-" * 70)

                for i, (chat_id, info) in enumerate(chat_ids.items(), 1):
                    print(f"\n{i}. Chat ID: {chat_id}")
                    print(f"   类型: {info['type']}")
                    print(f"   名称: {info['title']}")
                    print(f"   消息数: {info['message_count']}")

                # 推荐使用哪个
                if len(chat_ids) == 1:
                    correct_chat_id = list(chat_ids.keys())[0]
                    print(f"\n" + "=" * 70)
                    print(f"✅ 你的 Chat ID 是: {correct_chat_id}")
                    print("=" * 70)
                    print(f"\n请设置环境变量:")
                    print(f"export TELEGRAM_CHAT_ID='{correct_chat_id}'")
                else:
                    print(f"\n" + "=" * 70)
                    print(f"⚠️  找到多个 Chat ID，请选择一个使用")
                    print("=" * 70)
                    print("\n推荐使用 private（私聊）类型的 Chat ID")

        else:
            print(f"❌ API 错误: {data}")
    else:
        print(f"❌ HTTP 错误: {response.status_code}")
        print(f"响应: {response.text}")

except Exception as e:
    print(f"❌ 异常: {e}")

print("\n" + "=" * 70)
