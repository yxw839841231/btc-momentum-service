#!/bin/bash
# Telegram Bot 服务器启动脚本

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   BTC 动能分析 - Telegram Bot 服务器启动                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查环境变量
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ 错误: 未设置 TELEGRAM_BOT_TOKEN 环境变量"
    echo ""
    echo "请先设置环境变量:"
    echo "  export TELEGRAM_BOT_TOKEN='your_bot_token'"
    echo ""
    echo "或者创建 .env 文件:"
    echo "  echo 'TELEGRAM_BOT_TOKEN=your_bot_token' > .env"
    exit 1
fi

# 检查数据库
if [ ! -f "data/subscriptions.db" ]; then
    echo "📦 初始化订阅数据库..."
    python3 scripts/init_subscription_db.py
fi

# 检查 python-telegram-bot
echo "🔍 检查依赖..."
if python3 -c "import telegram" 2>/dev/null; then
    echo "✅ python-telegram-bot 已安装（推荐）"
    MODE="updater"
else
    echo "⚠️  python-telegram-bot 未安装"
    echo "   安装以获得更好体验: pip install python-telegram-bot"
    echo "   使用简单轮询模式..."
    MODE="simple"
fi

echo ""
echo "🚀 启动 Bot 服务器..."
echo "   模式: $MODE"
echo "   按 Ctrl+C 停止"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 启动 Bot 服务器
python3 scripts/telegram_bot_server.py
