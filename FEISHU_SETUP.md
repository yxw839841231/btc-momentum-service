# 飞书机器人配置指南

本文档说明如何配置飞书机器人接收 BTC 分析推送。

## 📱 创建飞书机器人

### 步骤 1：创建飞书群组

1. 打开飞书客户端或网页版
2. 创建一个新群组或使用现有群组
3. 记下群组名称

### 步骤 2：添加自定义机器人

1. 进入群组聊天界面
2. 点击群组名称打开群设置
3. 找到 **"群机器人"** → **"添加机器人"**
4. 点击 **"自定义机器人"**
5. 输入机器人名称：`BTC 分析助手`
6. 点击 **"添加"**
7. **重要**：复制生成的 Webhook URL
   - 格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxx`
   - 请妥善保管，不要泄露

### 步骤 3：测试机器人

在飞书群组中发送消息测试机器人是否正常工作。

## 🔧 配置 GitHub Secrets

### 添加飞书 Webhook URL

1. 访问 GitHub 仓库设置
   ```
   https://github.com/yxw839841231/btc-momentum-service/settings/secrets/actions
   ```

2. 点击 **"New repository secret"**

3. 添加以下 Secret：
   - **Name**: `FEISHU_WEBHOOK_URL`
   - **Value**: 你的飞书机器人 Webhook URL（完整URL）
   - 点击 **"Add secret"**

### 同时支持 Telegram 和飞书

你可以同时配置两个平台：

**已配置的 Secrets**：
- `TELEGRAM_BOT_TOKEN` - Telegram Bot Token
- `TELEGRAM_CHAT_ID` - Telegram Chat ID
- `FEISHU_WEBHOOK_URL` - 飞书 Webhook URL

**注意**：
- 至少需要配置一个平台（Telegram 或飞书）
- 可以同时配置两个，系统会同时推送到两个平台
- 如果只配置一个，只会推送到该平台

## 🧪 本地测试

### 测试飞书机器人

```bash
cd /Users/yxw/code/BTC/btc-momentum-service

export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_url"

python3 src/feishu_bot.py
```

如果成功，你应该在飞书群组中收到测试消息。

### 测试完整流程

```bash
export TELEGRAM_BOT_TOKEN="your_telegram_token"  # 可选
export TELEGRAM_CHAT_ID="your_chat_id"           # 可选
export FEISHU_WEBHOOK_URL="your_feishu_url"     # 可选（至少配置一个）

python3 scripts/run_analysis.py
```

## 📊 飞书消息格式

飞书机器人会收到漂亮的卡片消息：

```
┌─────────────────────────────────┐
│ 📊 BTC 动能分析报告              │
├─────────────────────────────────┤
│                                  │
│ 📈 当前价格                      │
│ 98,456.78                       │
│ 24h: +1234.56 (+1.27%)          │
│                                  │
│ 时间: 2026-01-27 16:00:00       │
│                                  │
│ 【大周期】                       │
│ • 2日线: 🟢 上涨                 │
│ • 1日线: 🟢 上涨                 │
│                                  │
│ 【中周期】                       │
│ • 12小时: 🟡 动能衰竭            │
│ • 6小时: 🟡 调整期               │
│ • 4小时: 🟡 过渡期               │
│                                  │
│ 【小周期】                       │
│ • 2小时: 🔴 下跌                 │
│ • 1小时: 🔴 下跌                 │
│ • 30分钟: 🔴 下跌                │
│                                  │
│ 🎯 关键信号                      │
│ • ⚠️ 12小时出现顶背离            │
│ • 🔄 30分钟柱状图收敛            │
│                                  │
│ 💡 操作建议: 观望                │
│                                  │
│ [查看详情] 按钮                  │
└─────────────────────────────────┘
```

## ⚙️ 高级配置

### 只使用飞书（不使用 Telegram）

如果你想只用飞书：

**选项 A：删除 Telegram Secrets**
1. 访问 GitHub Secrets 设置
2. 删除 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`
3. 保留 `FEISHU_WEBHOOK_URL`
4. 系统会自动检测并只推送到飞书

**选项 B：留空但不删除**
- 不设置 Telegram 环境变量
- 只设置 `FEISHU_WEBHOOK_URL`
- 系统会自动跳过 Telegram

### 推送到多个飞书群组

如果你需要推送到多个飞书群组：

**方法 1：使用群机器人广播**
- 在多个群组中添加同一个机器人
- 机器人会自动推送到所有群组

**方法 2：创建多个 Webhook**
- 在每个群组中创建机器人
- 修改代码支持多个 Webhook URL
- 需要开发扩展功能

## 🔍 故障排查

### 问题 1：飞书收不到消息

**检查清单**：
1. ✅ 确认 `FEISHU_WEBHOOK_URL` 已正确添加到 GitHub Secrets
2. ✅ Webhook URL 完整且正确（以 `https://open.feishu.cn` 开头）
3. ✅ 机器人已添加到群组
4. ✅ GitHub Actions 运行成功（绿色 ✓）

**调试步骤**：
1. 本地测试飞书机器人
   ```bash
   export FEISHU_WEBHOOK_URL="your_url"
   python3 src/feishu_bot.py
   ```
2. 查看 GitHub Actions 日志
3. 检查飞书群组是否移除了机器人

### 问题 2：GitHub Actions 失败

**可能原因**：
- 没有配置任何消息平台（Telegram 或飞书）
- 代码执行错误

**解决方法**：
- 至少配置一个平台的 Webhook
- 查看 Actions 日志获取详细错误信息

### 问题 3：消息格式显示异常

**可能原因**：
- Markdown 格式不兼容

**解决方法**：
- 飞书机器人使用富文本和卡片格式
- 已优化兼容性，应该不会有问题
- 如果仍有问题，请提交 Issue

## 📝 Webhook URL 安全提示

⚠️ **重要安全建议**：

1. **不要泄露 Webhook URL**
   - Webhook URL 就像密码，任何人拥有它都能发送消息
   - 不要在公开代码中提交
   - 不要在公开论坛分享

2. **定期轮换 Webhook**
   - 如果怀疑泄露，删除旧机器人并创建新的
   - 更新 GitHub Secrets

3. **使用环境变量**
   - 始终使用 GitHub Secrets 存储
   - 不要硬编码在脚本中

## 🎯 快速开始

### 最简配置（只用飞书）

```bash
# 1. 创建飞书机器人并获取 Webhook URL

# 2. 添加到 GitHub Secrets
# Name: FEISHU_WEBHOOK_URL
# Value: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx

# 3. 手动触发 GitHub Actions 测试
# 访问 Actions → BTC Momentum Analysis → Run workflow

# 4. 等待接收消息
```

### 完整配置（Telegram + 飞书）

只需同时配置三个 Secrets：
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `FEISHU_WEBHOOK_URL`

系统会自动同时推送到两个平台！

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 GitHub Actions 日志
2. 提交 GitHub Issue
3. 参考飞书机器人官方文档

祝你使用愉快！🚀
