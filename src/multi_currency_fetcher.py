"""
多币种价格获取模块
从交易所获取实时价格数据（支持 SUI 等多个币种）
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiCurrencyPriceFetcher:
    """多币种价格获取器（支持 BTC、ETH、SOL、SUI 等）"""

    # 支持的币种及其对应的交易对
    SUPPORTED_CURRENCIES = {
        'BTC': 'BTC-USDT',
        'ETH': 'ETH-USDT',
        'SOL': 'SOL-USDT',
        'SUI': 'SUI-USDT',  # Sui Network
        'BNB': 'BNB-USDT',
        'XRP': 'XRP-USDT',
        'ADA': 'ADA-USDT',
        'DOGE': 'DOGE-USDT',
        'DOT': 'DOT-USDT',
        'MATIC': 'MATIC-USDT',
        'AVAX': 'AVAX-USDT'
    }

    def __init__(self, exchange: str = "okx"):
        """
        初始化价格获取器

        Args:
            exchange: 交易所名称 (okx, binance, etc.)
        """
        self.exchange = exchange
        logger.info(f"多币种价格获取器初始化: {exchange}")

    def fetch_currency_price(self, symbol: str = "BTC", use_fallback: bool = True) -> Optional[Dict]:
        """
        从多个交易所获取指定币种的价格（支持容错）

        Args:
            symbol: 币种符号 (BTC, ETH, SOL, SUI, etc.)
            use_fallback: 是否使用备用方案（模拟数据）

        Returns:
            价格信息字典
        """
        symbol_upper = symbol.upper()
        if symbol_upper not in self.SUPPORTED_CURRENCIES:
            logger.warning(f"不支持的币种: {symbol}")
            return None

        # 尝试从 OKX 获取
        price_data = self._fetch_from_okx(symbol_upper)

        # 如果 OKX 失败，尝试从 Binance 获取
        if not price_data:
            price_data = self._fetch_from_binance(symbol_upper)

        # 如果都失败，使用模拟数据
        if not price_data and use_fallback:
            logger.warning(f"{symbol_upper} 价格获取失败，使用模拟数据")
            price_data = self._get_fallback_price(symbol_upper)

        return price_data

    def _fetch_from_okx(self, symbol: str) -> Optional[Dict]:
        """从 OKX 获取价格"""
        try:
            inst_id = self.SUPPORTED_CURRENCIES[symbol]
            url = f"https://www.okx.com/api/v5/market/ticker?instId={inst_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("code") == "0" and data.get("data"):
                ticker = data["data"][0]
                price = float(ticker.get("last", 0))

                if price > 0:
                    return self._format_price_data(symbol, price, ticker)
                else:
                    logger.warning(f"OKX 返回的 {symbol} 价格为0")
                    return None
        except Exception as e:
            logger.debug(f"从 OKX 获取 {symbol} 失败: {e}")
            return None

    def _fetch_from_binance(self, symbol: str) -> Optional[Dict]:
        """从 Binance 获取价格"""
        try:
            binance_symbol = f"{symbol}USDT"
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={binance_symbol}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            ticker = response.json()
            price = float(ticker.get("lastPrice", 0))

            if price > 0:
                return self._format_price_data_binance(symbol, price, ticker)
            else:
                logger.warning(f"Binance 返回的 {symbol} 价格为0")
                return None
        except Exception as e:
            logger.debug(f"从 Binance 获取 {symbol} 失败: {e}")
            return None

    def _format_price_data(self, symbol: str, price: float, ticker: dict) -> Dict:
        """格式化 OKX 价格数据"""
        price_24h_high = float(ticker.get("high24h", 0))
        price_24h_low = float(ticker.get("low24h", 0))
        change_24h = price - price_24h_low
        change_24h_pct = (change_24h / price_24h_low * 100) if price_24h_low > 0 else 0

        # 根据价格决定格式化方式
        if price < 0.01:
            price_formatted = f"{price:.6f}".rstrip('0').rstrip('.')
        elif price < 1:
            price_formatted = f"{price:.4f}".rstrip('0').rstrip('.')
        else:
            price_formatted = f"{price:,.2f}"

        change_24h_formatted = round(change_24h, 4) if price < 1 else round(change_24h, 2)
        change_24h_pct_formatted = round(change_24h_pct, 2)

        logger.info(f"✅ {symbol} 价格: ${price_formatted} ({change_24h_pct_formatted:+.2f}%)")

        return {
            "symbol": symbol,
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

    def _format_price_data_binance(self, symbol: str, price: float, ticker: dict) -> Dict:
        """格式化 Binance 价格数据"""
        change_24h = float(ticker.get("priceChange", 0))
        change_24h_pct = float(ticker.get("priceChangePercent", 0))

        if price < 0.01:
            price_formatted = f"{price:.6f}".rstrip('0').rstrip('.')
        elif price < 1:
            price_formatted = f"{price:.4f}".rstrip('0').rstrip('.')
        else:
            price_formatted = f"{price:,.2f}"

        change_24h_formatted = round(change_24h, 4) if price < 1 else round(change_24h, 2)

        logger.info(f"✅ {symbol} 价格: ${price_formatted} ({change_24h_pct:+.2f}%) [Binance]")

        return {
            "symbol": symbol,
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

    def _get_fallback_price(self, symbol: str) -> Dict:
        """获取模拟价格数据（当所有交易所都失败时）"""
        # 使用固定的模拟价格
        fallback_prices = {
            'BTC': 98000.0,
            'ETH': 3500.0,
            'SOL': 150.0,
            'SUI': 1.5,  # Sui Network 假设价格
            'BNB': 600.0,
            'XRP': 2.5,
            'ADA': 0.5,
            'DOGE': 0.15,
            'DOT': 7.0,
            'MATIC': 0.85,
            'AVAX': 35.0
        }

        price = fallback_prices.get(symbol.upper(), 1.0)

        # 添加小的随机波动模拟实时变化
        import random
        variation = random.uniform(-0.02, 0.02)  # ±2% 随机波动
        price = price * (1 + variation)

        if price < 0.01:
            price_formatted = f"{price:.6f}".rstrip('0').rstrip('.')
        elif price < 1:
            price_formatted = f"{price:.4f}".rstrip('0').rstrip('.')
        else:
            price_formatted = f"{price:,.2f}"

        logger.info(f"⚠️  {symbol} 使用模拟价格: ${price_formatted}")

        return {
            "symbol": symbol.upper(),
            "price": price_formatted,
            "price_raw": price,
            "change_24h": 0,
            "change_24h_pct": 0,
            "high_24h": price * 1.02,
            "low_24h": price * 0.98,
            "volume": 1000000,
            "timestamp": datetime.now().isoformat(),
            "exchange": "Simulated"
        }

    def fetch_all_prices(self, symbols: list) -> Dict[str, Dict]:
        """
        批量获取多个币种的价格

        Args:
            symbols: 币种列表

        Returns:
            币种到价格的映射字典
        """
        prices = {}
        for symbol in symbols:
            price_data = self.fetch_currency_price(symbol)
            if price_data:
                prices[symbol.upper()] = price_data
        return prices


# 向后兼容：保持 BTCPriceFetcher 类名可用
class BTCPriceFetcher(MultiCurrencyPriceFetcher):
    """BTC 价格获取器（向后兼容别名）"""

    def fetch_price(self, symbol: str = "BTC") -> Dict:
        """
        获取指定币种价格（兼容旧接口）

        Args:
            symbol: 币种符号

        Returns:
            价格信息字典
        """
        price_data = self.fetch_currency_price(symbol)

        if price_data:
            return price_data

        # 如果获取失败，返回默认值
        logger.error(f"{symbol} 价格获取失败，使用默认值")
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


if __name__ == "__main__":
    # 测试代码
    fetcher = MultiCurrencyPriceFetcher()

    # 测试单个币种
    print("=" * 60)
    print("多币种价格获取测试")
    print("=" * 60)

    # 测试 BTC
    print("\n1. 测试 BTC:")
    btc_price = fetcher.fetch_currency_price("BTC")
    if btc_price:
        print(f"  价格: ${btc_price['price']}")
        print(f"  24h: {btc_price['change_24h']:+.2f} ({btc_price['change_24h_pct']:+.2f}%)")

    # 测试 SUI
    print("\n2. 测试 SUI:")
    sui_price = fetcher.fetch_currency_price("SUI")
    if sui_price:
        print(f"  价格: ${sui_price['price']}")
        print(f"  24h: {sui_price['change_24h']:+.4f} ({sui_price['change_24h_pct']:+.2f}%)")
    else:
        print("  ⚠️  SUI 价格获取失败（可能 OKX 不支持 SUI 交易对）")

    # 测试批量获取
    print("\n3. 批量获取测试:")
    prices = fetcher.fetch_all_prices(["BTC", "ETH", "SUI", "SOL"])
    for symbol, data in prices.items():
        print(f"  {symbol}: ${data['price']} ({data['change_24h_pct']:+.2f}%)")

    print("\n" + "=" * 60)
