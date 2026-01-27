#!/usr/bin/env python3
"""
主分析脚本
执行完整的 BTC 动能分析流程并推送到 Telegram
支持订阅管理和多币种分析
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
from src.price_fetcher import PriceFetcher
from src.subscription_manager import SubscriptionManager
from src.currency_config import CurrencyConfig

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
        },
        "analysis": {
            "currency": os.environ.get("ANALYSIS_CURRENCY", "BTC"),  # 默认分析 BTC
            "timeframe": os.environ.get("ANALYSIS_TIMEFRAME", "1d")  # 默认1日线
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
        # 0. 获取币种实时价格
        currency = config["analysis"]["currency"].upper()
        timeframe = config["analysis"]["timeframe"]
        logger.info(f"💰 步骤 0: 获取 {currency} 实时价格")
        price_fetcher = PriceFetcher(exchange="okx")
        currency_price = price_fetcher.fetch_price(currency)

        if currency_price and currency_price.get("price") != "N/A":
            logger.info(f"✅ {currency} 价格: ${currency_price['price']} ({currency_price['change_24h_pct']:+.2f}%)")
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
        analysis_result["currency"] = currency
        analysis_result["currency_price"] = currency_price

        # 3. 生成 HTML 报告
        logger.info("📄 步骤 3: 生成 HTML 报告")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"reports/{currency.lower()}_analysis_{timestamp}.html"

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

        # 5. 推送到消息平台（基于订阅）
        logger.info("📤 步骤 5: 推送到消息平台（基于订阅）")

        # 初始化订阅管理器
        subscription_manager = SubscriptionManager()

        # 检查哪些平台已启用
        telegram_enabled = config["telegram"]["enabled"]
        feishu_enabled = config["feishu"]["enabled"]

        if not telegram_enabled and not feishu_enabled:
            logger.warning("⚠️ 没有配置任何消息推送平台（Telegram 或 飞书）")
        else:
            # 获取需要推送的用户列表
            telegram_sent_count = 0
            feishu_sent_count = 0

            # 推送到 Telegram
            if telegram_enabled:
                logger.info("📱 推送到 Telegram...")
                telegram_bot = TelegramBot(
                    bot_token=config["telegram"]["bot_token"],
                    default_chat_id=config["telegram"]["chat_id"]
                )

                # 获取所有 Telegram 订阅者
                subscribers = subscription_manager.get_all_subscribers('telegram')
                logger.info(f"  Telegram 订阅者数量: {len(subscribers)}")

                for subscriber in subscribers:
                    user_id = subscriber['user_id']
                    chat_id = subscriber['chat_id']

                    # 检查是否应该发送
                    if telegram_bot.should_send_report(user_id, chat_id, currency, timeframe):
                        send_result = telegram_bot.send_analysis_report(
                            analysis_data=analysis_result,
                            report_url=report_url,
                            index_url=index_url,
                            chat_id=chat_id
                        )

                        if send_result.get("status") == "success":
                            telegram_sent_count += 1
                            logger.info(f"  ✅ 推送成功: chat_id={chat_id}")
                        else:
                            logger.warning(f"  ⚠️ 推送失败: chat_id={chat_id}, error={send_result.get('error')}")
                    else:
                        logger.info(f"  ⏭️  跳过: chat_id={chat_id} (未订阅或过滤设置)")

                logger.info(f"  Telegram 推送完成: {telegram_sent_count}/{len(subscribers)}")

            # 推送到飞书
            if feishu_enabled:
                logger.info("📱 推送到飞书...")
                feishu_bot = FeishuBot(webhook_url=config["feishu"]["webhook_url"])

                # 飞书使用 webhook，推送到默认地址
                # 注意：飞书机器人使用单一 webhook，无法像 Telegram 那样定向推送给不同用户
                # 这里我们检查是否有任何订阅者需要接收报告
                subscribers = subscription_manager.get_all_subscribers('feishu')

                # 检查是否至少有一个订阅者需要接收
                should_send = any(
                    feishu_bot.should_send_report(sub['user_id'], sub['chat_id'], currency, timeframe)
                    for sub in subscribers
                )

                if should_send or len(subscribers) == 0:  # 如果没有订阅者，默认推送（向后兼容）
                    send_result = feishu_bot.send_analysis_report(
                        analysis_data=analysis_result,
                        report_url=report_url,
                        index_url=index_url
                    )

                    if send_result.get("status") == "success":
                        feishu_sent_count = 1
                        logger.info("  ✅ 飞书推送成功")
                    else:
                        logger.warning(f"  ⚠️ 飞书推送失败: {send_result.get('error')}")
                else:
                    logger.info("  ⏭️  飞书推送跳过（无订阅者需要接收）")

            logger.info(f"📊 推送统计: Telegram {telegram_sent_count}, 飞书 {feishu_sent_count}")

        logger.info("=" * 60)
        logger.info("✅ 分析流程完成！")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ 执行失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
