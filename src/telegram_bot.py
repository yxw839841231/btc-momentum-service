"""
Telegram Bot 模块
处理 Telegram 消息和推送
"""

import logging
from typing import Optional, Dict
import requests
import sys
from pathlib import Path

# 添加父目录到路径以导入其他模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.command_parser import CommandParser
from src.subscription_manager import SubscriptionManager, AlertFilter
from src.currency_config import CurrencyConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram Bot 客户端"""

    def __init__(self, bot_token: str, default_chat_id: Optional[str] = None,
                 db_path: str = "data/subscriptions.db"):
        """
        初始化 Bot

        Args:
            bot_token: Telegram Bot Token
            default_chat_id: 默认 Chat ID
            db_path: 订阅数据库路径
        """
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

        # 初始化订阅管理
        self.subscription_manager = SubscriptionManager(db_path=db_path)
        self.alert_filter = AlertFilter(self.subscription_manager)
        self.command_parser = CommandParser()
        self.currency_config = CurrencyConfig()

        logger.info(f"Telegram Bot 初始化成功")

    def send_message(
        self,
        chat_id: Optional[str] = None,
        text: str = "",
        parse_mode: Optional[str] = None
    ) -> dict:
        """
        发送消息

        Args:
            chat_id: Chat ID (如果为 None，使用 default_chat_id)
            text: 消息文本
            parse_mode: 解析模式 (Markdown, HTML, None) - 默认 None

        Returns:
            API 响应
        """
        if chat_id is None:
            chat_id = self.default_chat_id

        if chat_id is None:
            logger.error("Chat ID 未设置")
            return {"status": "error", "error": "Chat ID 未设置"}

        # 确保 chat_id 是整数（Telegram API 要求）
        try:
            chat_id_int = int(chat_id)
        except (ValueError, TypeError):
            logger.error(f"Chat ID 格式错误: {chat_id}")
            return {"status": "error", "error": f"Chat ID 格式错误: {chat_id}"}

        url = f"{self.api_url}/sendMessage"

        data = {
            "chat_id": chat_id_int,
            "text": text,
            "disable_web_page_preview": False
        }

        # 只在明确指定 parse_mode 时才添加
        if parse_mode:
            data["parse_mode"] = parse_mode

        try:
            # 增加超时时间到 30 秒
            response = requests.post(url, json=data, timeout=30)

            # 记录详细的响应信息
            logger.info(f"Telegram API 响应状态码: {response.status_code}")

            # 先解析 JSON，获取详细信息
            try:
                result = response.json()
            except:
                result = {"raw": response.text}

            if response.status_code == 200 and result.get("ok"):
                logger.info(f"✅ 消息发送成功: chat_id={chat_id_int}")
                return {"status": "success", "data": result}
            else:
                # 详细的错误信息
                error_desc = result.get("description", "未知错误")
                error_params = result.get("parameters", {})
                logger.error(f"❌ Telegram API 错误:")
                logger.error(f"   状态码: {response.status_code}")
                logger.error(f"   错误描述: {error_desc}")
                logger.error(f"   错误参数: {error_params}")
                logger.error(f"   完整响应: {result}")
                return {"status": "error", "error": result}

        except requests.RequestException as e:
            logger.error(f"❌ 网络请求失败: {e}")
            return {"status": "error", "error": str(e)}

    def format_analysis_summary(self, analysis_data: dict, report_url: str, index_url: str = "") -> str:
        """
        格式化分析摘要

        Args:
            analysis_data: 分析数据
            report_url: 报告链接
            index_url: 主页链接

        Returns:
            格式化的消息文本
        """
        # TODO: 根据实际分析数据格式化

        # 简化时间格式，避免特殊字符
        timestamp = analysis_data.get('timestamp', 'N/A')
        if timestamp != 'N/A':
            # 简化 ISO 格式时间为可读格式
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass

        # 获取价格信息
        btc_price = analysis_data.get('btc_price', {})
        current_price = btc_price.get('price', 'N/A')
        price_change = btc_price.get('change_24h', 0)
        price_change_pct = btc_price.get('change_24h_pct', 0)
        price_indicator = "📈" if price_change >= 0 else "📉"

        message = f"""📊 BTC 动能分析

