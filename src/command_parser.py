"""
命令解析器模块
解析用户发送的订阅命令
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CommandParser:
    """命令解析器"""

    # 支持的时间级别
    VALID_TIMEFRAMES = {'2d', '1d', '12h', '6h', '4h', '2h', '1h', '30m'}

    # 支持的信号类型
    VALID_SIGNAL_TYPES = {'divergence', 'buy_signal', 'sell_signal', 'discrete_control'}

    # 支持的币种
    VALID_CURRENCIES = {
        'BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'DOT', 'MATIC', 'AVAX'
    }

    # 支持的推送频率
    VALID_FREQUENCIES = {'all', 'alerts', 'daily', 'none'}

    # 信号类型别名映射
    SIGNAL_TYPE_ALIASES = {
        'divergence': ['divergence', 'div', '背离', 'divergence'],
        'buy_signal': ['buy_signal', 'buy', '买点', '买入信号', 'buy'],
        'sell_signal': ['sell_signal', 'sell', '卖点', '卖出信号', 'sell'],
        'discrete_control': ['discrete_control', 'dc', '分立调控', '调控']
    }

    # 推送频率别名映射
    FREQUENCY_ALIASES = {
        'all': ['all', '全部', '所有', 'a'],
        'alerts': ['alerts', '告警', 'alert', 'al'],
        'daily': ['daily', '每天', '每日', '摘要', 'd'],
        'none': ['none', '无', '关闭', '暂停', 'n']
    }

    def __init__(self):
        """初始化命令解析器"""
        logger.info("命令解析器初始化完成")

    def parse_command(self, text: str) -> Dict:
        """
        解析命令

        Args:
            text: 用户输入的文本

        Returns:
            解析结果
        """
        text = text.strip()
        if not text:
            return {
                'status': 'error',
                'error': '空命令'
            }

        # 移除开头的斜杠（如果有）
        if text.startswith('/'):
            text = text[1:].strip()

        # 分割命令和参数
        parts = text.split(None, 1)
        command = parts[0].lower() if parts else ''
        args = parts[1].strip() if len(parts) > 1 else ''

        # 命令路由
        if command in ['subscribe', 'sub']:
            return self.parse_subscribe_command(args)
        elif command in ['unsubscribe', 'unsub']:
            return self.parse_unsubscribe_command(args)
        elif command in ['subscribe_signal', 'sub_signal', 'ssub']:
            return self.parse_subscribe_signal_command(args)
        elif command in ['unsubscribe_signal', 'unsub_signal', 'usub']:
            return self.parse_unsubscribe_signal_command(args)
        elif command in ['subscribe_currency', 'sub_currency', 'subcur']:
            return self.parse_subscribe_currency_command(args)
        elif command in ['unsubscribe_currency', 'unsub_currency', 'unsubcur']:
            return self.parse_unsubscribe_currency_command(args)
        elif command in ['mysubscriptions', 'mysubs', 'mysub', 'my']:
            return {'status': 'success', 'command': 'mysubscriptions'}
        elif command in ['my_currencies', 'mycur', 'mc']:
            return {'status': 'success', 'command': 'my_currencies'}
        elif command in ['list_currencies', 'listcur', 'lc']:
            return {'status': 'success', 'command': 'list_currencies'}
        elif command in ['frequency', 'freq', 'f']:
            return self.parse_frequency_command(args)
        elif command in ['help', 'h', '?']:
            return {'status': 'success', 'command': 'help'}
        else:
            return {
                'status': 'error',
                'error': f'未知命令: /{command}\n输入 /help 查看帮助'
            }

    def parse_subscribe_command(self, args: str) -> Dict:
        """
        解析订阅时间级别命令

        Args:
            args: 参数字符串

        Returns:
            解析结果
        """
        if not args:
            return {
                'status': 'error',
                'error': '请指定要订阅的时间级别\n例如: /subscribe 1d 4h 1h'
            }

        # 提取时间级别
        timeframes = self.extract_timeframes(args)

        if not timeframes:
            return {
                'status': 'error',
                'error': f'无效的时间级别\n支持: {", ".join(sorted(self.VALID_TIMEFRAMES))}'
            }

        return {
            'status': 'success',
            'command': 'subscribe',
            'timeframes': timeframes
        }

    def parse_unsubscribe_command(self, args: str) -> Dict:
        """
        解析取消订阅时间级别命令

        Args:
            args: 参数字符串

        Returns:
            解析结果
        """
        if not args:
            return {
                'status': 'error',
                'error': '请指定要取消的时间级别\n例如: /unsubscribe 30m 1h'
            }

        # 提取时间级别
        timeframes = self.extract_timeframes(args)

        if not timeframes:
            return {
                'status': 'error',
                'error': f'无效的时间级别\n支持: {", ".join(sorted(self.VALID_TIMEFRAMES))}'
            }

        return {
            'status': 'success',
            'command': 'unsubscribe',
            'timeframes': timeframes
        }

    def parse_subscribe_signal_command(self, args: str) -> Dict:
        """
        解析订阅信号类型命令

        Args:
            args: 参数字符串

        Returns:
            解析结果
        """
        if not args:
            return {
                'status': 'error',
                'error': '请指定要订阅的信号类型\n例如: /subscribe_signal divergence buy_signal'
            }

        # 提取信号类型
        signals = self.extract_signal_types(args)

        if not signals:
            return {
                'status': 'error',
                'error': f'无效的信号类型\n支持: divergence, buy_signal, sell_signal, discrete_control'
            }

        return {
            'status': 'success',
            'command': 'subscribe_signal',
            'signals': signals
        }

    def parse_unsubscribe_signal_command(self, args: str) -> Dict:
        """
        解析取消订阅信号类型命令

        Args:
            args: 参数字符串

        Returns:
            解析结果
        """
        if not args:
            return {
                'status': 'error',
                'error': '请指定要取消的信号类型\n例如: /unsubscribe_signal divergence'
            }

        # 提取信号类型
        signals = self.extract_signal_types(args)

        if not signals:
            return {
                'status': 'error',
                'error': f'无效的信号类型\n支持: divergence, buy_signal, sell_signal, discrete_control'
            }

        return {
            'status': 'success',
            'command': 'unsubscribe_signal',
            'signals': signals
        }

    def parse_subscribe_currency_command(self, args: str) -> Dict:
        """
        解析订阅币种命令

        Args:
            args: 参数字符串

        Returns:
            解析结果
        """
        if not args:
            return {
                'status': 'error',
                'error': '请指定要订阅的币种\n例如: /subscribe_currency btc eth sol'
            }

        # 提取币种
        currencies = self.extract_currencies(args)

        if not currencies:
            return {
                'status': 'error',
                'error': f'无效的币种\n支持: {", ".join(sorted(self.VALID_CURRENCIES))}'
            }

        return {
            'status': 'success',
            'command': 'subscribe_currency',
            'currencies': currencies
        }

    def parse_unsubscribe_currency_command(self, args: str) -> Dict:
        """
        解析取消订阅币种命令

        Args:
            args: 参数字符串

        Returns:
            解析结果
        """
        if not args:
            return {
                'status': 'error',
                'error': '请指定要取消的币种\n例如: /unsubscribe_currency eth'
            }

        # 提取币种
        currencies = self.extract_currencies(args)

        if not currencies:
            return {
                'status': 'error',
                'error': f'无效的币种\n支持: {", ".join(sorted(self.VALID_CURRENCIES))}'
            }

        return {
            'status': 'success',
            'command': 'unsubscribe_currency',
            'currencies': currencies
        }

    def parse_frequency_command(self, args: str) -> Dict:
        """
        解析设置推送频率命令

        Args:
            args: 参数字符串

        Returns:
            解析结果
        """
        if not args:
            return {
                'status': 'error',
                'error': '请指定推送频率\n例如: /frequency alerts\n支持: all, alerts, daily, none'
            }

        # 解析频率
        frequency = self.normalize_frequency(args)

        if not frequency:
            return {
                'status': 'error',
                'error': f'无效的推送频率\n支持: all (所有), alerts (仅告警), daily (每日摘要), none (暂停)'
            }

        return {
            'status': 'success',
            'command': 'frequency',
            'frequency': frequency
        }

    # ==================== 辅助方法 ====================

    def extract_timeframes(self, text: str) -> List[str]:
        """
        从文本中提取时间级别

        Args:
            text: 文本

        Returns:
            时间级别列表
        """
        # 匹配时间级别模式（数字 + d/h/m）
        pattern = r'\b(\d+[dhm])\b'
        matches = re.findall(pattern, text.lower())

        # 过滤有效的时间级别
        valid_timeframes = [m for m in matches if m in self.VALID_TIMEFRAMES]

        return list(set(valid_timeframes))  # 去重

    def extract_signal_types(self, text: str) -> List[str]:
        """
        从文本中提取信号类型

        Args:
            text: 文本

        Returns:
            信号类型列表
        """
        found_signals = []

        # 检查每个信号类型及其别名
        for signal_type, aliases in self.SIGNAL_TYPE_ALIASES.items():
            for alias in aliases:
                # 使用单词边界匹配
                pattern = r'\b' + re.escape(alias.lower()) + r'\b'
                if re.search(pattern, text.lower()):
                    if signal_type not in found_signals:
                        found_signals.append(signal_type)
                    break

        return found_signals

    def extract_currencies(self, text: str) -> List[str]:
        """
        从文本中提取币种

        Args:
            text: 文本

        Returns:
            币种列表
        """
        found_currencies = []

        # 提取所有大写单词（可能是币种）
        words = re.findall(r'\b([A-Z]{2,10})\b', text.upper())

        for word in words:
            if word in self.VALID_CURRENCIES and word not in found_currencies:
                found_currencies.append(word)

        return found_currencies

    def normalize_frequency(self, text: str) -> Optional[str]:
        """
        标准化推送频率

        Args:
            text: 文本

        Returns:
            标准化的频率值
        """
        text_lower = text.lower().strip()

        # 检查每个频率及其别名
        for frequency, aliases in self.FREQUENCY_ALIASES.items():
            if text_lower in [alias.lower() for alias in aliases]:
                return frequency

        return None

    def format_help_message(self) -> str:
        """
        格式化帮助消息

        Returns:
            帮助消息文本
        """
        help_text = """📖 *订阅管理帮助*

