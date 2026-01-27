#!/usr/bin/env python3
"""
简单的 Telegram 测试脚本
"""

import os
import sys
import requests

# 从环境变量读取配置
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if not bot_token or not chat_id:
    print("❌ 错误: 请设置环境变量")
    sys.exit(1)

print(f"Bot Token: {bot_token[:20]}...")
print(f"Chat ID: {chat_id}")
print(f"Chat ID 类型: {type(chat_id)}")

# API URL
url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

# 测试 1: 最简单的消息
print("\n📤 测试 1: 发送最简单的消息")
data1 = {
    "chat_id": int(chat_id),  # 确保是整数
    "text": "Test message"
}

try:
    response = requests.post(url, json=data1, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    if response.status_code == 200:
        print("✅ 测试 1 成功！")
    else:
        print("❌ 测试 1 失败")
except Exception as e:
    print(f"❌ 异常: {e}")

# 测试 2: 带 emoji 的消息
print("\n📤 测试 2: 带 emoji 的消息")
data2 = {
    "chat_id": int(chat_id),
    "text": "📊 测试消息\n\nBTC 分析服务测试"
}

try:
    response = requests.post(url, json=data2, timeout=30)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ 测试 2 成功！")
    else:
        print(f"❌ 测试 2 失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 测试 3: 完整消息
print("\n📤 测试 3: 完整消息")
data3 = {
    "chat_id": int(chat_id),
    "text": """📊 BTC 动能分析

时间: 2026-01-27 12:00

【大周期】2日线 ↑ 1日线 ↑
【中周期】12h ⚠️  6h 调整 4h ↓
【小周期】2h ↓ 1h ↓ 30m ⟲

🔴 关键信号:
• 12h 出现顶背离
• 30m 柱状图收敛，可能反转

📈 完整报告:
https://yxw839841231.github.io/btc-momentum-service/reports/test.html

💡 操作建议: 观望"""
}

try:
    response = requests.post(url, json=data3, timeout=30)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ 测试 3 成功！")
    else:
        print(f"❌ 测试 3 失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

print("\n" + "=" * 60)
print("测试完成")
