# 多币种配置化推送指南

## 概述

这是一个简化版本的多币种推送方案，通过配置文件指定要推送的币种，无需复杂的订阅管理系统。

**特点**：
- ✅ 简单配置，无需数据库
- ✅ 支持多币种推送
- ✅ 一次性配置，自动运行
- ✅ 完美适配 GitHub Actions

## 快速开始

### 1. 配置币种

编辑 `config.json` 文件：

```json
{
  "analysis": {
    "currencies": ["BTC", "ETH", "SOL"],
    "timeframes": ["2d", "1d", "12h", "6h", "4h", "2h", "1h", "30m"],
    "exchange": "okx"
  },
  "telegram": {
    "enabled": true,
    "bot_token": "${TELEGRAM_BOT_TOKEN}",
    "chat_id": "${TELEGRAM_CHAT_ID}"
  },
  "feishu": {
    "enabled": false,
    "webhook_url": "${FEISHU_WEBHOOK_URL}"
  },
  "reports": {
    "output_dir": "reports",
    "github_pages_url": "https://your-username.github.io/btc-momentum-service"
  }
}
```

### 2. 配置说明

#### currencies - 要分析的币种列表

支持以下币种：
- `BTC` - 比特币（默认，完全支持）
- `ETH` - 以太坊
- `SOL` - Solana
- `BNB` - Binance Coin
- `XRP` - Ripple
- `ADA` - Cardano
- `DOGE` - Dogecoin
- `DOT` - Polkadot
- `MATIC` - Polygon
- `AVAX` - Avalanche

**示例**：
```json
// 只推送 BTC
"currencies": ["BTC"]

// 推送 BTC 和 ETH
"currencies": ["BTC", "ETH"]

// 推送多个主流币种
"currencies": ["BTC", "ETH", "SOL", "BNB"]
```

#### telegram - Telegram 配置

```json
"telegram": {
  "enabled": true,  // true = 启用, false = 禁用
  "bot_token": "${TELEGRAM_BOT_TOKEN}",  // 从环境变量读取
  "chat_id": "${TELEGRAM_CHAT_ID}"
}
```

#### feishu - 飞书配置

```json
"feishu": {
  "enabled": false,  // true = 启用, false = 禁用
  "webhook_url": "${FEISHU_WEBHOOK_URL}"
}
```

#### reports - 报告配置

```json
"reports": {
  "output_dir": "reports",  // 报告输出目录
  "github_pages_url": "https://your-username.github.io/btc-momentum-service"
}
```

### 3. 运行分析

#### 本地测试

```bash
# 设置环境变量
export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id'

# 运行分析
python scripts/run_analysis_multi.py
```

#### GitHub Actions

修改 `.github/workflows/scheduled-analysis.yml`：

```yaml
- name: 运行多币种分析
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
    FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
  run: |
    python scripts/run_analysis_multi.py
```

### 4. 配置示例

#### 示例 1：只推送 BTC

```json
{
  "analysis": {
    "currencies": ["BTC"],
    "timeframes": ["2d", "1d", "12h", "6h", "4h", "2h", "1h", "30m"],
    "exchange": "okx"
  },
  "telegram": {
    "enabled": true,
    "bot_token": "${TELEGRAM_BOT_TOKEN}",
    "chat_id": "${TELEGRAM_CHAT_ID}"
  },
  "feishu": {
    "enabled": false
  }
}
```

#### 示例 2：推送 BTC、ETH、SOL

```json
{
  "analysis": {
    "currencies": ["BTC", "ETH", "SOL"],
    "timeframes": ["2d", "1d", "12h", "6h", "4h", "2h", "1h", "30m"],
    "exchange": "okx"
  },
  "telegram": {
    "enabled": true,
    "bot_token": "${TELEGRAM_BOT_TOKEN}",
    "chat_id": "${TELEGRAM_CHAT_ID}"
  },
  "feishu": {
    "enabled": true,
    "webhook_url": "${FEISHU_WEBHOOK_URL}"
  }
}
```

#### 示例 3：所有主流币种

```json
{
  "analysis": {
    "currencies": ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "DOT", "MATIC", "AVAX"],
    "timeframes": ["1d", "4h", "1h"],
    "exchange": "okx"
  },
  "telegram": {
    "enabled": true,
    "bot_token": "${TELEGRAM_BOT_TOKEN}",
    "chat_id": "${TELEGRAM_CHAT_ID}"
  },
  "feishu": {
    "enabled": false
  }
}
```

## 工作流程

```
1. 读取 config.json 配置
   ↓
2. 循环处理每个币种
   ├─ 获取价格
   ├─ 运行分析
   ├─ 生成报告
   └─ 推送消息
   ↓
3. 生成索引页面
   ↓
4. 完成
```

