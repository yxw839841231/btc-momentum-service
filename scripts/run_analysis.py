#!/usr/bin/env python3
"""
主分析脚本
执行完整的 BTC 动能分析流程并推送到 Telegram
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
from src.price_fetcher import BTCPriceFetcher

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """加载配置"""
    # 这里简化处理，实际应该解析 config.yaml
    return {
        "telegram": {
            "bot_token": os.environ.get("TELEGRAM_BOT_TOKEN"),
            "chat_id": os.environ.get("TELEGRAM_CHAT_ID"),
            "enabled": bool(os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"))
        },
        "feishu": {
            "webhook_url": os.environ.get("FEISHU_WEBHOOK_URL"),
            "enabled": bool(os.environ.get("FEISHU_WEBHOOK_URL"))
        },
        "reports": {
            "output_dir": "reports"
        }
    }


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("BTC 动能分析服务启动")
    logger.info("=" * 60)

    # 加载配置
    config = load_config()

    # 检查是否至少配置了一个消息平台
    telegram_enabled = config["telegram"]["enabled"]
    feishu_enabled = config["feishu"]["enabled"]

    if not telegram_enabled and not feishu_enabled:
        logger.error("❌ 错误: 请至少配置一个消息推送平台")
        logger.error("")
        logger.error("Telegram 配置:")
        logger.error("  export TELEGRAM_BOT_TOKEN='your_bot_token'")
        logger.error("  export TELEGRAM_CHAT_ID='your_chat_id'")
        logger.error("")
        logger.error("飞书配置:")
        logger.error("  export FEISHU_WEBHOOK_URL='your_webhook_url'")
        return 1

    try:
        # 0. 获取 BTC 实时价格
        logger.info("💰 步骤 0: 获取 BTC 实时价格")
        price_fetcher = BTCPriceFetcher(exchange="okx")
        btc_price = price_fetcher.fetch_price()

        if btc_price and btc_price.get("price") != "N/A":
            logger.info(f"✅ BTC 价格: ${btc_price['price']} ({btc_price['change_24h_pct']:+.2f}%)")
        else:
            logger.warning("⚠️  价格获取失败，使用默认值")

        # 1. 初始化分析器
        logger.info("📊 步骤 1: 初始化分析器")
        analyzer = MomentumAnalyzer()

        # 2. 执行完整分析
        logger.info("📈 步骤 2: 执行动能分析")
        analysis_result = analyzer.run_full_analysis()

        if analysis_result["status"] != "success":
            logger.error(f"❌ 分析失败: {analysis_result}")
            return 1

        # 将价格信息添加到分析结果
        analysis_result["btc_price"] = btc_price

        # 3. 生成 HTML 报告
        logger.info("📄 步骤 3: 生成 HTML 报告")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"reports/btc_analysis_{timestamp}.html"

        generator = HTMLReportGenerator()
        report_path = generator.generate_html(analysis_result, report_file)
        logger.info(f"✅ 报告已生成: {report_path}")

        # 3.5 生成索引页面
        logger.info("📋 生成索引页面")
        import subprocess
        subprocess.run([sys.executable, "scripts/generate_index.py"],
                      cwd=Path(__file__).parent.parent)
        logger.info("✅ 索引页面已生成")

        # 4. 构建报告 URL
        # TODO: 实际部署后需要配置正确的 GitHub Pages URL
        report_filename = Path(report_path).name
        report_url = f"https://yxw839841231.github.io/btc-momentum-service/reports/{report_filename}"
        index_url = "https://yxw839841231.github.io/btc-momentum-service/"

        # 5. 推送到消息平台（Telegram 和/或 飞书）
        logger.info("📤 步骤 5: 推送到消息平台")

        # 检查哪些平台已启用
        telegram_enabled = config["telegram"]["enabled"]
        feishu_enabled = config["feishu"]["enabled"]

        if not telegram_enabled and not feishu_enabled:
            logger.warning("⚠️ 没有配置任何消息推送平台（Telegram 或 飞书）")

        # 推送到 Telegram
        if telegram_enabled:
            logger.info("📱 推送到 Telegram...")
            telegram_bot = TelegramBot(
                bot_token=config["telegram"]["bot_token"],
                default_chat_id=config["telegram"]["chat_id"]
            )

            send_result = telegram_bot.send_analysis_report(
                analysis_data=analysis_result,
                report_url=report_url,
                index_url=index_url
            )

            if send_result.get("status") == "success":
                logger.info("✅ Telegram 推送成功")
            else:
                logger.warning(f"⚠️ Telegram 推送失败: {send_result.get('error')}")

        # 推送到飞书
        if feishu_enabled:
            logger.info("📱 推送到飞书...")
            feishu_bot = FeishuBot(webhook_url=config["feishu"]["webhook_url"])

            send_result = feishu_bot.send_analysis_report(
                analysis_data=analysis_result,
                report_url=report_url,
                index_url=index_url
            )

            if send_result.get("status") == "success":
                logger.info("✅ 飞书推送成功")
            else:
                logger.warning(f"⚠️ 飞书推送失败: {send_result.get('error')}")

        logger.info("=" * 60)
        logger.info("✅ 分析流程完成！")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ 执行失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
