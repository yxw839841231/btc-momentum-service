#!/bin/bash
# 多币种分析诊断脚本

echo "============================================================"
echo "多币种分析诊断"
echo "============================================================"

echo ""
echo "1. 检查 config.json"
echo "-------------------"
if [ -f "config.json" ]; then
    echo "✅ config.json 存在"
    echo "币种配置:"
    cat config.json | grep -A 1 '"currencies"' | grep '\['
else
    echo "❌ config.json 不存在"
    exit 1
fi

echo ""
echo "2. 检查 Python 环境"
echo "--------------------"
python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Python 可用"
else
    echo "❌ Python 不可用"
    exit 1
fi

echo ""
echo "3. 检查必要文件"
echo "----------------"
files=(
    "scripts/run_analysis_multi.py"
    "src/multi_currency_fetcher.py"
    "src/analyzer.py"
    "scripts/fetch_btc_data.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file 不存在"
    fi
done

echo ""
echo "4. 测试价格获取"
echo "----------------"
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from src.multi_currency_fetcher import MultiCurrencyPriceFetcher

fetcher = MultiCurrencyPriceFetcher(exchange='okx')
currencies = ['BTC', 'SUI', 'SOL']

for currency in currencies:
    price_data = fetcher.fetch_currency_price(currency)
    if price_data:
        print(f'✅ {currency}: \${price_data[\"price\"]} ({price_data[\"exchange\"]})')
    else:
        print(f'❌ {currency}: 获取失败')
"

echo ""
echo "5. 检查 GitHub Actions workflow"
echo "--------------------------------"
if [ -f ".github/workflows/multi-currency-analysis.yml" ]; then
    echo "✅ multi-currency-analysis.yml 存在"
    echo "运行脚本:"
    grep "python scripts/" .github/workflows/multi-currency-analysis.yml | head -1
else
    echo "❌ multi-currency-analysis.yml 不存在"
fi

echo ""
echo "============================================================"
echo "诊断完成"
echo "============================================================"
