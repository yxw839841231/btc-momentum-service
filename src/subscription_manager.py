"""
订阅管理模块
管理用户订阅、时间级别、信号类型和币种偏好
"""

import sqlite3
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SubscriptionManager:
    """订阅管理器"""

    # 支持的时间级别
    VALID_TIMEFRAMES = {'2d', '1d', '12h', '6h', '4h', '2h', '1h', '30m'}

    # 支持的信号类型
    VALID_SIGNAL_TYPES = {'divergence', 'buy_signal', 'sell_signal', 'discrete_control'}

    # 支持的推送频率
    VALID_FREQUENCIES = {'all', 'alerts', 'daily', 'none'}

    def __init__(self, db_path: str = "data/subscriptions.db"):
        """
        初始化订阅管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_exists()
        logger.info(f"订阅管理器初始化完成: {db_path}")

    def _ensure_db_exists(self):
        """确保数据库和表结构存在"""
        # 确保目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建订阅表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                currencies TEXT DEFAULT 'btc',
                timeframes TEXT,
                signal_types TEXT,
                frequency TEXT DEFAULT 'all',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, chat_id, platform)
            )
        """)

        # 创建告警历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_hash TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                currency TEXT DEFAULT 'btc',
                content TEXT,
                first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sent TIMESTAMP,
                UNIQUE(signal_hash)
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_subscriptions_user
            ON subscriptions(user_id, chat_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_history_type
            ON alerts_history(signal_type, timeframe, currency)
        """)

        # 创建支持的币种表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supported_currencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                exchange_symbol TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                priority INTEGER DEFAULT 0
            )
        """)

        # 插入默认币种
        default_currencies = [
            ('BTC', 'Bitcoin', 'BTC-USDT', 1, 0),
            ('ETH', 'Ethereum', 'ETH-USDT', 1, 1),
            ('SOL', 'Solana', 'SOL-USDT', 1, 2),
            ('BNB', 'Binance Coin', 'BNB-USDT', 1, 3),
            ('XRP', 'Ripple', 'XRP-USDT', 1, 4),
            ('ADA', 'Cardano', 'ADA-USDT', 1, 5),
            ('DOGE', 'Dogecoin', 'DOGE-USDT', 1, 6),
            ('DOT', 'Polkadot', 'DOT-USDT', 1, 7),
            ('MATIC', 'Polygon', 'MATIC-USDT', 1, 8),
            ('AVAX', 'Avalanche', 'AVAX-USDT', 1, 9),
        ]

        for symbol, name, exchange_symbol, enabled, priority in default_currencies:
            cursor.execute("""
                INSERT OR IGNORE INTO supported_currencies
                (symbol, name, exchange_symbol, enabled, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (symbol, name, exchange_symbol, enabled, priority))

        conn.commit()
        conn.close()

    def _parse_list(self, text: Optional[str]) -> List[str]:
        """解析逗号分隔的字符串为列表"""
        if not text:
            return []
        return [item.strip() for item in text.split(',') if item.strip()]

    def _format_list(self, items: List[str]) -> str:
        """将列表格式化为逗号分隔的字符串"""
        return ','.join(items) if items else ''

    # ==================== 订阅管理 ====================

    def get_or_create_subscription(
        self,
        user_id: int,
        chat_id: str,
        platform: str
    ) -> Dict:
        """
        获取或创建用户订阅

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台 (telegram/feishu)

        Returns:
            订阅信息字典
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, user_id, chat_id, platform, currencies, timeframes,
                   signal_types, frequency, created_at, updated_at
            FROM subscriptions
            WHERE user_id = ? AND chat_id = ? AND platform = ?
        """, (user_id, str(chat_id), platform))

        row = cursor.fetchone()

        if row:
            subscription = {
                'id': row[0],
                'user_id': row[1],
                'chat_id': row[2],
                'platform': row[3],
                'currencies': self._parse_list(row[4]),
                'timeframes': self._parse_list(row[5]),
                'signal_types': self._parse_list(row[6]),
                'frequency': row[7],
                'created_at': row[8],
                'updated_at': row[9]
            }
        else:
            # 创建新订阅
            cursor.execute("""
                INSERT INTO subscriptions
                (user_id, chat_id, platform, currencies, frequency)
                VALUES (?, ?, ?, 'btc', 'all')
            """, (user_id, str(chat_id), platform))

            conn.commit()

            subscription = {
                'id': cursor.lastrowid,
                'user_id': user_id,
                'chat_id': str(chat_id),
                'platform': platform,
                'currencies': ['btc'],
                'timeframes': [],
                'signal_types': [],
                'frequency': 'all',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            logger.info(f"创建新订阅: user_id={user_id}, platform={platform}")

        conn.close()
        return subscription

    def subscribe_timeframes(
        self,
        user_id: int,
        chat_id: str,
        platform: str,
        timeframes: List[str]
    ) -> Dict:
        """
        订阅时间级别

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台
            timeframes: 时间级别列表

        Returns:
            更新后的订阅
        """
        # 验证时间级别
        valid_timeframes = [tf for tf in timeframes if tf in self.VALID_TIMEFRAMES]

        if not valid_timeframes:
            return {
                'status': 'error',
                'error': f'无效的时间级别。支持: {", ".join(sorted(self.VALID_TIMEFRAMES))}'
            }

        # 获取当前订阅
        subscription = self.get_or_create_subscription(user_id, chat_id, platform)

        # 合并时间级别（去重）
        current_timeframes = set(subscription['timeframes'])
        current_timeframes.update(valid_timeframes)

        # 更新数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE subscriptions
            SET timeframes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND chat_id = ? AND platform = ?
        """, (self._format_list(list(current_timeframes)), user_id, str(chat_id), platform))

        conn.commit()
        conn.close()

        logger.info(f"用户 {user_id} 订阅时间级别: {valid_timeframes}")

        return {
            'status': 'success',
            'timeframes': list(current_timeframes),
            'added': valid_timeframes
        }

    def unsubscribe_timeframes(
        self,
        user_id: int,
        chat_id: str,
        platform: str,
        timeframes: List[str]
    ) -> Dict:
        """
        取消订阅时间级别

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台
            timeframes: 时间级别列表

        Returns:
            更新后的订阅
        """
        subscription = self.get_or_create_subscription(user_id, chat_id, platform)

        # 移除指定时间级别
        current_timeframes = set(subscription['timeframes'])
        removed = [tf for tf in timeframes if tf in current_timeframes]
        current_timeframes.difference_update(timeframes)

        # 更新数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE subscriptions
            SET timeframes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND chat_id = ? AND platform = ?
        """, (self._format_list(list(current_timeframes)), user_id, str(chat_id), platform))

        conn.commit()
        conn.close()

        logger.info(f"用户 {user_id} 取消订阅时间级别: {removed}")

        return {
            'status': 'success',
            'timeframes': list(current_timeframes),
            'removed': removed
        }

    def subscribe_signals(
        self,
        user_id: int,
        chat_id: str,
        platform: str,
        signals: List[str]
    ) -> Dict:
        """
        订阅信号类型

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台
            signals: 信号类型列表

        Returns:
            更新后的订阅
        """
        # 验证信号类型
        valid_signals = [s for s in signals if s in self.VALID_SIGNAL_TYPES]

        if not valid_signals:
            return {
                'status': 'error',
                'error': f'无效的信号类型。支持: {", ".join(sorted(self.VALID_SIGNAL_TYPES))}'
            }

        # 获取当前订阅
        subscription = self.get_or_create_subscription(user_id, chat_id, platform)

        # 合并信号类型（去重）
        current_signals = set(subscription['signal_types'])
        current_signals.update(valid_signals)

        # 更新数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE subscriptions
            SET signal_types = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND chat_id = ? AND platform = ?
        """, (self._format_list(list(current_signals)), user_id, str(chat_id), platform))

        conn.commit()
        conn.close()

        logger.info(f"用户 {user_id} 订阅信号类型: {valid_signals}")

        return {
            'status': 'success',
            'signal_types': list(current_signals),
            'added': valid_signals
        }

    def unsubscribe_signals(
        self,
        user_id: int,
        chat_id: str,
        platform: str,
        signals: List[str]
    ) -> Dict:
        """
        取消订阅信号类型

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台
            signals: 信号类型列表

        Returns:
            更新后的订阅
        """
        subscription = self.get_or_create_subscription(user_id, chat_id, platform)

        # 移除指定信号类型
        current_signals = set(subscription['signal_types'])
        removed = [s for s in signals if s in current_signals]
        current_signals.difference_update(signals)

        # 更新数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE subscriptions
            SET signal_types = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND chat_id = ? AND platform = ?
        """, (self._format_list(list(current_signals)), user_id, str(chat_id), platform))

        conn.commit()
        conn.close()

        logger.info(f"用户 {user_id} 取消订阅信号类型: {removed}")

        return {
            'status': 'success',
            'signal_types': list(current_signals),
            'removed': removed
        }

    def subscribe_currencies(
        self,
        user_id: int,
        chat_id: str,
        platform: str,
        currencies: List[str]
    ) -> Dict:
        """
        订阅币种

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台
            currencies: 币种列表

        Returns:
            更新后的订阅
        """
        # 验证币种
        valid_currencies = self._get_valid_currencies(currencies)

        if not valid_currencies:
            return {
                'status': 'error',
                'error': f'无效的币种。支持: {", ".join(self._get_all_supported_currencies()["symbols"])}'
            }

        # 获取当前订阅
        subscription = self.get_or_create_subscription(user_id, chat_id, platform)

        # 合并币种（去重）
        current_currencies = set(subscription['currencies'])
        current_currencies.update(valid_currencies)

        # 更新数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE subscriptions
            SET currencies = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND chat_id = ? AND platform = ?
        """, (self._format_list(list(current_currencies)), user_id, str(chat_id), platform))

        conn.commit()
        conn.close()

        logger.info(f"用户 {user_id} 订阅币种: {valid_currencies}")

        return {
            'status': 'success',
            'currencies': list(current_currencies),
            'added': valid_currencies
        }

    def unsubscribe_currencies(
        self,
        user_id: int,
        chat_id: str,
        platform: str,
        currencies: List[str]
    ) -> Dict:
        """
        取消订阅币种

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台
            currencies: 币种列表

        Returns:
            更新后的订阅
        """
        subscription = self.get_or_create_subscription(user_id, chat_id, platform)

        # 移除指定币种
        current_currencies = set(subscription['currencies'])
        removed = [c for c in currencies if c in current_currencies]
        current_currencies.difference_update(currencies)

        # 确保至少订阅一个币种
        if not current_currencies:
            current_currencies = {'btc'}

        # 更新数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE subscriptions
            SET currencies = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND chat_id = ? AND platform = ?
        """, (self._format_list(list(current_currencies)), user_id, str(chat_id), platform))

        conn.commit()
        conn.close()

        logger.info(f"用户 {user_id} 取消订阅币种: {removed}")

        return {
            'status': 'success',
            'currencies': list(current_currencies),
            'removed': removed
        }

    def set_frequency(
        self,
        user_id: int,
        chat_id: str,
        platform: str,
        frequency: str
    ) -> Dict:
        """
        设置推送频率

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台
            frequency: 推送频率

        Returns:
            更新后的订阅
        """
        if frequency not in self.VALID_FREQUENCIES:
            return {
                'status': 'error',
                'error': f'无效的频率。支持: {", ".join(self.VALID_FREQUENCIES)}'
            }

        # 获取当前订阅
        subscription = self.get_or_create_subscription(user_id, chat_id, platform)

        # 更新数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE subscriptions
            SET frequency = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND chat_id = ? AND platform = ?
        """, (frequency, user_id, str(chat_id), platform))

        conn.commit()
        conn.close()

        logger.info(f"用户 {user_id} 设置推送频率: {frequency}")

        return {
            'status': 'success',
            'frequency': frequency
        }

    # ==================== 查询功能 ====================

    def get_all_subscribers(self, platform: str) -> List[Dict]:
        """
        获取平台所有订阅者

        Args:
            platform: 平台 (telegram/feishu)

        Returns:
            订阅者列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, chat_id, currencies, timeframes, signal_types, frequency
            FROM subscriptions
            WHERE platform = ?
        """, (platform,))

        rows = cursor.fetchall()
        subscribers = []

        for row in rows:
            subscribers.append({
                'user_id': row[0],
                'chat_id': row[1],
                'currencies': self._parse_list(row[2]),
                'timeframes': self._parse_list(row[3]),
                'signal_types': self._parse_list(row[4]),
                'frequency': row[5]
            })

        conn.close()
        return subscribers

    def get_subscribers_for_currency(
        self,
        currency: str,
        platform: str
    ) -> List[Dict]:
        """
        获取订阅指定币种的用户

        Args:
            currency: 币种
            platform: 平台

        Returns:
            订阅者列表
        """
        all_subscribers = self.get_all_subscribers(platform)
        return [
            sub for sub in all_subscribers
            if currency.upper() in [c.upper() for c in sub['currencies']]
        ]

    def get_subscribers_for_timeframe(
        self,
        timeframe: str,
        platform: str
    ) -> List[Dict]:
        """
        获取订阅指定时间级别的用户

        Args:
            timeframe: 时间级别
            platform: 平台

        Returns:
            订阅者列表
        """
        all_subscribers = self.get_all_subscribers(platform)

        # 如果用户没有设置时间级别，默认接收所有
        return [
            sub for sub in all_subscribers
            if not sub['timeframes'] or timeframe in sub['timeframes']
        ]

    def get_subscribers_for_signal(
        self,
        signal_type: str,
        platform: str
    ) -> List[Dict]:
        """
        获取订阅指定信号类型的用户

        Args:
            signal_type: 信号类型
            platform: 平台

        Returns:
            订阅者列表
        """
        all_subscribers = self.get_all_subscribers(platform)

        # 如果用户没有设置信号类型，默认接收所有
        return [
            sub for sub in all_subscribers
            if not sub['signal_types'] or signal_type in sub['signal_types']
        ]

    # ==================== 告警历史 ====================

    def record_alert_sent(
        self,
        signal_hash: str,
        signal_type: str,
        timeframe: str,
        currency: str = 'btc',
        content: str = ''
    ) -> bool:
        """
        记录告警已发送

        Args:
            signal_hash: 信号唯一标识
            signal_type: 信号类型
            timeframe: 时间级别
            currency: 币种
            content: 信号内容

        Returns:
            是否成功
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO alerts_history (signal_hash, signal_type, timeframe, currency, content, last_sent)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(signal_hash) DO UPDATE SET
                    last_sent = CURRENT_TIMESTAMP,
                    content = excluded.content
            """, (signal_hash, signal_type, timeframe, currency, content))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"记录告警失败: {e}")
            conn.close()
            return False

    def is_alert_sent_recently(
        self,
        signal_hash: str,
        hours: int = 12
    ) -> bool:
        """
        检查告警是否最近已发送

        Args:
            signal_hash: 信号唯一标识
            hours: 小时数

        Returns:
            是否最近已发送
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        cursor.execute("""
            SELECT last_sent FROM alerts_history
            WHERE signal_hash = ? AND last_sent > ?
        """, (signal_hash, cutoff_time))

        row = cursor.fetchone()
        conn.close()

        return row is not None

    # ==================== 币种管理 ====================

    def _get_valid_currencies(self, currencies: List[str]) -> List[str]:
        """获取有效的币种列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        valid_currencies = []
        for currency in currencies:
            cursor.execute("""
                SELECT symbol FROM supported_currencies
                WHERE UPPER(symbol) = ? AND enabled = 1
            """, (currency.upper(),))

            if cursor.fetchone():
                valid_currencies.append(currency.upper())

        conn.close()
        return valid_currencies

    def _get_all_supported_currencies(self) -> Dict:
        """获取所有支持的币种"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT symbol, name FROM supported_currencies
            WHERE enabled = 1
            ORDER BY priority
        """)

        rows = cursor.fetchall()
        currencies = {
            'symbols': [row[0] for row in rows],
            'names': {row[0]: row[1] for row in rows}
        }

        conn.close()
        return currencies


