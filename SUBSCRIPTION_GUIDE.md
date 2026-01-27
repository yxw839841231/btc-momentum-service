# 订阅管理使用指南

本指南详细说明如何使用订阅管理功能自定义接收的分析内容。

## 目录

- [快速开始](#快速开始)
- [订阅类型详解](#订阅类型详解)
- [命令参考](#命令参考)
- [使用场景](#使用场景)
- [常见问题](#常见问题)

## 快速开始

### 第一步：添加 Bot

在 Telegram 中搜索你的 Bot，点击 "Start" 或发送 `/start` 命令。

### 第二步：查看帮助

发送 `/help` 查看所有可用命令。

### 第三步：设置订阅

```bash
# 订阅日线和4小时线
/subscribe 1d 4h

# 查看订阅状态
/mysubscriptions
```

## 订阅类型详解

### 1. 时间级别订阅

**作用**：控制接收哪些时间级别的分析报告

**支持的时间级别**：
- `2d` - 2日线（大周期）
- `1d` - 日线（大周期）
- `12h` - 12小时线（中周期）
- `6h` - 6小时线（中周期）
- `4h` - 4小时线（中周期）
- `2h` - 2小时线（小周期）
- `1h` - 1小时线（小周期）
- `30m` - 30分钟线（小周期）

**示例**：
```bash
# 只接收日线报告
/subscribe 1d

# 接收多个时间级别
/subscribe 1d 4h 1h

# 取消某个时间级别
/unsubscribe 30m
```

**注意**：如果不设置时间级别，默认接收所有时间级别的报告。

### 2. 币种订阅

**作用**：选择接收哪些加密货币的分析

**支持的币种**：
- BTC（比特币）
- ETH（以太坊）
- SOL（Solana）
- BNB（Binance Coin）
- XRP（Ripple）
- ADA（Cardano）
- DOGE（Dogecoin）
- DOT（Polkadot）
- MATIC（Polygon）
- AVAX（Avalanche）

**示例**：
```bash
# 订阅 BTC 和 ETH
/subscribe_currency btc eth

# 订阅多个币种
/subscribe_currency btc eth sol bnb

# 取消某个币种
/unsubscribe_currency eth

# 查看订阅的币种
/my_currencies

# 查看所有支持的币种
/list_currencies
```

**注意**：
- 新用户默认只订阅 BTC
- 每个币种会生成独立的分析报告
- 建议只订阅你关注或交易的币种

### 3. 信号类型订阅

**作用**：控制接收哪些类型的信号告警

**支持的信号类型**：
- `divergence` - 背离信号（顶背离、底背离）
- `buy_signal` - 买点信号
- `sell_signal` - 卖点信号
- `discrete_control` - 分立调控

**示例**：
```bash
# 订阅背离信号
/subscribe_signal divergence

# 订阅多种信号
/subscribe_signal divergence buy_signal

# 取消某个信号
/unsubscribe_signal sell_signal
```

**注意**：如果不设置信号类型，默认接收所有信号类型的告警。

### 4. 推送频率

**作用**：控制接收消息的频率

**支持的频率**：
- `all` - 接收所有推送（常规报告 + 告警）
- `alerts` - 仅重要告警，不推送常规报告
- `daily` - 每日摘要（暂未实现）
- `none` - 暂停所有推送

**示例**：
```bash
# 仅接收告警
/frequency alerts

# 恢复所有推送
/frequency all

# 暂停推送
/frequency none
```

## 命令参考

### 基础命令

| 命令 | 别名 | 说明 |
|------|------|------|
| `/help` | `/h`, `/?` | 显示帮助信息 |
| `/mysubscriptions` | `/mysubs`, `/my` | 查看当前订阅 |

### 时间级别订阅

| 命令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `/subscribe <tf>` | `/sub` | 订阅时间级别 | `/subscribe 1d 4h` |
| `/unsubscribe <tf>` | `/unsub` | 取消时间级别 | `/unsubscribe 30m` |

### 币种订阅

| 命令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `/subscribe_currency <symbols>` | `/subcur` | 订阅币种 | `/subscribe_currency btc eth` |
| `/unsubscribe_currency <symbols>` | `/unsubcur` | 取消币种 | `/unsubscribe_currency eth` |
| `/my_currencies` | `/mycur`, `/mc` | 查看订阅的币种 | - |
| `/list_currencies` | `/listcur`, `/lc` | 列出所有支持的币种 | - |

### 信号订阅

| 命令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `/subscribe_signal <type>` | `/ssub` | 订阅信号类型 | `/subscribe_signal divergence` |
| `/unsubscribe_signal <type>` | `/usub` | 取消信号类型 | `/unsubscribe_signal sell_signal` |

### 推送控制

| 命令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `/frequency <freq>` | `/freq`, `/f` | 设置推送频率 | `/frequency alerts` |

## 使用场景

### 场景 1：长期投资者

只关注日线级别的趋势变化。

```bash
/subscribe 1d
/subscribe_currency btc
/frequency all
```

### 场景 2：日内交易者

关注短周期变化，多个币种。

```bash
/subscribe 4h 1h 30m
/subscribe_currency btc eth sol
/frequency alerts
```

### 场景 3：背离信号跟踪者

只接收背离信号告警。

```bash
/subscribe_signal divergence
/frequency alerts
```

### 场景 4：多币种持有者

关注多个币种的大周期趋势。

```bash
/subscribe 1d
/subscribe_currency btc eth bnb sol ada
/frequency all
```

## 常见问题

### Q1: 如何停止接收所有消息？

```bash
/frequency none
```

### Q2: 如何只接收重要告警？

```bash
/frequency alerts
```

### Q3: 取消订阅后还能收到报告吗？

这取决于你的其他订阅设置：
- 如果设置了 `/frequency alerts`，只接收告警
- 如果设置了时间级别，只接收那些级别的报告
- 如果设置了币种，只接收那些币种的报告

### Q4: 如何重置所有订阅？

取消所有时间级别订阅：
```bash
/unsubscribe 2d 1d 12h 6h 4h 2h 1h 30m
```

然后重新订阅你需要的级别。

### Q5: 为什么没有收到报告？

检查以下几点：
1. 查看订阅状态：`/mysubscriptions`
2. 确认推送频率不是 `none`
3. 确认订阅了该币种
4. 确认订阅了该时间级别

### Q6: 可以订阅所有币种吗？

理论上可以，但建议只订阅你关注的币种（3-5个），避免消息过多。

### Q7: 飞书机器人如何使用订阅？

飞书机器人目前使用 Webhook 推送，暂不支持交互式命令。建议使用 Telegram Bot 进行订阅管理。

## 技术说明

### 数据存储

订阅数据存储在 SQLite 数据库中（`data/subscriptions.db`），包括：
- 用户 ID 和 Chat ID
- 订阅的币种列表
- 订阅的时间级别列表
- 订阅的信号类型列表
- 推送频率设置

### 推送逻辑

系统在推送前会检查：
1. 用户的推送频率设置
2. 用户是否订阅了该币种
3. 用户是否订阅了该时间级别
4. 用户是否订阅了该信号类型（仅告警）

只有所有条件满足时才会推送。

### 隐私保护

- 用户数据仅用于推送功能
- 不收集任何个人信息
- 数据库仅供系统使用

## 反馈与支持

如有问题或建议，请通过 GitHub Issues 联系。

---

**祝使用愉快！** 🚀
