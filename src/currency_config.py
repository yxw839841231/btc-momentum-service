"""
币种配置模块
管理支持的加密货币及其配置
"""

import logging
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CurrencyConfig:
    """币种配置管理"""

    # 默认支持的币种配置
    DEFAULT_CURRENCIES = {
        'BTC': {
            'name': 'Bitcoin',
            'exchange_symbol': 'BTC-USDT',
            'color': '#F7931A',  # 橙色
            'icon': '₿',
            'enabled': True,
            'priority': 0,
            'timeframes': ['2d', '1d', '12h', '6h', '4h', '2h', '1h', '30m']
        },
        'ETH': {
            'name': 'Ethereum',
            'exchange_symbol': 'ETH-USDT',
            'color': '#627EEA',  # 蓝色
            'icon': 'Ξ',
            'enabled': True,
            'priority': 1,
            'timeframes': ['1d', '12h', '6h', '4h', '2h', '1h']
        },
        'SOL': {
            'name': 'Solana',
            'exchange_symbol': 'SOL-USDT',
            'color': '#00FFA3',  # 绿色
            'icon': '◎',
            'enabled': True,
            'priority': 2,
            'timeframes': ['1d', '4h', '1h']
        },
        'BNB': {
            'name': 'Binance Coin',
            'exchange_symbol': 'BNB-USDT',
            'color': '#F3BA2F',  # 黄色
            'icon': 'BNB',
            'enabled': True,
            'priority': 3,
            'timeframes': ['1d', '4h', '1h']
        },
        'XRP': {
            'name': 'Ripple',
            'exchange_symbol': 'XRP-USDT',
            'color': '#23292F',  # 深灰色
            'icon': 'XRP',
            'enabled': True,
            'priority': 4,
            'timeframes': ['1d', '4h', '1h']
        },
        'ADA': {
            'name': 'Cardano',
            'exchange_symbol': 'ADA-USDT',
            'color': '#0033AD',  # 深蓝色
            'icon': 'ADA',
            'enabled': True,
            'priority': 5,
            'timeframes': ['1d', '4h', '1h']
        },
        'DOGE': {
            'name': 'Dogecoin',
            'exchange_symbol': 'DOGE-USDT',
            'color': '#C2A633',  # 金色
            'icon': 'Ð',
            'enabled': True,
            'priority': 6,
            'timeframes': ['1d', '4h', '1h']
        },
        'DOT': {
            'name': 'Polkadot',
            'exchange_symbol': 'DOT-USDT',
            'color': '#E6007A',  # 粉色
            'icon': 'DOT',
            'enabled': True,
            'priority': 7,
            'timeframes': ['1d', '4h', '1h']
        },
        'MATIC': {
            'name': 'Polygon',
            'exchange_symbol': 'MATIC-USDT',
            'color': '#8247E5',  # 紫色
            'icon': 'MATIC',
            'enabled': True,
            'priority': 8,
            'timeframes': ['1d', '4h', '1h']
        },
        'AVAX': {
            'name': 'Avalanche',
            'exchange_symbol': 'AVAX-USDT',
            'color': '#E84142',  # 红色
            'icon': 'AVAX',
            'enabled': True,
            'priority': 9,
            'timeframes': ['1d', '4h', '1h']
        }
    }

    def __init__(self, custom_config: Optional[Dict] = None):
        """
        初始化币种配置

        Args:
            custom_config: 自定义币种配置（可选）
        """
        if custom_config:
            self.currencies = custom_config
        else:
            self.currencies = self.DEFAULT_CURRENCIES

        logger.info(f"币种配置初始化完成，支持 {len(self.currencies)} 个币种")

    def get_exchange_symbol(self, symbol: str) -> str:
        """
        获取交易所交易对符号

        Args:
            symbol: 币种符号

        Returns:
            交易对符号
        """
        symbol_upper = symbol.upper()
        if symbol_upper in self.currencies:
            return self.currencies[symbol_upper]['exchange_symbol']
        return f"{symbol_upper}-USDT"

    def is_supported(self, symbol: str) -> bool:
        """
        检查币种是否支持

        Args:
            symbol: 币种符号

        Returns:
            是否支持
        """
        symbol_upper = symbol.upper()
        return symbol_upper in self.currencies and self.currencies[symbol_upper]['enabled']

    def get_currency_name(self, symbol: str) -> Optional[str]:
        """
        获取币种名称

        Args:
            symbol: 币种符号

        Returns:
            币种名称
        """
        symbol_upper = symbol.upper()
        if symbol_upper in self.currencies:
            return self.currencies[symbol_upper]['name']
        return None

    def get_currency_color(self, symbol: str) -> str:
        """
        获取币种颜色

        Args:
            symbol: 币种符号

        Returns:
            颜色代码
        """
        symbol_upper = symbol.upper()
        if symbol_upper in self.currencies:
            return self.currencies[symbol_upper]['color']
        return '#6C757D'  # 默认灰色

    def get_currency_icon(self, symbol: str) -> str:
        """
        获取币种图标

        Args:
            symbol: 币种符号

        Returns:
            图标符号
        """
        symbol_upper = symbol.upper()
        if symbol_upper in self.currencies:
            return self.currencies[symbol_upper]['icon']
        return '📊'

    def get_currency_timeframes(self, symbol: str) -> List[str]:
        """
        获取币种支持的时间级别

        Args:
            symbol: 币种符号

        Returns:
            时间级别列表
        """
        symbol_upper = symbol.upper()
        if symbol_upper in self.currencies:
            return self.currencies[symbol_upper]['timeframes']
        return ['1d', '4h', '1h']  # 默认时间级别

    def get_all_supported_symbols(self) -> List[str]:
        """
        获取所有支持的币种符号

        Returns:
            币种符号列表
        """
        return [
            symbol for symbol, config in self.currencies.items()
            if config['enabled']
        ]

    def get_all_currencies_info(self) -> List[Dict]:
        """
        获取所有币种信息

        Returns:
            币种信息列表
        """
        currencies_list = []

        for symbol, config in sorted(
            self.currencies.items(),
            key=lambda x: x[1]['priority']
        ):
            if config['enabled']:
                currencies_list.append({
                    'symbol': symbol,
                    'name': config['name'],
                    'exchange_symbol': config['exchange_symbol'],
                    'color': config['color'],
                    'icon': config['icon']
                })

        return currencies_list

    def format_currencies_list(self) -> str:
        """
        格式化币种列表文本

        Returns:
            格式化的文本
        """
        lines = ["📋 *支持的币种*\n"]

        for currency in self.get_all_currencies_info():
            icon = currency['icon']
            symbol = currency['symbol']
            name = currency['name']
            lines.append(f"{icon} *{symbol}* - {name}")

        return "\n".join(lines)


# 全局配置实例
currency_config = CurrencyConfig()


if __name__ == "__main__":
    # 测试代码
    config = CurrencyConfig()

    print("=" * 60)
    print("币种配置测试")
    print("=" * 60)

    # 测试获取交易对符号
    print("\n获取交易对符号:")
    for symbol in ['BTC', 'ETH', 'SOL']:
        print(f"  {symbol} -> {config.get_exchange_symbol(symbol)}")

    # 测试检查支持
    print("\n检查币种支持:")
    for symbol in ['BTC', 'ETH', 'XYZ']:
        print(f"  {symbol}: {'✅ 支持' if config.is_supported(symbol) else '❌ 不支持'}")

    # 测试获取币种信息
    print("\n币种信息:")
    info = config.get_all_currencies_info()
    for currency in info[:3]:
        print(f"  {currency['symbol']}: {currency['name']} ({currency['color']})")

    # 测试格式化列表
    print("\n格式化币种列表:")
    print(config.format_currencies_list())