class AlertFilter:
    """告警过滤器"""

    def __init__(self, subscription_manager: SubscriptionManager):
        """
        初始化过滤器

        Args:
            subscription_manager: 订阅管理器实例
        """
        self.subscription_manager = subscription_manager

    def should_send_report(
        self,
        user_id: int,
        chat_id: str,
        platform: str,
        currency: str,
        timeframe: str
    ) -> bool:
        """
        检查是否应该发送报告

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台
            currency: 币种
            timeframe: 时间级别

        Returns:
            是否应该发送
        """
        # 获取用户订阅
        subscription = self.subscription_manager.get_or_create_subscription(
            user_id, chat_id, platform
        )

        # 检查频率设置
        frequency = subscription.get('frequency', 'all')

        # none = 暂停所有推送
        if frequency == 'none':
            return False

        # alerts = 仅推送告警，不推送常规报告
        if frequency == 'alerts':
            return False

        # 检查币种订阅
        currencies = subscription.get('currencies', ['btc'])
        if currency.upper() not in [c.upper() for c in currencies]:
            return False

        # 检查时间级别订阅
        timeframes = subscription.get('timeframes', [])
        if timeframes and timeframe not in timeframes:
            return False

        return True

    def should_send_alert(
        self,
        user_id: int,
        chat_id: str,
        platform: str,
        signal_type: str,
        timeframe: str,
        currency: str = 'btc'
    ) -> bool:
        """
        检查是否应该发送告警

        Args:
            user_id: 用户 ID
            chat_id: 聊天 ID
            platform: 平台
            signal_type: 信号类型
            timeframe: 时间级别
            currency: 币种

        Returns:
            是否应该发送
        """
        # 获取用户订阅
        subscription = self.subscription_manager.get_or_create_subscription(
            user_id, chat_id, platform
        )

        # 检查频率设置
        frequency = subscription.get('frequency', 'all')

        # none = 暂停所有推送
        if frequency == 'none':
            return False

        # daily = 每日摘要，不推送实时告警
        if frequency == 'daily':
            return False

        # 检查币种订阅
        currencies = subscription.get('currencies', ['btc'])
        if currency.upper() not in [c.upper() for c in currencies]:
            return False

        # 检查时间级别订阅
        timeframes = subscription.get('timeframes', [])
        if timeframes and timeframe not in timeframes:
            return False

        # 检查信号类型订阅
        signal_types = subscription.get('signal_types', [])
        if signal_types and signal_type not in signal_types:
            return False

        return True

    def generate_signal_hash(
        self,
        signal_type: str,
        timeframe: str,
        currency: str,
        additional_data: str = ''
    ) -> str:
        """
        生成信号唯一标识

        Args:
            signal_type: 信号类型
            timeframe: 时间级别
            currency: 币种
            additional_data: 额外数据

        Returns:
            信号哈希
        """
        import hashlib

        data = f"{signal_type}:{timeframe}:{currency}:{additional_data}"
        return hashlib.md5(data.encode()).hexdigest()


