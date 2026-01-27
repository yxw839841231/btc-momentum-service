#!/usr/bin/env python3
"""
测试多币种分析流程（完整模拟）
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_config_loading():
    """测试配置加载"""
    print("="*60)
    print("测试 1: 配置加载")
    print("="*60)

    from scripts.run_analysis_multi import load_config

    try:
        config = load_config()
        print(f"✅ 配置加载成功")
        print(f"币种: {config['analysis']['currencies']}")
        print(f"时间级别: {config['analysis']['timeframes']}")
        print(f"交易所: {config['analysis']['exchange']}")
        return config
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return None

def test_currency_iteration(config):
    """测试币种循环"""
    print("\n" + "="*60)
    print("测试 2: 币种循环")
    print("="*60)

    currencies = config["analysis"].get("currencies", ["BTC"])
    print(f"配置的币种: {currencies}")
    print(f"币种数量: {len(currencies)}")

    for i, currency in enumerate(currencies, 1):
        print(f"  {i}. {currency}")

    return currencies

def test_price_fetching(currencies):
    """测试价格获取"""
    print("\n" + "="*60)
    print("测试 3: 价格获取")
    print("="*60)

    from src.multi_currency_fetcher import MultiCurrencyPriceFetcher

    fetcher = MultiCurrencyPriceFetcher(exchange="okx")
    prices = {}

    for currency in currencies:
        print(f"\n获取 {currency} 价格...")
        try:
            price_data = fetcher.fetch_currency_price(currency)
            if price_data:
                print(f"  ✅ {currency}: ${price_data['price']} ({price_data['change_24h_pct']:+.2f}%)")
                print(f"  来源: {price_data['exchange']}")
                prices[currency] = price_data
            else:
                print(f"  ❌ {currency}: 获取失败")
        except Exception as e:
            print(f"  ❌ {currency}: 错误 - {e}")

    return prices

def test_analysis_preparation(currencies):
    """测试分析准备（不实际运行分析）"""
    print("\n" + "="*60)
    print("测试 4: 分析准备")
    print("="*60)

    from src.analyzer import MomentumAnalyzer

    for currency in currencies:
        symbol = f"{currency}-USDT"
        print(f"\n{currency}:")
        print(f"  交易对: {symbol}")

        # 测试是否可以创建分析器
        try:
            analyzer = MomentumAnalyzer()
            print(f"  ✅ 分析器创建成功")
        except Exception as e:
            print(f"  ❌ 分析器创建失败: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("多币种分析流程测试")
    print("="*60)

    # 测试 1: 配置加载
    config = test_config_loading()
    if not config:
        print("\n❌ 配置加载失败，无法继续测试")
        sys.exit(1)

    # 测试 2: 币种循环
    currencies = test_currency_iteration(config)

    # 测试 3: 价格获取
    prices = test_price_fetching(currencies)

    # 测试 4: 分析准备
    test_analysis_preparation(currencies)

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"配置的币种: {', '.join(currencies)}")
    print(f"成功获取价格的币种: {', '.join(prices.keys()) if prices else '无'}")
    print(f"预期分析结果: {len(currencies)} 个币种的分析报告")
    print("="*60)
