#!/usr/bin/env python3
"""
Telegram Bot 服务器
持续运行以接收和处理用户命令
使用长轮询模式（适合本地或服务器运行）
"""

import os
import sys
import logging
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 检查是否安装了 python-telegram-bot
try:
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot 未安装，将使用备用方案")

# 导入本地模块
from src.telegram_bot import TelegramBot
from src.subscription_manager import SubscriptionManager

# Telegram Bot 配ration
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DB_PATH = os.environ.get("SUBSCRIPTION_DB_PATH", "data/subscriptions.db")


def start_command(update: Update, context: CallbackContext) -> None:
    """处理 /start 命令"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    welcome_message = """👋 欢迎使用 BTC 动能分析服务！

我为您提供以下功能：

📊 **动能分析报告**
   • 多时间级别分析
   • 实时价格推送
   • 关键信号提示

⚙️ **订阅管理**
   • 自定义时间级别
   • 选择关注的币种
   • 设置推送频率

📝 **常用命令**
   /help - 查看所有命令
   /mysubscriptions - 查看我的订阅
   /subscribe <时间级别> - 订阅时间级别
   /subscribe_currency <币种> - 订阅币种

💡 提示：发送 /help 查看完整命令列表
"""

    update.message.reply_text(welcome_message)
    logger.info(f"用户 {user_id} 启动了 Bot")


def help_command(update: Update, context: CallbackContext) -> None:
    """处理 /help 命令"""
    from src.command_parser import CommandParser
    parser = CommandParser()

    help_message = parser.format_help_message()
    update.message.reply_text(help_message, parse_mode='Markdown')
    logger.info(f"用户 {update.effective_user.id} 查看了帮助")


def handle_text_message(update: Update, context: CallbackContext) -> None:
    """处理文本消息（命令）"""
    user_id = update.effective_user.id
    chat_id = str(update.effective_chat.id)
    text = update.message.text

    logger.info(f"收到来自用户 {user_id} 的消息: {text}")

    # 使用 TelegramBot 类处理命令
    bot = TelegramBot(bot_token=BOT_TOKEN, db_path=DB_PATH)
    result = bot.handle_command(chat_id, text, user_id)

    # 如果命令处理失败，发送帮助消息
    if result.get('status') == 'error':
        update.message.reply_text(
            f"❌ {result.get('error', '未知错误')}\n\n"
            f"发送 /help 查看可用命令"
        )


def error_handler(update: Update, context: CallbackContext) -> None:
    """处理错误"""
    logger.error(f"Update {update} 导致错误 {context.error}")

    if update and update.effective_message:
        update.effective_message.reply_text(
            "❌ 处理命令时出错，请稍后重试"
        )


def main() -> None:
    """启动 Bot 服务器"""
    if not BOT_TOKEN:
        logger.error("❌ 错误: 未设置 TELEGRAM_BOT_TOKEN 环境变量")
        logger.error("")
        logger.error("请设置环境变量:")
        logger.error("  export TELEGRAM_BOT_TOKEN='your_bot_token'")
        sys.exit(1)

    if TELEGRAM_AVAILABLE:
        # 使用 python-telegram-bot（推荐）
        logger.info("使用 python-telegram-bot 库")
        run_with_updater()
    else:
        # 使用备用方案（简单的轮询）
        logger.warning("python-telegram-bot 未安装，使用备用方案")
        run_with_simple_polling()


def run_with_updater() -> None:
    """使用 python-telegram-bot 的 Updater 运行"""
    from telegram.ext import Updater

    # 创建 Updater
    updater = Updater(token=BOT_TOKEN)

    # 获取分发器以注册处理器
    dispatcher = updater.dispatcher

    # 注册命令处理器
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler(["help", "h"], help_command))

    # 注册文本消息处理器（处理所有其他命令）
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        handle_text_message
    ))

    # 注册错误处理器
    dispatcher.add_error_handler(error_handler)

    # 启动 Bot
    logger.info("🚀 Bot 服务器启动中...")
    logger.info("使用长轮询模式接收消息")
    logger.info("按 Ctrl+C 停止")

    updater.start_polling()
    updater.idle()


def run_with_simple_polling() -> None:
    """
    使用简单的 HTTP 轮询（备用方案）
    注意：这个方案功能有限，只支持基本命令
    """
    import time
    import requests

    bot = TelegramBot(bot_token=BOT_TOKEN, db_path=DB_PATH)
    offset = 0
    poll_interval = 2  # 秒

    logger.info("🚀 Bot 服务器启动中...")
    logger.info("使用简单轮询模式")
    logger.info("提示: 安装 python-telegram-bot 以获得更好体验")
    logger.info("   pip install python-telegram-bot")
    logger.info("按 Ctrl+C 停止")
    logger.info("")

    while True:
        try:
            # 获取更新
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {
                "offset": offset,
                "timeout": 10,
                "allowed_updates": ["message"]
            }

            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if data.get("ok"):
                updates = data.get("result", [])

                for update in updates:
                    # 更新 offset
                    offset = update["update_id"] + 1

                    # 处理消息
                    if "message" in update:
                        message = update["message"]
                        chat_id = str(message["chat"]["id"])
                        text = message.get("text", "")

                        if text:
                            user_id = message["from"]["id"]

                            # 处理命令
                            logger.info(f"收到消息: {text} (chat_id={chat_id})")
                            bot.handle_command(chat_id, text, user_id)

            # 等待下一次轮询
            time.sleep(poll_interval)

        except KeyboardInterrupt:
            logger.info("\n⏹️  Bot 服务器已停止")
            break
        except Exception as e:
            logger.error(f"❌ 错误: {e}")
            time.sleep(5)  # 出错后等待5秒再重试


if __name__ == "__main__":
    main()