if __name__ == "__main__":
    # 测试代码
    manager = SubscriptionManager("data/test_subscriptions.db")

    # 测试创建订阅
    print("=== 测试创建订阅 ===")
    subscription = manager.get_or_create_subscription(
        user_id=123456,
        chat_id="123456",
        platform="telegram"
    )
    print(json.dumps(subscription, indent=2, ensure_ascii=False))

    # 测试订阅时间级别
    print("\n=== 测试订阅时间级别 ===")
    result = manager.subscribe_timeframes(
        user_id=123456,
        chat_id="123456",
        platform="telegram",
        timeframes=["1d", "4h", "1h"]
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 测试订阅币种
    print("\n=== 测试订阅币种 ===")
    result = manager.subscribe_currencies(
        user_id=123456,
        chat_id="123456",
        platform="telegram",
        currencies=["btc", "eth", "sol"]
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 测试设置频率
    print("\n=== 测试设置频率 ===")
    result = manager.set_frequency(
        user_id=123456,
        chat_id="123456",
        platform="telegram",
        frequency="alerts"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 测试查询订阅者
    print("\n=== 测试查询订阅者 ===")
    subscribers = manager.get_all_subscribers("telegram")
    print(f"Telegram 订阅者数量: {len(subscribers)}")
    print(json.dumps(subscribers, indent=2, ensure_ascii=False))
