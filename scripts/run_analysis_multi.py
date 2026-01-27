#!/usr/bin/env python3
"""
主分析脚本 - 支持多币种配置化推送
执行完整的动能分析流程并推送到 Telegram/飞书
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import MomentumAnalyzer
from src.telegram_bot import TelegramBot
from src.feishu_bot import FeishuBot
from src.report_generator import HTMLReportGenerator
from src.multi_currency_fetcher import MultiCurrencyPriceFetcher
from src.alert_manager import AlertManager, check_all_alerts

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_file="config.json"):
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / config_file

    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        logger.error("请创建 config.json 文件")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 替换环境变量
    def replace_env(obj):
        if isinstance(obj, str):
            # 替换 ${VAR_NAME} 格式的环境变量
            if obj.startswith("${") and obj.endswith("}"):
                env_var = obj[2:-1]
                return os.environ.get(env_var, "")
            return obj
        elif isinstance(obj, dict):
            return {k: replace_env(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_env(item) for item in obj]
        return obj

    config = replace_env(config)
    logger.info(f"✅ 配置加载成功: {config_file}")
    return config


def analyze_currency(currency, config, timeframes):
    """
    分析单个币种

    Args:
        currency: 币种符号 (BTC, ETH, etc.)
        config: 配置字典
        timeframes: 时间级别列表

    Returns:
        分析结果字典
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"开始分析 {currency}")
    logger.info(f"{'='*60}")

    try:
        # 获取价格
        logger.info(f"💰 获取 {currency} 实时价格...")
        price_fetcher = MultiCurrencyPriceFetcher(exchange=config["analysis"]["exchange"])

        # 获取币种价格
        price_data = price_fetcher.fetch_currency_price(currency)

        if price_data and price_data.get("price") != "N/A" and price_data["price"] != "0.00":
            logger.info(f"✅ {currency} 价格: ${price_data['price']} ({price_data['change_24h_pct']:+.2f}%)")
        else:
            logger.warning(f"⚠️  {currency} 价格获取失败，使用模拟数据")

        # 初始化分析器
        logger.info(f"📊 初始化 {currency} 分析器...")
        analyzer = MomentumAnalyzer()

        # 构建交易对符号
        symbol = f"{currency}-USDT"

        # 执行分析 - 传递正确的交易对符号
        logger.info(f"📈 执行 {currency} 动能分析...")
        analysis_result = analyzer.run_full_analysis(symbol=symbol)

        if analysis_result["status"] != "success":
            logger.error(f"❌ {currency} 分析失败: {analysis_result}")
            return None

        # 添加价格和币种信息
        analysis_result["currency"] = currency.upper()
        analysis_result["currency_price"] = price_data
        analysis_result["btc_price"] = price_data  # 向后兼容

        # 生成报告
        logger.info(f"📄 生成 {currency} HTML 报告...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"reports/{currency.lower()}_analysis_{timestamp}.html"

        generator = HTMLReportGenerator()
        report_path = generator.generate_html(analysis_result, report_file)
        logger.info(f"✅ {currency} 报告已生成: {report_path}")

        return {
            "currency": currency.upper(),
            "analysis_result": analysis_result,
            "report_path": report_path,
            "price_data": price_data
        }

    except Exception as e:
        logger.error(f"❌ {currency} 分析过程出错: {e}", exc_info=True)
        return None


def main():
    """主函数"""
    logger.info("="*60)
    logger.info("BTC 动能分析服务启动（多币种配置版）")
    logger.info("="*60)

    # 加载配置
    config = load_config()

    # 检查是否配置了消息推送平台
    telegram_enabled = config["telegram"].get("enabled", False)
    feishu_enabled = config["feishu"].get("enabled", False)

    if not telegram_enabled and not feishu_enabled:
        logger.error("❌ 错误: 请至少配置一个消息推送平台")
        logger.error("")
        logger.error("在 config.json 中配置:")
        logger.error('  "telegram": {"enabled": true}')
        logger.error('  "feishu": {"enabled": true}')
        return 1

    # 获取要分析的币种列表
    currencies = config["analysis"].get("currencies", ["BTC"])
    logger.info(f"📊 配置的币种: {', '.join(currencies)}")

    # 分析所有币种
    all_results = []
    logger.info(f"\n{'='*60}")
    logger.info(f"开始分析 {len(currencies)} 个币种")
    logger.info(f"{'='*60}")

    for i, currency in enumerate(currencies, 1):
        logger.info(f"\n[{i}/{len(currencies)}] 准备分析 {currency}...")
        result = analyze_currency(currency, config, config["analysis"]["timeframes"])
        if result:
            all_results.append(result)
            logger.info(f"✅ {currency} 分析完成")
        else:
            logger.error(f"❌ {currency} 分析失败")

    logger.info(f"\n{'='*60}")
    logger.info(f"分析结果汇总: {len(all_results)}/{len(currencies)} 个币种成功")
    if all_results:
        logger.info(f"成功的币种: {', '.join([r['currency'] for r in all_results])}")
    logger.info(f"{'='*60}\n")

    # 检查价格预警
    logger.info(f"🚨 检查价格预警...")
    alert_manager = AlertManager()
    all_alerts = []

    for result in all_results:
        currency = result["currency"]
        price_data = result["price_data"]
        analysis_result = result["analysis_result"]

        # 检查该币种的告警
        alerts = check_all_alerts(currency, price_data, analysis_result)
        all_alerts.extend(alerts)

    if all_alerts:
        logger.warning(f"⚠️  检测到 {len(all_alerts)} 个预警")
        for alert in all_alerts:
            logger.warning(f"  - {alert.format_message()}")
    else:
        logger.info(f"✅ 无预警")

    if not all_results:
        logger.error("❌ 所有币种分析均失败")
        return 1

    # 生成索引页面
    logger.info(f"\n📋 生成索引页面...")
    subprocess_run([sys.executable, "scripts/generate_index.py"],
                  cwd=Path(__file__).parent.parent)

    # 构建报告 URL
    github_pages_url = config["reports"].get("github_pages_url",
                                           "https://yxw839841231.github.io/btc-momentum-service")

    # 推送消息
    logger.info(f"\n📤 开始推送消息...")
    logger.info(f"待推送币种数量: {len(all_results)}")
    logger.info(f"待推送币种: {', '.join([r['currency'] for r in all_results])}")

    # 推送到 Telegram
    if telegram_enabled and config["telegram"]["bot_token"]:
        logger.info("📱 推送到 Telegram...")
        telegram_bot = TelegramBot(
            bot_token=config["telegram"]["bot_token"],
            default_chat_id=config["telegram"].get("chat_id")
        )

        telegram_success = 0
        for result in all_results:
            currency = result["currency"]
            analysis_result = result["analysis_result"]
            report_filename = Path(result["report_path"]).name
            report_url = f"{github_pages_url}/reports/{report_filename}"

            logger.info(f"  正在推送 {currency} 到 Telegram...")
            send_result = telegram_bot.send_analysis_report(
                analysis_data=analysis_result,
                report_url=report_url,
                index_url=github_pages_url + "/"
            )

            if send_result.get("status") == "success":
                logger.info(f"  ✅ {currency} Telegram 推送成功")
                telegram_success += 1
            else:
                logger.warning(f"  ⚠️  {currency} Telegram 推送失败: {send_result.get('error')}")

        logger.info(f"📱 Telegram 推送完成: {telegram_success}/{len(all_results)} 成功")

        # 如果有告警，发送告警汇总
        if all_alerts:
            logger.info(f"  正在推送告警汇总到 Telegram...")
            alert_summary = alert_manager.format_alerts_summary(all_alerts)
            alert_message = f"🚨 **价格预警汇总**\n\n{alert_summary}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            alert_result = telegram_bot.send_message(text=alert_message)
            if alert_result.get("status") == "success":
                logger.info(f"  ✅ 告警汇总推送成功")
            else:
                logger.warning(f"  ⚠️  告警汇总推送失败")

    # 推送到飞书（使用合并消息）
    if feishu_enabled and config["feishu"]["webhook_url"]:
        logger.info("📱 推送到飞书（多币种合并消息）...")
        feishu_bot = FeishuBot(webhook_url=config["feishu"]["webhook_url"])

        # 使用合并消息格式，一次性发送所有币种
        logger.info(f"  合并 {len(all_results)} 个币种到一条消息...")
        send_result = feishu_bot.send_multi_currency_report(
            all_results=all_results,
            index_url=github_pages_url + "/",
            style="rich"  # 使用富文本卡片格式
        )

        if send_result.get("status") == "success":
            logger.info(f"  ✅ 飞书推送成功（合并 {len(all_results)} 个币种）")
        else:
            logger.error(f"  ❌ 飞书推送失败")
            logger.error(f"  错误详情: {send_result.get('error')}")

    logger.info("\n" + "="*60)
    logger.info(f"✅ 分析流程完成！共处理 {len(all_results)} 个币种")
    logger.info("="*60)

    return 0


def subprocess_run(cmd, cwd=None):
    """运行子进程"""
    import subprocess
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️  子进程执行失败: {e}")


if __name__ == "__main__":
    sys.exit(main())
