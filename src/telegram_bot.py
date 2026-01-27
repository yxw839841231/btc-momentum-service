"""
Telegram Bot 模块
处理 Telegram 消息和推送
"""

import logging
from typing import Optional
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram Bot 客户端"""

    def __init__(self, bot_token: str, default_chat_id: Optional[str] = None):
        """
        初始化 Bot

        Args:
            bot_token: Telegram Bot Token
            default_chat_id: 默认 Chat ID
        """
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        logger.info(f"Telegram Bot 初始化成功")

    def send_message(
        self,
        chat_id: Optional[str] = None,
        text: str = "",
        parse_mode: str = "Markdown"
    ) -> dict:
        """
        发送消息

        Args:
            chat_id: Chat ID (如果为 None，使用 default_chat_id)
            text: 消息文本
            parse_mode: 解析模式 (Markdown, HTML, None)

        Returns:
            API 响应
        """
        if chat_id is None:
            chat_id = self.default_chat_id

        if chat_id is None:
            logger.error("Chat ID 未设置")
            return {"status": "error", "error": "Chat ID 未设置"}

        url = f"{self.api_url}/sendMessage"

        data = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": False
        }

        if parse_mode:
            data["parse_mode"] = parse_mode

        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info(f"消息发送成功: chat_id={chat_id}")
                return {"status": "success", "data": result}
            else:
                logger.error(f"消息发送失败: {result}")
                return {"status": "error", "error": result}

        except requests.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            return {"status": "error", "error": str(e)}

    def format_analysis_summary(self, analysis_data: dict, report_url: str) -> str:
        """
        格式化分析摘要

        Args:
            analysis_data: 分析数据
            report_url: 报告链接

        Returns:
            格式化的消息文本
        """
        # TODO: 根据实际分析数据格式化

        message = f"""📊 *BTC 动能分析*

时间: {analysis_data.get('timestamp', 'N/A')}

【大周期】2日线 ↑ 1日线 ↑
【中周期】12h ⚠️  6h 调整 4h ↓
【小周期】2h ↓ 1h ↓ 30m ⟲

🔴 *关键信号*:
• 12h 出现顶背离
• 30m 柱状图收敛，可能反转

📈 [完整报告]({report_url})

💡 *操作建议*: 观望
"""

        return message

    def send_analysis_report(
        self,
        analysis_data: dict,
        report_url: str,
        chat_id: Optional[str] = None
    ) -> dict:
        """
        发送分析报告

        Args:
            analysis_data: 分析数据
            report_url: 报告链接
            chat_id: Chat ID

        Returns:
            发送结果
        """
        message = self.format_analysis_summary(analysis_data, report_url)
        return self.send_message(chat_id=chat_id, text=message)

    def send_alert(
        self,
        signal_type: str,
        timeframe: str,
        message: str,
        chat_id: Optional[str] = None
    ) -> dict:
        """
        发送实时告警

        Args:
            signal_type: 信号类型 (背离, 买点, 分立调控)
            timeframe: 时间级别
            message: 告警消息
            chat_id: Chat ID

        Returns:
            发送结果
        """
        alert_message = f"""🚨 *实时告警*

{signal_type} - {timeframe}
{message}
"""

        return self.send_message(chat_id=chat_id, text=alert_message)

    def test_connection(self) -> bool:
        """
        测试 Bot 连接

        Returns:
            连接是否成功
        """
        url = f"{self.api_url}/getMe"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                bot_info = result.get("result", {})
                logger.info(f"Bot 连接成功: @{bot_info.get('username')}")
                return True
            else:
                logger.error(f"Bot 连接失败: {result}")
                return False

        except requests.RequestException as e:
            logger.error(f"Bot 连接测试失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    import os

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if bot_token and chat_id:
        bot = TelegramBot(bot_token=bot_token, default_chat_id=chat_id)

        # 测试连接
        if bot.test_connection():
            print("✅ Bot 连接成功")

            # 发送测试消息
            result = bot.send_message(text="📊 测试消息\n\nBTC 分析服务已启动")
            print(f"消息发送结果: {result}")
        else:
            print("❌ Bot 连接失败")
    else:
        print("请设置环境变量:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("export TELEGRAM_CHAT_ID='your_chat_id'")
