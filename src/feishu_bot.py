"""
飞书机器人模块
处理飞书消息和推送
"""

import logging
from typing import Optional, Dict, List
import requests
import json as json_module

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeishuBot:
    """飞书机器人客户端"""

    def __init__(self, webhook_url: str):
        """
        初始化飞书机器人

        Args:
            webhook_url: 飞书机器人 Webhook URL
        """
        self.webhook_url = webhook_url
        logger.info(f"飞书机器人初始化成功")

    def send_text(self, content: str) -> dict:
        """
        发送纯文本消息

        Args:
            content: 消息内容

        Returns:
            API 响应
        """
        data = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }

        return self._send_request(data)

    def send_post(self, title: str, content: List[Dict]) -> dict:
        """
        发送富文本消息

        Args:
            title: 标题
            content: 内容列表，每个元素是一个字典，包含 tag 和 text

        Returns:
            API 响应
        """
        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": content
                    }
                }
            }
        }

        return self._send_request(data)

    def send_card(self, title: str, content: str, btn_text: str = "", btn_url: str = "") -> dict:
        """
        发送卡片消息

        Args:
            title: 标题
            content: 内容
            btn_text: 按钮文本（可选）
            btn_url: 按钮链接（可选）

        Returns:
            API 响应
        """
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": content,
                        "tag": "lark_md"
                    }
                }
            ]
        }

        if title:
            card["header"] = {
                "title": {
                    "content": title,
                    "tag": "plain_text"
                },
                "template": "blue"
            }

        if btn_text and btn_url:
            card["elements"].append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {
                        "content": btn_text,
                        "tag": "plain_text"
                    },
                    "url": btn_url,
                    "type": "default"
                }]
            })

        data = {
            "msg_type": "interactive",
            "card": card
        }

        return self._send_request(data)

    def _send_request(self, data: dict) -> dict:
        """
        发送 HTTP 请求

        Args:
            data: 请求数据

        Returns:
            API 响应
        """
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )

            # 记录响应信息
            logger.info(f"飞书 API 响应状态码: {response.status_code}")

            result = response.json()
            if response.status_code == 200:
                if result.get("code") == 0:
                    logger.info(f"✅ 消息发送成功")
                    return {"status": "success", "data": result}
                else:
                    logger.error(f"❌ 飞书 API 错误: {result}")
                    return {"status": "error", "error": result}
            else:
                logger.error(f"❌ HTTP 错误: {response.status_code}")
                return {"status": "error", "error": f"HTTP {response.status_code}"}

        except requests.RequestException as e:
            logger.error(f"❌ 网络请求失败: {e}")
            return {"status": "error", "error": str(e)}

    def format_analysis_card(self, analysis_data: dict, report_url: str, index_url: str = "") -> Dict:
        """
        格式化分析卡片

        Args:
            analysis_data: 分析数据
            report_url: 报告链接
            index_url: 主页链接

        Returns:
            卡片数据
        """
        # 获取币种信息
        currency = analysis_data.get('currency', 'BTC').upper()

        # 获取价格信息（兼容新旧字段名）
        price_data = analysis_data.get('currency_price', {}) or analysis_data.get('btc_price', {})
        current_price = price_data.get('price', 'N/A')
        price_change = price_data.get('change_24h', 0)
        price_change_pct = price_data.get('change_24h_pct', 0)
        price_indicator = "📈" if price_change >= 0 else "📉"
        price_color = "green" if price_change >= 0 else "red"

        # 币种图标映射
        currency_icons = {
            'BTC': '₿', 'ETH': 'Ξ', 'SOL': '◎',
            'SUI': '◆', 'BNB': '◆', 'XRP': '✕',
            'ADA': '◆', 'DOGE': 'Ð', 'DOT': '◆',
            'MATIC': '◆', 'AVAX': '◆'
        }
        icon = currency_icons.get(currency, '●')

        # 格式化时间
        timestamp = analysis_data.get('timestamp', 'N/A')
        if timestamp != 'N/A':
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass

        # 构建卡片内容
        title = f"📊 {currency} 动能分析报告"

        content = f"""**{price_indicator} {icon} {currency} 当前价格**
**${current_price}**
24h: {price_change:+.2f} ({price_change_pct:+.2f}%)

---

**时间**: {timestamp}

**【大周期】**
• 2日线: 🟢 上涨
• 1日线: 🟢 上涨

**【中周期】**
• 12小时: 🟡 动能衰竭
• 6小时: 🟡 调整期
• 4小时: 🟡 过渡期

**【小周期】**
• 2小时: 🔴 下跌
• 1小时: 🔴 下跌
• 30分钟: 🔴 下跌

---

**🎯 关键信号**
• ⚠️ 12小时出现顶背离
• 🔄 30分钟柱状图收敛，可能反转

---

**💡 操作建议**: 观望

---

📈 **[查看完整报告]({report_url})**
🏠 **[所有报告]({index_url})**

---
*数据来源: OKX API | 生成时间: {timestamp}*"""

        return {
            "title": title,
            "content": content,
            "btn_text": "查看详情",
            "btn_url": report_url
        }

    def send_analysis_report(
        self,
        analysis_data: dict,
        report_url: str,
        index_url: str = ""
    ) -> dict:
        """
        发送分析报告

        Args:
            analysis_data: 分析数据
            report_url: 报告链接
            index_url: 主页链接

        Returns:
            发送结果
        """
        card_data = self.format_analysis_card(analysis_data, report_url, index_url)
        return self.send_card(
            title=card_data["title"],
            content=card_data["content"],
            btn_text=card_data["btn_text"],
            btn_url=card_data["btn_url"]
        )

    def test_connection(self) -> bool:
        """
        测试连接

        Returns:
            连接是否成功
        """
        test_message = "✅ 飞书机器人连接测试成功！"
        result = self.send_text(test_message)
        return result.get("status") == "success"


if __name__ == "__main__":
    # 测试代码
    import os

    webhook_url = os.environ.get("FEISHU_WEBHOOK_URL")

    if webhook_url:
        bot = FeishuBot(webhook_url=webhook_url)

        # 测试连接
        if bot.test_connection():
            print("✅ Bot 连接成功")

            # 发送测试卡片
            mock_data = {
                'timestamp': '2026-01-27 16:00:00',
                'btc_price': {
                    'price': '98,456.78',
                    'change_24h': 1234.56,
                    'change_24h_pct': 1.27
                }
            }

            result = bot.send_analysis_report(
                analysis_data=mock_data,
                report_url="https://example.com/report.html",
                index_url="https://example.com/"
            )

            if result.get("status") == "success":
                print("✅ 卡片发送成功")
            else:
                print(f"❌ 卡片发送失败: {result}")
        else:
            print("❌ Bot 连接失败")
    else:
        print("请设置环境变量:")
        print("export FEISHU_WEBHOOK_URL='your_webhook_url'")
