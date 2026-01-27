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
from src.report_generator import HTMLReportGenerator

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
            "chat_id": os.environ.get("TELEGRAM_CHAT_ID")
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

    # 检查环境变量
    bot_token = config["telegram"]["bot_token"]
    chat_id = config["telegram"]["chat_id"]

    if not bot_token or not chat_id:
        logger.error("❌ 错误: 请设置环境变量 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")
        return 1

    try:
        # 1. 初始化分析器
        logger.info("📊 步骤 1: 初始化分析器")
        analyzer = MomentumAnalyzer()

        # 2. 执行完整分析
        logger.info("📈 步骤 2: 执行动能分析")
        analysis_result = analyzer.run_full_analysis()

        if analysis_result["status"] != "success":
            logger.error(f"❌ 分析失败: {analysis_result}")
            return 1

        # 3. 生成 HTML 报告
        logger.info("📄 步骤 3: 生成 HTML 报告")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"reports/btc_analysis_{timestamp}.html"

        generator = HTMLReportGenerator()
        report_path = generator.generate_html(analysis_result, report_file)
        logger.info(f"✅ 报告已生成: {report_path}")

        # 4. 构建报告 URL
        # TODO: 实际部署后需要配置正确的 GitHub Pages URL
        report_filename = Path(report_path).name
        report_url = f"https://yxw839841231.github.io/btc-momentum-service/reports/{report_filename}"

        # 5. 推送到 Telegram
        logger.info("📤 步骤 4: 推送到 Telegram")
        bot = TelegramBot(bot_token=bot_token, default_chat_id=chat_id)

        # 直接尝试发送消息（不预先测试连接，避免超时问题）
        send_result = bot.send_analysis_report(
            analysis_data=analysis_result,
            report_url=report_url
        )

        if send_result.get("status") == "success":
            logger.info("✅ Telegram 推送成功")
        else:
            logger.warning(f"⚠️ Telegram 推送失败，但报告已生成: {send_result.get('error')}")
            logger.warning("报告链接: " + report_url)
            # 不要返回错误，因为报告已经成功生成

        logger.info("=" * 60)
        logger.info("✅ 分析流程完成！")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ 执行失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