💰 价格: {price_indicator} ${current_price}
   24h: {price_change:+.2f} ({price_change_pct:+.2f}%)

时间: {timestamp}

【大周期】2日线 ↑ 1日线 ↑
【中周期】12h 警告 6h 调整 4h 下跌
【小周期】2h 下跌 1h 下跌 30m 反转

🔴 关键信号:
• 12h 出现顶背离
• 30m 柱状图收敛，可能反转

📈 最新报告:
{report_url}

🏠 所有报告:
{index_url}

💡 操作建议: 观望
"""

        return message

    def send_analysis_report(
        self,
        analysis_data: dict,
        report_url: str,
        index_url: str = "",
        chat_id: Optional[str] = None
    ) -> dict:
        """
        发送分析报告

        Args:
            analysis_data: 分析数据
            report_url: 报告链接
            index_url: 主页链接
            chat_id: Chat ID

        Returns:
            发送结果
        """
        message = self.format_analysis_summary(analysis_data, report_url, index_url)
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
            # 增加超时时间到 15 秒
            response = requests.get(url, timeout=15)
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

    # ==================== 命令处理方法 ====================

    def handle_command(self, chat_id: str, text: str, user_id: Optional[int] = None) -> dict:
        """
        处理用户命令

        Args:
            chat_id: 聊天 ID
            text: 命令文本
            user_id: 用户 ID（可选）

        Returns:
            处理结果
        """
        try:
            # 解析命令
            result = self.command_parser.parse_command(text)

            if result['status'] == 'error':
                return self.send_error_message(chat_id, result['error'])

            command = result.get('command')

            # 使用 chat_id 作为 user_id（如果未提供）
            if user_id is None:
                try:
                    user_id = int(chat_id)
                except (ValueError, TypeError):
                    user_id = hash(chat_id)

            # 命令路由
            if command == 'subscribe':
                return self._handle_subscribe(chat_id, user_id, result)
            elif command == 'unsubscribe':
                return self._handle_unsubscribe(chat_id, user_id, result)
            elif command == 'subscribe_signal':
                return self._handle_subscribe_signal(chat_id, user_id, result)
            elif command == 'unsubscribe_signal':
                return self._handle_unsubscribe_signal(chat_id, user_id, result)
            elif command == 'subscribe_currency':
                return self._handle_subscribe_currency(chat_id, user_id, result)
            elif command == 'unsubscribe_currency':
                return self._handle_unsubscribe_currency(chat_id, user_id, result)
            elif command == 'mysubscriptions':
                return self._handle_mysubscriptions(chat_id, user_id)
            elif command == 'my_currencies':
                return self._handle_my_currencies(chat_id, user_id)
            elif command == 'list_currencies':
                return self._handle_list_currencies(chat_id)
            elif command == 'frequency':
                return self._handle_frequency(chat_id, user_id, result)
            elif command == 'help':
                return self.send_help_message(chat_id)
            else:
                return self.send_error_message(chat_id, f"未知命令: {command}")

        except Exception as e:
            logger.error(f"处理命令失败: {e}", exc_info=True)
            return self.send_error_message(chat_id, f"处理命令时出错: {str(e)}")

    def _handle_subscribe(self, chat_id: str, user_id: int, result: Dict) -> dict:
        """处理订阅时间级别命令"""
        timeframes = result['timeframes']
        sub_result = self.subscription_manager.subscribe_timeframes(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram',
            timeframes=timeframes
        )

        if sub_result['status'] == 'success':
            message = f"✅ *订阅成功*\n\n"
            message += f"已添加时间级别: {', '.join(sub_result['added'])}\n"
            message += f"当前订阅: {', '.join(sub_result['timeframes']) or '无'}"
            return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        else:
            return self.send_error_message(chat_id, sub_result['error'])

    def _handle_unsubscribe(self, chat_id: str, user_id: int, result: Dict) -> dict:
        """处理取消订阅时间级别命令"""
        timeframes = result['timeframes']
        sub_result = self.subscription_manager.unsubscribe_timeframes(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram',
            timeframes=timeframes
        )

        if sub_result['status'] == 'success':
            message = f"✅ *取消订阅成功*\n\n"
            if sub_result['removed']:
                message += f"已移除时间级别: {', '.join(sub_result['removed'])}\n"
                message += f"当前订阅: {', '.join(sub_result['timeframes']) or '无'}"
            else:
                message += f"未订阅这些时间级别: {', '.join(timeframes)}"
            return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        else:
            return self.send_error_message(chat_id, sub_result['error'])

    def _handle_subscribe_signal(self, chat_id: str, user_id: int, result: Dict) -> dict:
        """处理订阅信号类型命令"""
        signals = result['signals']
        sub_result = self.subscription_manager.subscribe_signals(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram',
            signals=signals
        )

        if sub_result['status'] == 'success':
            message = f"✅ *信号订阅成功*\n\n"
            message += f"已添加信号类型: {', '.join(sub_result['added'])}\n"
            message += f"当前订阅: {', '.join(sub_result['signal_types']) or '无'}"
            return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        else:
            return self.send_error_message(chat_id, sub_result['error'])

    def _handle_unsubscribe_signal(self, chat_id: str, user_id: int, result: Dict) -> dict:
        """处理取消订阅信号类型命令"""
        signals = result['signals']
        sub_result = self.subscription_manager.unsubscribe_signals(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram',
            signals=signals
        )

        if sub_result['status'] == 'success':
            message = f"✅ *取消信号订阅成功*\n\n"
            if sub_result['removed']:
                message += f"已移除信号类型: {', '.join(sub_result['removed'])}\n"
                message += f"当前订阅: {', '.join(sub_result['signal_types']) or '无'}"
            else:
                message += f"未订阅这些信号类型: {', '.join(signals)}"
            return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        else:
            return self.send_error_message(chat_id, sub_result['error'])

    def _handle_subscribe_currency(self, chat_id: str, user_id: int, result: Dict) -> dict:
        """处理订阅币种命令"""
        currencies = result['currencies']
        sub_result = self.subscription_manager.subscribe_currencies(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram',
            currencies=currencies
        )

        if sub_result['status'] == 'success':
            message = f"✅ *币种订阅成功*\n\n"
            message += f"已添加币种: {', '.join(sub_result['added'])}\n"
            message += f"当前订阅: {', '.join(sub_result['currencies'])}"
            return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        else:
            return self.send_error_message(chat_id, sub_result['error'])

    def _handle_unsubscribe_currency(self, chat_id: str, user_id: int, result: Dict) -> dict:
        """处理取消订阅币种命令"""
        currencies = result['currencies']
        sub_result = self.subscription_manager.unsubscribe_currencies(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram',
            currencies=currencies
        )

        if sub_result['status'] == 'success':
            message = f"✅ *取消币种订阅成功*\n\n"
            if sub_result['removed']:
                message += f"已移除币种: {', '.join(sub_result['removed'])}\n"
                message += f"当前订阅: {', '.join(sub_result['currencies'])}"
            else:
                message += f"未订阅这些币种: {', '.join(currencies)}"
            return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        else:
            return self.send_error_message(chat_id, sub_result['error'])

    def _handle_mysubscriptions(self, chat_id: str, user_id: int) -> dict:
        """处理查看订阅命令"""
        subscription = self.subscription_manager.get_or_create_subscription(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram'
        )

        message = "📋 *我的订阅*\n\n"

        # 币种
        currencies = subscription.get('currencies', [])
        if currencies:
            currency_names = [self.currency_config.get_currency_name(c) or c for c in currencies]
            message += f"💰 *币种*: {', '.join(currencies)}\n"
        else:
            message += f"💰 *币种*: 无\n"

        # 时间级别
        timeframes = subscription.get('timeframes', [])
        if timeframes:
            message += f"⏰ *时间级别*: {', '.join(timeframes)}\n"
        else:
            message += f"⏰ *时间级别*: 全部\n"

        # 信号类型
        signals = subscription.get('signal_types', [])
        if signals:
            message += f"🔔 *信号类型*: {', '.join(signals)}\n"
        else:
            message += f"🔔 *信号类型*: 全部\n"

        # 推送频率
        frequency = subscription.get('frequency', 'all')
        frequency_text = {
            'all': '所有推送',
            'alerts': '仅告警',
            'daily': '每日摘要',
            'none': '暂停推送'
        }.get(frequency, frequency)
        message += f"📬 *推送频率*: {frequency_text}\n"

        return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

    def _handle_my_currencies(self, chat_id: str, user_id: int) -> dict:
        """处理查看我的币种命令"""
        subscription = self.subscription_manager.get_or_create_subscription(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram'
        )

        currencies = subscription.get('currencies', [])
        message = "💰 *我订阅的币种*\n\n"

        if currencies:
            for currency in currencies:
                icon = self.currency_config.get_currency_icon(currency)
                name = self.currency_config.get_currency_name(currency) or currency
                message += f"{icon} *{currency}* - {name}\n"
        else:
            message += "未订阅任何币种"

        return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

    def _handle_list_currencies(self, chat_id: str) -> dict:
        """处理列出所有币种命令"""
        message = self.currency_config.format_currencies_list()
        return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

    def _handle_frequency(self, chat_id: str, user_id: int, result: Dict) -> dict:
        """处理设置推送频率命令"""
        frequency = result['frequency']
        sub_result = self.subscription_manager.set_frequency(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram',
            frequency=frequency
        )

        if sub_result['status'] == 'success':
            frequency_text = {
                'all': '所有推送',
                'alerts': '仅告警',
                'daily': '每日摘要',
                'none': '暂停推送'
            }.get(frequency, frequency)

            message = f"✅ *推送频率已设置*\n\n"
            message += f"当前设置: {frequency_text}"
            return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        else:
            return self.send_error_message(chat_id, sub_result['error'])

    # ==================== 辅助方法 ====================

    def send_help_message(self, chat_id: str) -> dict:
        """发送帮助消息"""
        message = self.command_parser.format_help_message()
        return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

    def send_error_message(self, chat_id: str, error: str) -> dict:
        """发送错误消息"""
        message = f"❌ *错误*\n\n{error}"
        return self.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

    def send_success_message(self, chat_id: str, message: str) -> dict:
        """发送成功消息"""
        success_msg = f"✅ *成功*\n\n{message}"
        return self.send_message(chat_id=chat_id, text=success_msg, parse_mode='Markdown')

    # ==================== 订阅检查方法 ====================

    def should_send_report(self, user_id: int, chat_id: str, currency: str, timeframe: str) -> bool:
        """
        检查是否应该发送报告

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            currency: 币种
            timeframe: 时间级别

        Returns:
            是否应该发送
        """
        return self.alert_filter.should_send_report(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram',
            currency=currency,
            timeframe=timeframe
        )

    def should_send_alert(
        self,
        user_id: int,
        chat_id: str,
        signal_type: str,
        timeframe: str,
        currency: str = 'btc'
    ) -> bool:
        """
        检查是否应该发送告警

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            signal_type: 信号类型
            timeframe: 时间级别
            currency: 币种

        Returns:
            是否应该发送
        """
        return self.alert_filter.should_send_alert(
            user_id=user_id,
            chat_id=chat_id,
            platform='telegram',
            signal_type=signal_type,
            timeframe=timeframe,
            currency=currency
        )


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
