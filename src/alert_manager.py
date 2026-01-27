"""
价格预警管理器
监控价格变化并触发告警
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertType(Enum):
    """告警类型"""
    LARGE_MOVE = "large_move"           # 大幅波动
    PRICE_TARGET = "price_target"       # 价格目标
    DIVERGENCE = "divergence"           # 技术指标背离
    GOLDEN_CROSS = "golden_cross"       # 金叉
    DEATH_CROSS = "death_cross"         # 死叉


class AlertSeverity(Enum):
    """告警严重程度"""
    LOW = "low"                         # 低
    MEDIUM = "medium"                   # 中
    HIGH = "high"                       # 高
    CRITICAL = "critical"               # 紧急


class PriceAlert:
    """价格告警"""

    def __init__(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        currency: str,
        message: str,
        metadata: Optional[Dict] = None
    ):
        self.alert_type = alert_type
        self.severity = severity
        self.currency = currency
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "currency": self.currency,
            "message": self.message,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

    def format_message(self) -> str:
        """格式化告警消息"""
        severity_icons = {
            AlertSeverity.LOW: "🔵",
            AlertSeverity.MEDIUM: "🟡",
            AlertSeverity.HIGH: "🟠",
            AlertSeverity.CRITICAL: "🔴"
        }

        icon = severity_icons.get(self.severity, "⚪")
        return f"{icon} **{self.currency}** {self.message}"


class AlertManager:
    """告警管理器"""

    def __init__(self):
        """初始化告警管理器"""
        self.alert_history = {}  # 告警历史，避免重复告警
        self.alert_cooldown = {}  # 告警冷却时间
        self.default_cooldown_minutes = 60  # 默认冷却时间：60分钟

        # 配置
        self.config = {
            "large_move_threshold": 5.0,     # 大幅波动阈值：±5%
            "price_targets": {               # 价格目标（示例）
                "BTC": {"high": 100000, "low": 90000}
            }
        }

        logger.info("告警管理器初始化完成")

    def check_price_alerts(self, currency: str, price_data: Dict) -> List[PriceAlert]:
        """
        检查价格告警

        Args:
            currency: 币种
            price_data: 价格数据

        Returns:
            告警列表
        """
        alerts = []

        try:
            # 1. 检查大幅波动告警
            large_move_alert = self._check_large_move(currency, price_data)
            if large_move_alert:
                alerts.append(large_move_alert)

            # 2. 检查价格目标告警
            target_alert = self._check_price_target(currency, price_data)
            if target_alert:
                alerts.append(target_alert)

            # 3. 可以添加更多告警类型...

            return alerts

        except Exception as e:
            logger.error(f"检查 {currency} 告警时出错: {e}")
            return []

    def _check_large_move(self, currency: str, price_data: Dict) -> Optional[PriceAlert]:
        """检查大幅波动告警"""
        try:
            change_24h_pct = price_data.get("change_24h_pct", 0)
            threshold = self.config.get("large_move_threshold", 5.0)

            if abs(change_24h_pct) >= threshold:
                # 检查冷却时间
                alert_key = f"{currency}_large_move"
                if self._is_in_cooldown(alert_key):
                    return None

                direction = "暴涨" if change_24h_pct > 0 else "暴跌"
                severity = AlertSeverity.HIGH if abs(change_24h_pct) >= 10 else AlertSeverity.MEDIUM

                alert = PriceAlert(
                    alert_type=AlertType.LARGE_MOVE,
                    severity=severity,
                    currency=currency,
                    message=f"24h{direction} {abs(change_24h_pct):.2f}%",
                    metadata={
                        "change_24h_pct": change_24h_pct,
                        "current_price": price_data.get("price")
                    }
                )

                # 记录告警
                self._record_alert(alert_key)

                return alert

        except Exception as e:
            logger.error(f"检查大幅波动告警失败: {e}")

        return None

    def _check_price_target(self, currency: str, price_data: Dict) -> Optional[PriceAlert]:
        """检查价格目标告警"""
        try:
            price_raw = price_data.get("price_raw", 0)
            if price_raw == 0:
                return None

            targets = self.config.get("price_targets", {}).get(currency)
            if not targets:
                return None

            alerts = []

            # 检查上限目标
            if "high" in targets and price_raw >= targets["high"]:
                alert_key = f"{currency}_price_high"
                if not self._is_in_cooldown(alert_key):
                    alerts.append(PriceAlert(
                        alert_type=AlertType.PRICE_TARGET,
                        severity=AlertSeverity.MEDIUM,
                        currency=currency,
                        message=f"突破价格目标 ${targets['high']:,.0f}",
                        metadata={"target": targets["high"], "current": price_raw}
                    ))
                    self._record_alert(alert_key)

            # 检查下限目标
            if "low" in targets and price_raw <= targets["low"]:
                alert_key = f"{currency}_price_low"
                if not self._is_in_cooldown(alert_key):
                    alerts.append(PriceAlert(
                        alert_type=AlertType.PRICE_TARGET,
                        severity=AlertSeverity.MEDIUM,
                        currency=currency,
                        message=f"跌破价格目标 ${targets['low']:,.0f}",
                        metadata={"target": targets["low"], "current": price_raw}
                    ))
                    self._record_alert(alert_key)

            return alerts[0] if alerts else None

        except Exception as e:
            logger.error(f"检查价格目标告警失败: {e}")

        return None

    def check_indicator_alerts(self, currency: str, analysis_result: Dict) -> List[PriceAlert]:
        """
        检查技术指标告警

        Args:
            currency: 币种
            analysis_result: 分析结果

        Returns:
            告警列表
        """
        alerts = []

        try:
            # 这里可以添加各种技术指标告警
            # 例如：金叉/死叉、背离等

            # 示例：检查是否有重要信号
            # signals = analysis_result.get("signals", [])
            # for signal in signals:
            #     if signal["type"] == "bullish_divergence":
            #         alerts.append(...)

            return alerts

        except Exception as e:
            logger.error(f"检查 {currency} 技术指标告警时出错: {e}")
            return []

    def _is_in_cooldown(self, alert_key: str) -> bool:
        """检查告警是否在冷却期内"""
        if alert_key not in self.alert_cooldown:
            return False

        last_alert_time = self.alert_cooldown[alert_key]
        cooldown_time = timedelta(minutes=self.default_cooldown_minutes)

        return datetime.now() - last_alert_time < cooldown_time

    def _record_alert(self, alert_key: str):
        """记录告警时间"""
        self.alert_cooldown[alert_key] = datetime.now()

    def set_price_target(self, currency: str, high: Optional[float] = None, low: Optional[float] = None):
        """
        设置价格目标

        Args:
            currency: 币种
            high: 上限目标
            low: 下限目标
        """
        if currency not in self.config["price_targets"]:
            self.config["price_targets"][currency] = {}

        if high is not None:
            self.config["price_targets"][currency]["high"] = high
            logger.info(f"设置 {currency} 上限目标: ${high:,.0f}")

        if low is not None:
            self.config["price_targets"][currency]["low"] = low
            logger.info(f"设置 {currency} 下限目标: ${low:,.0f}")

    def format_alerts_summary(self, all_alerts: List[PriceAlert]) -> str:
        """格式化告警汇总"""
        if not all_alerts:
            return ""

        lines = ["\n**🚨 价格预警**\n"]

        # 按严重程度分组
        by_severity = {
            AlertSeverity.CRITICAL: [],
            AlertSeverity.HIGH: [],
            AlertSeverity.MEDIUM: [],
            AlertSeverity.LOW: []
        }

        for alert in all_alerts:
            by_severity[alert.severity].append(alert)

        # 从高到低显示
        for severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH, AlertSeverity.MEDIUM, AlertSeverity.LOW]:
            alerts = by_severity[severity]
            if alerts:
                for alert in alerts:
                    lines.append(f"• {alert.format_message()}")

        return "\n".join(lines)


# 便捷函数
def check_all_alerts(currency: str, price_data: Dict, analysis_result: Dict) -> List[PriceAlert]:
    """
    检查所有告警（便捷函数）

    Args:
        currency: 币种
        price_data: 价格数据
        analysis_result: 分析结果

    Returns:
        所有告警列表
    """
    manager = AlertManager()
    alerts = []

    # 检查价格告警
    price_alerts = manager.check_price_alerts(currency, price_data)
    alerts.extend(price_alerts)

    # 检查技术指标告警
    indicator_alerts = manager.check_indicator_alerts(currency, analysis_result)
    alerts.extend(indicator_alerts)

    return alerts


if __name__ == "__main__":
    # 测试代码
    manager = AlertManager()

    # 设置价格目标
    manager.set_price_target("BTC", high=100000, low=90000)

    # 测试大幅波动告警
    test_price_data = {
        "price": "$98,000.00",
        "price_raw": 98000.0,
        "change_24h_pct": 6.5,  # 6.5% 涨跌
        "exchange": "OKX"
    }

    alerts = manager.check_price_alerts("BTC", test_price_data)

    if alerts:
        print("检测到告警:")
        for alert in alerts:
            print(f"  - {alert.format_message()}")
            print(f"    详情: {alert.to_dict()}")
    else:
        print("没有检测到告警")
