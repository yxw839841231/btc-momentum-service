#!/usr/bin/env python3
"""
测试 SUI 币种价格获取
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.multi_currency_fetcher import MultiCurrencyPriceFetcher

def test_sui_price():
    """测试 SUI 价格获取"""
    print("="*60)
    print("SUI 币种价格获取测试")
    print("="*60)

    fetcher = MultiCurrencyPriceFetcher(exchange="okx")

    print("\n正在获取 SUI 价格...")
    sui_price = fetcher.fetch_currency_price("SUI")

    if sui_price:
        print("\n✅ SUI 价格获取成功！")
        print("-" * 40)
        print(f"币种: {sui_price['symbol']}")
        print(f"价格: ${sui_price['price']}")
        print(f"24h涨跌: {sui_price['change_24h']:+.4f}")
        print(f"24h涨跌幅: {sui_price['change_24h_pct']:+.2f}%")
        print(f"24h最高: ${sui_price['high_24h']:,.4f}")
        print(f"24h最低: ${sui_price['low_24h']:,.4f}")
        print(f"24h成交量: {sui_price['volume']:,.0f}")
        print(f"数据来源: {sui_price['exchange']}")
        print(f"更新时间: {sui_price['timestamp']}")
        return True
    else:
        print("\n❌ SUI 价格获取失败")
        print("\n可能的原因:")
        print("1. OKX 交易所不支持 SUI-USDT 交易对")
        print("2. SUI 在 OKX 上的交易对名称可能不同")
        print("3. 网络问题")
        print("\n建议:")
        print("• 检查 OKX 网站确认 SUI 交易对是否存在")
        print("• 尝试其他交易所（如 Binance、KuCoin）")
        print("• 或者使用模拟数据")
        return False

def test_multiple_currencies():
    """测试多个币种包括 SUI"""
    print("\n" + "="*60)
    print("多币种价格获取测试（包括 SUI）")
    print("="*60)

    fetcher = MultiCurrencyPriceFetcher(exchange="okx")

    # 测试币种列表
    test_currencies = ["BTC", "ETH", "SUI", "SOL"]
    print(f"\n测试币种: {', '.join(test_currencies)}")
    print("-" * 40)

    results = fetcher.fetch_all_prices(test_currencies)

    print("\n结果:")
    for symbol, data in results.items():
        if data and data.get("price") != "N/A":
            print(f"  ✅ {symbol}: ${data['price']} ({data['change_24h_pct']:+.2f}%)")
        else:
            print(f"  ❌ {symbol}: 获取失败")

    return results

if __name__ == "__main__":
    # 测试 SUI
    success = test_sui_price()

    # 测试多个币种
    test_multiple_currencies()

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