🎯 *时间级别订阅*
`/subscribe <时间级别>` - 订阅时间级别
  例如: `/subscribe 1d 4h 1h`
`/unsubscribe <时间级别>` - 取消订阅
  例如: `/unsubscribe 30m`

支持的时间级别:
  `2d` `1d` `12h` `6h` `4h` `2h` `1h` `30m`

🔔 *信号类型订阅*
`/subscribe_signal <类型>` - 订阅信号
  例如: `/subscribe_signal divergence`
`/unsubscribe_signal <类型>` - 取消订阅
  例如: `/unsubscribe_signal sell_signal`

支持的信号类型:
  `divergence` - 背离信号
  `buy_signal` - 买点信号
  `sell_signal` - 卖点信号
  `discrete_control` - 分立调控

💰 *币种订阅*
`/subscribe_currency <币种>` - 订阅币种
  例如: `/subscribe_currency btc eth sol`
`/unsubscribe_currency <币种>` - 取消订阅
  例如: `/unsubscribe_currency eth`

支持的币种:
  `BTC` `ETH` `SOL` `BNB` `XRP` `ADA` `DOGE` `DOT` `MATIC` `AVAX`

⚙️ *推送频率*
`/frequency <频率>` - 设置推送频率
  例如: `/frequency alerts`

