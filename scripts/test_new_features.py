#!/usr/bin/env python3
"""
测试新功能：CoinGecko API 和价格预警
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.multi_currency_fetcher import MultiCurrencyPriceFetcher
from src.alert_manager import AlertManager, check_all_alerts

def test_coingecko_api():
    """测试 CoinGecko API"""
    print("="*60)
    print("测试 1: CoinGecko API 价格获取")
    print("="*60)

    fetcher = MultiCurrencyPriceFetcher(exchange="okx")

    # 测试 SUI（CoinGecko 支持）
    print("\n正在获取 SUI 价格...")
    sui_price = fetcher.fetch_currency_price("SUI")

    if sui_price:
        print(f"✅ SUI 价格: ${sui_price['price']} ({sui_price['change_24h_pct']:+.2f}%)")
        print(f"   来源: {sui_price['exchange']}")
    else:
        print("❌ SUI 价格获取失败")

    # 测试其他币种
    test_currencies = ["BTC", "ETH", "SOL", "SUI"]
    print(f"\n批量获取: {', '.join(test_currencies)}")

    results = fetcher.fetch_all_prices(test_currencies)
    for symbol, data in results.items():
        source = data['exchange']
        print(f"  {symbol}: ${data['price']} ({data['change_24h_pct']:+.2f}%) [{source}]")

def test_price_alerts():
    """测试价格预警"""
    print("\n" + "="*60)
    print("测试 2: 价格预警功能")
    print("="*60)

    alert_manager = AlertManager()

    # 设置价格目标
    alert_manager.set_price_target("BTC", high=100000, low=90000)
    print("\n✅ 已设置 BTC 价格目标:")
    print("   上限: $100,000")
    print("   下限: $90,000")

    # 测试场景 1: 大幅波动
    print("\n【场景 1】大幅波动测试")
    price_data_1 = {
        "price": "$105,000.00",
        "price_raw": 105000.0,
        "change_24h_pct": 6.5,  # 6.5% 涨跌（超过5%阈值）
        "exchange": "OKX"
    }

    alerts_1 = alert_manager.check_price_alerts("BTC", price_data_1)
    if alerts_1:
        print(f"✅ 检测到 {len(alerts_1)} 个告警:")
        for alert in alerts_1:
            print(f"   - {alert.format_message()}")
    else:
        print("❌ 未检测到告警")

    # 测试场景 2: 价格目标
    print("\n【场景 2】价格目标测试")
    price_data_2 = {
        "price": "$101,500.00",
        "price_raw": 101500.0,  # 超过 $100,000
        "change_24h_pct": 2.5,
        "exchange": "OKX"
    }

    alerts_2 = alert_manager.check_price_alerts("BTC", price_data_2)
    if alerts_2:
        print(f"✅ 检测到 {len(alerts_2)} 个告警:")
        for alert in alerts_2:
            print(f"   - {alert.format_message()}")
    else:
        print("❌ 未检测到告警")

    # 测试场景 3: 正常波动（无告警）
    print("\n【场景 3】正常波动测试")
    price_data_3 = {
        "price": "$98,000.00",
        "price_raw": 98000.0,  # 在目标范围内
        "change_24h_pct": 2.0,   # 低于5%阈值
        "exchange": "OKX"
    }

    alerts_3 = alert_manager.check_price_alerts("BTC", price_data_3)
    if alerts_3:
        print(f"⚠️  检测到 {len(alerts_3)} 个告警:")
        for alert in alerts_3:
            print(f"   - {alert.format_message()}")
    else:
        print("✅ 无告警（正常波动）")

def test_alert_cooldown():
    """测试告警冷却"""
    print("\n" + "="*60)
    print("测试 3: 告警冷却机制")
    print("="*60)

    alert_manager = AlertManager()

    price_data = {
        "price": "$106,000.00",
        "price_raw": 106000.0,
        "change_24h_pct": 7.0,
        "exchange": "OKX"
    }

    print("\n第一次检查...")
    alerts_1 = alert_manager.check_price_alerts("BTC", price_data)
    print(f"检测到 {len(alerts_1)} 个告警")

    print("\n立即第二次检查（应在冷却期）...")
    alerts_2 = alert_manager.check_price_alerts("BTC", price_data)
    print(f"检测到 {len(alerts_2)} 个告警（应为0，因为冷却）")

    if len(alerts_1) > 0 and len(alerts_2) == 0:
        print("✅ 冷却机制工作正常")
    else:
        print("❌ 冷却机制可能有问题")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("新功能测试")
    print("="*60)

    # 测试 CoinGecko API
    test_coingecko_api()

    # 测试价格预警
    test_price_alerts()

    # 测试告警冷却
    test_alert_cooldown()

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

    print("\n✅ 功能验证:")
    print("  1. CoinGecko API - 获取 SUI 等小币种价格")
    print("  2. 价格预警 - 大幅波动告警（±5%）")
    print("  3. 价格目标 - 突破/跌破关键价位")
    print("  4. 告警冷却 - 避免重复告警（60分钟）")
    print("="*60)