## 推送效果

### Telegram

每个币种推送一条独立消息：

```
📊 ₿ BTC 动能分析

💰 价格: 📈 $98,456.78
   24h: +1,234.56 (+1.27%)

时间: 2026-01-27 18:00:00
【大周期】2日线 ↑ 1日线 ↑
【中周期】12h ⚠️  6h 调整 4h ↓
【小周期】2h ↓ 1h ↓ 30m ⟲

📈 最新报告:
https://yxw839841231.github.io/.../btc_analysis_20250127_1800.html

💡 操作建议: 观望
```

```
📊 Ξ ETH 动能分析

💰 价格: 📈 $3,456.78
   24h: +123.45 (+3.69%)

...
```

### 飞书

每个币种推送一张独立卡片，包含币种图标和颜色。

## 高级配置

### 修改时间级别

如果不需要所有时间级别，可以减少分析的时间：

```json
{
  "analysis": {
    "currencies": ["BTC"],
    "timeframes": ["1d", "4h", "1h"],  // 只分析这3个时间级别
    "exchange": "okx"
  }
}
```

### 同时推送到 Telegram 和飞书

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "${TELEGRAM_BOT_TOKEN}",
    "chat_id": "${TELEGRAM_CHAT_ID}"
  },
  "feishu": {
    "enabled": true,  // 同时启用飞书
    "webhook_url": "${FEISHU_WEBHOOK_URL}"
  }
}
```

### 自定义 GitHub Pages URL

```json
{
  "reports": {
    "github_pages_url": "https://your-custom-domain.com"
  }
}
```

## 注意事项

### 1. 价格获取

当前版本：
- ✅ BTC 价格获取完全支持
- ⚠️  其他币种价格获取待实现（使用模拟数据）

如需其他币种的真实价格，需要扩展 `price_fetcher.py`。

### 2. 分析完整性

所有币种都使用相同的动能分析逻辑，但：
- BTC 数据源：OKX/Binance API
- 其他币种：待添加数据源

### 3. 推送频率

币种越多，推送消息越多。例如：
- 1 个币种 = 1 条消息
- 3 个币种 = 3 条消息
- 10 个币种 = 10 条消息

建议：
- 个人使用：1-3 个币种
- 小团队：3-5 个币种
- 大团队：5-10 个币种

## 常见问题

### Q1: 如何添加新币种？

在 `config.json` 的 `currencies` 数组中添加：
```json
"currencies": ["BTC", "ETH", "NEW_COIN"]
```

### Q2: 如何临时禁用某个币种？

从 `currencies` 数组中移除：
```json
"currencies": ["BTC", "SOL"]  // ETH 被移除
```

### Q3: 如何只运行一次分析？

```bash
python scripts/run_analysis_multi.py
```

### Q4: 如何修改 GitHub Pages URL？

在 `config.json` 中修改：
```json
{
  "reports": {
    "github_pages_url": "https://your-new-url.github.io/repo"
  }
}
```

### Q5: 如何验证配置是否正确？

```bash
# 测试配置加载
python -c "
import json
with open('config.json') as f:
    config = json.load(f)
    print('配置的币种:', config['analysis']['currencies'])
    print('Telegram 启用:', config['telegram']['enabled'])
    print('飞书启用:', config['feishu']['enabled'])
"
```

## 与订阅管理版本的区别

| 功能 | 配置化版本 | 订阅管理版本 |
|------|-----------|-------------|
| 配置方式 | config.json 文件 | Telegram Bot 命令 |
| 数据库 | 不需要 | SQLite 数据库 |
| Bot 服务器 | 不需要 | 需要持续运行 |
| 部署复杂度 | 简单 | 复杂 |
| 适用场景 | 个人/小团队 | 多用户/大量用户 |
| 灵活性 | 每次运行前配置 | 用户可随时修改 |
| 个性化 | 所有人接收相同内容 | 每人接收不同内容 |

## 迁移指南

如果从订阅管理版本迁移到配置化版本：

1. **保留配置文件**
   - 删除订阅管理相关文件
   - 保留 `config.json`

2. **简化 GitHub Actions**
   - 使用 `run_analysis_multi.py`
   - 移除数据库相关步骤

3. **清理环境**
   - 停止 Bot 服务器
   - 删除数据库文件（可选）

## 总结

配置化方案的优势：
- ✅ 部署简单，无需额外服务
- ✅ 配置直观，易于理解
- ✅ 完美适配 GitHub Actions
- ✅ 无需管理数据库
- ✅ 适合个人和小团队使用

**建议**：大多数用户使用这个配置化版本即可满足需求。

---

**需要帮助？** 请查看项目文档或提交 Issue。
