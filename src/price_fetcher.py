"""
价格获取模块
从交易所获取实时价格数据（支持多币种）
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Optional, List
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.currency_config import CurrencyConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PriceFetcher:
    """价格获取器（支持多币种）"""

    def __init__(self, exchange: str = "okx"):
        """
        初始化价格获取器

        Args:
            exchange: 交易所名称 (okx, binance, etc.)
        """
        self.exchange = exchange
        self.currency_config = CurrencyConfig()
        logger.info(f"价格获取器初始化: {exchange}")

    def fetch_price_okx(self, symbol: str = "BTC") -> Optional[Dict]:
        """
        从 OKX 获取价格

        Args:
            symbol: 币种符号

        Returns:
            价格信息字典
        """
        try:
            # 获取交易对符号
            inst_id = self.currency_config.get_exchange_symbol(symbol)
            url = f"https://www.okx.com/api/v5/market/ticker?instId={inst_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("code") == "0" and data.get("data"):
                ticker = data["data"][0]
                price = float(ticker.get("last", 0))
                price_24h_high = float(ticker.get("high24h", 0))
                price_24h_low = float(ticker.get("low24h", 0))

                # 计算24小时变化
                change_24h = price - price_24h_low
                change_24h_pct = (change_24h / price_24h_low * 100) if price_24h_low > 0 else 0

                # 格式化价格显示
                price_formatted = f"{price:,.2f}"
                change_24h_formatted = round(change_24h, 2)
                change_24h_pct_formatted = round(change_24h_pct, 2)

                return {
                    "symbol": symbol.upper(),
                    "price": price_formatted,
                    "price_raw": price,
                    "change_24h": change_24h_formatted,
                    "change_24h_pct": change_24h_pct_formatted,
                    "high_24h": price_24h_high,
                    "low_24h": price_24h_low,
                    "volume": float(ticker.get("vol24h", 0)),
                    "timestamp": datetime.now().isoformat(),
                    "exchange": "OKX"
                }
        except Exception as e:
            logger.error(f"从 OKX 获取 {symbol} 价格失败: {e}")
            return None

    def fetch_price_binance(self, symbol: str = "BTC") -> Optional[Dict]:
        """
        从 Binance 获取价格

        Args:
            symbol: 币种符号

        Returns:
            价格信息字典
        """
        try:
            # Binance 使用不同的符号格式
            binance_symbol = f"{symbol.upper()}USDT"
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={binance_symbol}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            ticker = response.json()
            price = float(ticker.get("lastPrice", 0))
            change_24h = float(ticker.get("priceChange", 0))
            change_24h_pct = float(ticker.get("priceChangePercent", 0))

            price_formatted = f"{price:,.2f}"
            change_24h_formatted = round(change_24h, 2)
            change_24h_pct_formatted = round(change_24h_pct, 2)

            return {
                "symbol": symbol.upper(),
                "price": price_formatted,
                "price_raw": price,
                "change_24h": change_24h_formatted,
                "change_24h_pct": change_24h_pct_formatted,
                "high_24h": float(ticker.get("highPrice", 0)),
                "low_24h": float(ticker.get("lowPrice", 0)),
                "volume": float(ticker.get("volume", 0)),
                "timestamp": datetime.now().isoformat(),
                "exchange": "Binance"
            }
        except Exception as e:
            logger.error(f"从 Binance 获取 {symbol} 价格失败: {e}")
            return None

    def fetch_price(self, symbol: str = "BTC", exchange: Optional[str] = None) -> Dict:
        """
        获取币种价格（自动尝试多个交易所）

        Args:
            symbol: 币种符号
            exchange: 指定交易所，如果为 None 则尝试配置的交易所

        Returns:
            价格信息字典
        """
        exchange_to_use = exchange or self.exchange

        # 先尝试指定的交易所
        if exchange_to_use == "okx":
            price_data = self.fetch_price_okx(symbol)
            if price_data:
                return price_data
        elif exchange_to_use == "binance":
            price_data = self.fetch_price_binance(symbol)
            if price_data:
                return price_data

        # 如果失败，尝试其他交易所
        logger.warning(f"从 {exchange_to_use} 获取 {symbol} 价格失败，尝试其他交易所")

        # 尝试 OKX
        price_data = self.fetch_price_okx(symbol)
        if price_data:
            return price_data

        # 尝试 Binance
        price_data = self.fetch_price_binance(symbol)
        if price_data:
            return price_data

        # 如果全部失败，返回默认值
        logger.error(f"所有交易所获取 {symbol} 价格失败，使用默认值")
        return {
            "symbol": symbol.upper(),
            "price": "N/A",
            "price_raw": 0,
            "change_24h": 0,
            "change_24h_pct": 0,
            "high_24h": 0,
            "low_24h": 0,
            "volume": 0,
            "timestamp": datetime.now().isoformat(),
            "exchange": "N/A"
        }

    def fetch_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        批量获取多个币种价格

        Args:
            symbols: 币种符号列表

        Returns:
            币种到价格的映射字典
        """
        prices = {}
        for symbol in symbols:
            price_data = self.fetch_price(symbol)
            prices[symbol.upper()] = price_data
        return prices


# 向后兼容的别名
BTCPriceFetcher = PriceFetcher


if __name__ == "__main__":
    # 测试代码
    fetcher = PriceFetcher()

    # 测试单个币种
    print("=" * 60)
    print("BTC 价格信息")
    print("=" * 60)
    price_data = fetcher.fetch_price("BTC")
    if price_data:
        print(f"当前价格: ${price_data['price']}")
        print(f"24h涨跌: {price_data['change_24h']:+.2f} ({price_data['change_24h_pct']:+.2f}%)")
        print(f"24h最高: ${price_data['high_24h']:,.2f}")
        print(f"24h最低: ${price_data['low_24h']:,.2f}")
        print(f"24h成交量: {price_data['volume']:,.0f} BTC")
        print(f"数据来源: {price_data['exchange']}")
        print(f"更新时间: {price_data['timestamp']}")
        print("=" * 60)
    else:
        print("❌ 价格获取失败")

    # 测试批量获取
    print("\n批量获取价格:")
    prices = fetcher.fetch_prices(["BTC", "ETH", "SOL"])
    for symbol, data in prices.items():
        if data.get("price") != "N/A":
            print(f"  {symbol}: ${data['price']} ({data['change_24h_pct']:+.2f}%)")
        else:
            print(f"  {symbol}: 获取失败")
