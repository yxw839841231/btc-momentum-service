# 多币种配置化推送方案（简化版）

这是一个简化版的多币种推送方案，通过配置文件指定要推送的币种，**无需复杂的订阅管理系统**。

## 核心特点

- ✅ **配置简单**：只需编辑 `config.json` 文件
- ✅ **无需数据库**：不需要 SQLite 或其他数据库
- ✅ **无需 Bot 服务器**：不需要持续运行的服务
- ✅ **完美适配 GitHub Actions**：开箱即用
- ✅ **支持多平台**：同时推送到 Telegram 和飞书
- ✅ **灵活配置**：随时修改配置文件

## 快速开始

### 1. 编辑配置文件

打开 `config.json`，修改 `currencies` 字段：

```json
{
  "analysis": {
    "currencies": ["BTC", "ETH", "SOL"],  // ← 在这里添加币种
    "timeframes": ["2d", "1d", "12h", "6h", "4h", "2h", "1h", "30m"],
    "exchange": "okx"
  }
}
```

### 2. 运行分析

```bash
# 本地测试
python scripts/run_analysis_multi.py
```

### 3. 推送效果

每个配置的币种都会收到一条独立的分析报告消息。

## 配置示例

### 只推送 BTC

```json
{
  "analysis": {
    "currencies": ["BTC"]
  }
}
```

### 推送主流币种

```json
{
  "analysis": {
    "currencies": ["BTC", "ETH", "SOL", "BNB"]
  }
}
```

### 推送所有支持的币种

```json
{
  "analysis": {
    "currencies": ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "DOT", "MATIC", "AVAX"]
  }
}
```

## 支持的币种

| 代号 | 名称 | 价格获取 | 分析支持 |
|------|------|---------|---------|
| BTC | 比特币 | ✅ 完全支持 | ✅ 完全支持 |
| ETH | 以太坊 | ⚠️  待实现 | ✅ 完全支持 |
| SOL | Solana | ⚠️  待实现 | ✅ 完全支持 |
| BNB | Binance Coin | ⚠️  待实现 | ✅ 完全支持 |
| XRP | Ripple | ⚠️  待实现 | ✅ 完全支持 |
| ADA | Cardano | ⚠️  待实现 | ✅ 完全支持 |
| DOGE | Dogecoin | ⚠️  待实现 | ✅ 完全支持 |
| DOT | Polkadot | ⚠️  待实现 | ✅ 完全支持 |
| MATIC | Polygon | ⚠️  待实现 | ✅ 完全支持 |
| AVAX | Avalanche | ⚠️  待实现 | ✅ 完全支持 |

**注意**：非 BTC 币种的价格获取功能待实现，当前使用模拟数据。

## 文件说明

### 核心文件

- `config.json` - 配置文件（重点）
- `scripts/run_analysis_multi.py` - 多币种分析脚本（新版）
- `.github/workflows/multi-currency-analysis.yml` - GitHub Actions 配置（新版）

### 文档

- `MULTI_CURRENCY_GUIDE.md` - 详细使用指南
- `README.md` - 项目说明

## GitHub Actions 部署

### 步骤 1：配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

- `TELEGRAM_BOT_TOKEN` - Telegram Bot Token
- `TELEGRAM_CHAT_ID` - Telegram Chat ID
- `FEISHU_WEBHOOK_URL` - 飞书 Webhook URL（可选）

### 步骤 2：启用 Workflow

将 `.github/workflows/multi-currency-analysis.yml` 提交到仓库。

### 步骤 3：手动测试

在 GitHub Actions 页面手动触发 workflow 运行测试。

## 与完整版的区别

### 完整版（订阅管理）

**文件**：
- `src/subscription_manager.py` - 订阅管理
- `src/command_parser.py` - 命令解析
- `scripts/telegram_bot_server.py` - Bot 服务器
- `data/subscriptions.db` - 数据库

**特点**：
- 用户可以通过 Telegram 命令自定义订阅
- 需要数据库持久化
- 需要独立的 Bot 服务器
- 适合多用户、大量用户场景

**缺点**：
- 部署复杂
- 需要维护服务器
- 需要管理数据库

### 简化版（配置化）✨ 推荐

**文件**：
- `config.json` - 配置文件
- `scripts/run_analysis_multi.py` - 分析脚本

**特点**：
- 通过配置文件指定币种
- 无需数据库
- 无需 Bot 服务器
- 开箱即用

**缺点**：
- 所有用户接收相同的推送
- 修改配置需要提交代码

## 使用建议

### 推荐使用简化版的情况

- ✅ 个人使用
- ✅ 小团队（1-5人）
- ✅ 币种偏好固定
- ✅ 不需要频繁调整

### 需要使用完整版的情况

- 多个用户（10+）
- 每个用户需要不同的币种组合
- 需要用户自助管理订阅
- 有服务器资源

## 常见问题

### Q1: 如何修改推送的币种？

编辑 `config.json` 文件，修改 `currencies` 数组，然后提交到 GitHub。

### Q2: 能不能让不同用户接收不同的币种？

简化版不行，所有用户接收相同推送。如需此功能，请使用完整版。

### Q3: 多币种会增加 GitHub Actions 运行时间吗？

是的，每个币种都会增加大约 30-60 秒的分析时间。建议配置 1-3 个币种。

### Q4: 如何只推送到飞书，不推送到 Telegram？

在 `config.json` 中设置：
```json
{
  "telegram": {
    "enabled": false
  },
  "feishu": {
    "enabled": true,
    "webhook_url": "${FEISHU_WEBHOOK_URL}"
  }
}
```

### Q5: 能不能临时跳过某个币种？

从 `currencies` 数组中移除即可。不需要完全删除，只是暂时不分析。

## 迁移从完整版到简化版

如果从完整版迁移：

1. **保留文件**：
   - ✅ 保留 `config.json`
   - ✅ 保留 `src/price_fetcher.py`
   - ✅ 保留 `src/telegram_bot.py`
   - ✅ 保留 `src/feishu_bot.py`

2. **移除文件**（可选）：
   - ❌ 删除订阅管理相关文件
   - ❌ 停止 Bot 服务器
   - ❌ 删除数据库文件

3. **更新 GitHub Actions**：
   - 使用 `multi-currency-analysis.yml`
   - 移除数据库相关步骤

## 总结

简化版配置化方案的优势：

| 方面 | 简化版 | 完整版 |
|------|-------|--------|
| 部署难度 | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| 维护成本 | ⭐ 低 | ⭐⭐⭐ 高 |
| 灵活性 | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 高 |
| 适合场景 | 个人/小团队 | 多用户/大量用户 |

**推荐**：大多数用户使用简化版即可满足需求！

---

**需要帮助？** 查看 [MULTI_CURRENCY_GUIDE.md](MULTI_CURRENCY_GUIDE.md)