支持的频率:
  `all` - 接收所有推送（默认）
  `alerts` - 仅重要告警
  `daily` - 每日摘要
  `none` - 暂停推送

📋 *查询订阅*
`/mysubscriptions` - 查看我的订阅
`/my_currencies` - 查看我订阅的币种
`/list_currencies` - 列出所有支持的币种

💡 *提示*
• 不指定时间级别 = 接收所有时间级别
• 不指定信号类型 = 接收所有信号类型
• 不指定币种 = 默认只接收 BTC
• 可以组合使用多个订阅条件

📱 *示例*
```
/subscribe 1d 4h              # 订阅日线和4小时线
/subscribe_currency btc eth   # 订阅 BTC 和 ETH
/subscribe_signal divergence  # 订阅背离信号
/frequency alerts             # 仅接收告警
```
"""
        return help_text


if __name__ == "__main__":
    # 测试代码
    parser = CommandParser()

    # 测试命令解析
    test_commands = [
        "/subscribe 1d 4h 1h",
        "/unsubscribe 30m",
        "/subscribe_signal divergence",
        "/subscribe_currency btc eth sol",
        "/frequency alerts",
        "/mysubscriptions",
        "/help",
        "/invalid_command",
        "/subscribe",
        ""
    ]

    print("=" * 60)
    print("命令解析测试")
    print("=" * 60)

    for cmd in test_commands:
        print(f"\n命令: {cmd}")
        result = parser.parse_command(cmd)
        print(f"结果: {result}")
