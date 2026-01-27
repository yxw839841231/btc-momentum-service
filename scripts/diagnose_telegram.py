#!/usr/bin/env python3
"""
Telegram Bot 诊断脚本
检查 Bot 配置和 API 连接
"""

import os
import sys
import requests
import json

# 从环境变量读取配置
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

print("=" * 70)
print("Telegram Bot 诊断工具")
print("=" * 70)

if not bot_token or not chat_id:
    print("❌ 错误: 请设置环境变量")
    print("   export TELEGRAM_BOT_TOKEN='your_token'")
    print("   export TELEGRAM_CHAT_ID='your_chat_id'")
    sys.exit(1)

print(f"\n📋 配置信息:")
print(f"   Bot Token: {bot_token[:20]}...{bot_token[-10:]}")
print(f"   Chat ID: {chat_id}")
print(f"   Chat ID 类型: {type(chat_id)}")

# 尝试转换为整数
try:
    chat_id_int = int(chat_id)
    print(f"   Chat ID (整数): {chat_id_int}")
except:
    print(f"   ⚠️  Chat ID 无法转换为整数")

# API 基础 URL
base_url = f"https://api.telegram.org/bot{bot_token}"

# 测试 1: getMe - 获取 Bot 信息
print("\n" + "-" * 70)
print("测试 1: 获取 Bot 信息 (getMe)")
print("-" * 70)

try:
    url = f"{base_url}/getMe"
    response = requests.get(url, timeout=15)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            bot_info = data.get("result", {})
            print(f"✅ 成功!")
            print(f"   Bot ID: {bot_info.get('id')}")
            print(f"   Bot 名称: @{bot_info.get('username')}")
            print(f"   Bot 显示名: {bot_info.get('first_name')}")
            print(f"   can_join_groups: {bot_info.get('can_join_groups')}")
            print(f"   can_read_all_group_messages: {bot_info.get('can_read_all_group_messages')}")
            print(f"   supports_inline_queries: {bot_info.get('supports_inline_queries')}")
        else:
            print(f"❌ 失败: {data}")
    else:
        print(f"❌ HTTP 错误: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 测试 2: 尝试不同的 Chat ID 格式
print("\n" + "-" * 70)
print("测试 2: 测试不同的 Chat ID 格式")
print("-" * 70)

test_cases = [
    ("原始 Chat ID (字符串)", chat_id),
    ("Chat ID (整数)", str(int(chat_id))),
    ("Chat ID (@前缀)", f"@{chat_id}"),
]

for name, test_chat_id in test_cases:
    print(f"\n📤 测试: {name}")
    print(f"   Chat ID 值: {test_chat_id}")

    try:
        url = f"{base_url}/sendMessage"
        data = {
            "chat_id": test_chat_id,
            "text": f"测试消息 - {name}"
        }
        response = requests.post(url, json=data, timeout=15)

        print(f"   状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"   ✅ 成功! 消息 ID: {result.get('result', {}).get('message_id')}")
            else:
                print(f"   ❌ API 错误: {result.get('description')}")
        else:
            try:
                error_data = response.json()
                print(f"   ❌ 错误: {error_data}")
            except:
                print(f"   ❌ HTTP 错误: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")

# 测试 3: 获取 Bot 的更新（看看是否有未读消息）
print("\n" + "-" * 70)
print("测试 3: 获取 Bot 更新 (getUpdates)")
print("-" * 70)

try:
    url = f"{base_url}/getUpdates"
    response = requests.get(url, timeout=15)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            updates = data.get("result", [])
            print(f"✅ 成功! 找到 {len(updates)} 条更新")

            if updates:
                print(f"\n最近的消息:")
                for update in updates[-3:]:  # 显示最近 3 条
                    message = update.get("message", {})
                    chat = message.get("chat", {})
                    print(f"   - Chat ID: {chat.get('id')}")
                    print(f"     类型: {chat.get('type')}")
                    print(f"     名称: {chat.get('first_name') or chat.get('title')}")
                    if message.get("text"):
                        print(f"     消息: {message.get('text')}")
            else:
                print(f"   ⚠️  没有找到更新")
                print(f"   💡 提示: 请给 Bot 发送一条 /start 消息")
        else:
            print(f"❌ 失败: {data}")
    else:
        print(f"❌ HTTP 错误: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)

print("""
💡 常见问题和解决方案:

1. Bot 没有收到 /start 命令
   → 在 Telegram 中搜索你的 Bot
   → 发送 /start 命令
   → 再次运行此脚本查看 Chat ID

2. Chat ID 格式错误
   → 私聊: 数字 ID (如: 123456789)
   → 群组: -数字 ID (如: -123456789)
   → 频道: @channelname

3. Bot 权限不足
   → 如果是群组/频道，确保 Bot 是管理员

4. Bot Token 错误
   → 重新从 @BotFather 获取 Token
""")
