#!/usr/bin/env python3
"""
测试多币种分析功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import MomentumAnalyzer

def test_currency_analysis(currency: str):
    """测试单个币种的分析"""
    print(f"\n{'='*60}")
    print(f"测试 {currency} 分析")
    print(f"{'='*60}")

    symbol = f"{currency}-USDT"
    analyzer = MomentumAnalyzer()

    print(f"交易对: {symbol}")
    print("开始分析...")

    result = analyzer.run_full_analysis(symbol=symbol)

    if result["status"] == "success":
        print(f"✅ {currency} 分析成功")
        print(f"数据文件: {result.get('data_file', 'N/A')}")
    else:
        print(f"❌ {currency} 分析失败")
        print(f"错误: {result.get('error', 'Unknown error')}")

    return result

if __name__ == "__main__":
    # 测试配置的币种
    test_currencies = ["BTC", "SUI", "SOL"]

    print("="*60)
    print("多币种分析测试")
    print("="*60)

    results = {}
    for currency in test_currencies:
        try:
            result = test_currency_analysis(currency)
            results[currency] = result
        except Exception as e:
            print(f"❌ {currency} 测试出错: {e}")
            results[currency] = {"status": "error", "error": str(e)}

    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for currency, result in results.items():
        status = "✅ 成功" if result.get("status") == "success" else "❌ 失败"
        print(f"{currency}: {status}")

    print("\n" + "="*60)
