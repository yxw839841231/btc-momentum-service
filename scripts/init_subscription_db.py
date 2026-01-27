#!/usr/bin/env python3
"""
初始化订阅数据库脚本
创建订阅管理所需的数据库和表结构
"""

import sys
import logging
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.subscription_manager import SubscriptionManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("初始化订阅数据库")
    logger.info("=" * 60)

    # 默认数据库路径
    db_path = "data/subscriptions.db"

    # 如果提供了命令行参数，使用自定义路径
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    logger.info(f"数据库路径: {db_path}")

    try:
        # 创建订阅管理器（会自动初始化数据库）
        manager = SubscriptionManager(db_path=db_path)

        logger.info("✅ 数据库初始化成功")

        # 显示支持的币种
        currencies = manager._get_all_supported_currencies()
        logger.info(f"\n支持的币种 ({len(currencies['symbols'])} 个):")
        for symbol in currencies['symbols']:
            logger.info(f"  • {symbol}: {currencies['names'][symbol]}")

        # 显示支持的配置
        logger.info(f"\n支持的时间级别:")
        logger.info(f"  {', '.join(sorted(manager.VALID_TIMEFRAMES))}")

        logger.info(f"\n支持的信号类型:")
        logger.info(f"  {', '.join(sorted(manager.VALID_SIGNAL_TYPES))}")

        logger.info(f"\n支持的推送频率:")
        logger.info(f"  {', '.join(sorted(manager.VALID_FREQUENCIES))}")

        logger.info("\n" + "=" * 60)
        logger.info("✅ 数据库初始化完成")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
