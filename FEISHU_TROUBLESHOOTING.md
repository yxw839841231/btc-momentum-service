# 飞书多币种推送问题排查

## 问题描述

Telegram 能推送所有币种，但飞书只推送了部分币种（或只推送了 BTC）。

## 可能的原因

### 1. 飞书 Webhook 频率限制 ⚠️ 最可能

飞书机器人 Webhook 对短时间内的消息发送频率有限制。如果短时间内发送多条消息，可能会触发限流机制，导致部分消息被拒绝。

**症状**：
- 第一条消息（BTC）成功
- 后续消息（SUI、SOL）失败
- 日志显示 API 错误或超时

### 2. 网络问题

网络不稳定可能导致某些消息发送失败。

### 3. 消息格式问题

某些币种的数据可能导致消息格式错误。

## 已实施的解决方案

### 1. 添加发送延迟

在每个币种的消息之间添加 2 秒延迟，避免触发飞书限流：

```python
for i, result in enumerate(all_results, 1):
    # 发送消息...

    # 第2条消息开始添加延迟
    if i > 1:
        time.sleep(2)
```

### 2. 改进错误处理

- 详细记录每个币种的发送状态
- 显示成功/失败统计
- 输出详细的错误信息和可能的原因

### 3. 增强日志

飞书 Bot 现在会记录：
- 发送的 URL（前 50 个字符）
- API 响应状态码
- 错误代码和消息
- 完整的错误响应

## 使用调试工具

### 运行飞书推送测试

```bash
# 设置环境变量
export FEISHU_WEBHOOK_URL='your_webhook_url'

# 运行调试脚本
python3 scripts/debug_feishu_push.py
```

脚本会：
1. 测试 BTC、SUI、SOL 三个币种的推送
2. 显示每个币种的发送状态
3. 输出详细的错误信息
4. 提供诊断建议

## 查看日志

### GitHub Actions 日志

在 GitHub Actions 运行日志中查找：

**1. 推送开始**：
```
📱 推送到飞书...
```

**2. 每个币种的推送状态**：
```
[1/3] 正在推送 BTC 到飞书...
  ✅ BTC 飞书推送成功

[2/3] 正在推送 SUI 到飞书...
  等待 2 秒以避免触发飞书限流...
  ✅ SUI 飞书推送成功

[3/3] 正在推送 SOL 到飞书...
  等待 2 秒以避免触发飞书限流...
  ❌ SOL 飞书推送失败
  错误详情: ...
```

**3. 最终统计**：
```
📱 飞书推送完成: 2 成功, 1 失败 (总计 3 个)
```

**4. 错误诊断**（如果有失败）：
```
⚠️  有 1 个币种推送失败，可能原因：
  - 飞书 Webhook 频率限制
  - 网络问题
  - 消息格式问题
```

### 飞书 API 错误码

常见错误码：

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 99991663 | 请求频率过快 | 增加发送延迟 |
| 99991401 | 参数错误 | 检查消息格式 |
| 99991400 | webhook 不存在 | 检查 webhook URL |

## 配置调整

### 调整发送延迟

如果仍然遇到限流问题，可以增加延迟时间：

编辑 `scripts/run_analysis_multi.py` 第 246 行：

```python
# 当前延迟 2 秒
time.sleep(2)

# 建议增加到 3-5 秒
time.sleep(5)
```

### 禁用飞书推送

如果飞书推送问题无法解决，可以暂时禁用：

编辑 `config.json`：

```json
{
  "feishu": {
    "enabled": false,
    "webhook_url": "${FEISHU_WEBHOOK_URL}"
  }
}
```

## 验证步骤

### 1. 测试单个币种

运行调试脚本，只测试一个币种，确认基本功能正常。

### 2. 测试多个币种

逐步增加币种数量，观察哪个币种开始失败。

### 3. 检查飞书群

在飞书群中确认：
- 是否收到了第一条消息（BTC）
- 是否收到了后续消息（SUI、SOL）
- 消息时间间隔是多少

### 4. 对比 Telegram

Telegram 和飞书使用相同的分析结果，对比两者收到的消息数量。

## 替代方案

如果飞书 Webhook 限流问题无法解决：

### 方案 1: 合并消息

将所有币种合并为一条飞书消息发送：

```python
# 一次性发送所有币种的汇总
combined_message = format_combined_summary(all_results)
feishu_bot.send_text(combined_message)
```

### 方案 2: 只推送重要币种

在配置中指定只推送某些币种到飞书：

```json
{
  "analysis": {
    "currencies": ["BTC", "SUI", "SOL"],
    "feishu_currencies": ["BTC"]  // 只推送 BTC 到飞书
  }
}
```

### 方案 3: 使用 Telegram

如果 Telegram 推送正常，可以暂时只使用 Telegram。

## 相关文件

- `scripts/run_analysis_multi.py` - 主推送脚本
- `src/feishu_bot.py` - 飞书 Bot 实现
- `scripts/debug_feishu_push.py` - 调试工具
- `TROUBLESHOOTING.md` - 通用故障排查指南

## 获取帮助

如果以上方法都无法解决问题，请提供：

1. GitHub Actions 运行日志（完整或关键部分）
2. 调试脚本的运行输出
3. 飞书群收到的消息截图
4. config.json 内容（隐藏敏感信息）
