# Telegram Bot 服务器使用指南

## 概述

Telegram Bot 服务器用于接收和处理用户的订阅命令。由于 GitHub Actions 只是定时运行分析任务，无法持续接收 Bot 命令，因此需要单独运行 Bot 服务器。

## 两种运行模式

### 模式 1：本地运行（推荐用于测试）

适合：
- ✅ 个人使用
- ✅ 测试功能
- ✅ 小规模部署

**步骤**：

1. 安装依赖
```bash
cd btc-momentum-service
pip install -r requirements.txt
```

2. 设置环境变量
```bash
export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id'  # 可选，用于推送
```

3. 运行 Bot 服务器
```bash
python scripts/telegram_bot_server.py
```

4. 在 Telegram 中测试
```
/start          # 启动 Bot
/help           # 查看帮助
/subscribe 1d   # 订阅日线
/mysubscriptions # 查看订阅
```

### 模式 2：服务器运行（推荐用于生产）

适合：
- ✅ 24/7 运行
- ✅ 多用户使用
- ✅ 生产环境

#### 方案 A：使用 systemd（Linux）

1. 创建服务文件
```bash
sudo nano /etc/systemd/system/btc-momentum-bot.service
```

2. 添加以下内容
```ini
[Unit]
Description=BTC Momentum Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/btc-momentum-service
Environment="TELEGRAM_BOT_TOKEN=your_bot_token"
Environment="SUBSCRIPTION_DB_PATH=data/subscriptions.db"
ExecStart=/usr/bin/python3 scripts/telegram_bot_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable btc-momentum-bot
sudo systemctl start btc-momentum-bot
sudo systemctl status btc-momentum-bot
```

#### 方案 B：使用 Docker

1. 创建 Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TELEGRAM_BOT_TOKEN=""
ENV SUBSCRIPTION_DB_PATH="data/subscriptions.db"

CMD ["python", "scripts/telegram_bot_server.py"]
```

2. 构建并运行
```bash
docker build -t btc-momentum-bot .
docker run -d \
  -e TELEGRAM_BOT_TOKEN="your_bot_token" \
  -v $(pwd)/data:/app/data \
  --name btc-bot \
  btc-momentum-bot
```

#### 方案 C：使用 Screen/Tmux

```bash
# 使用 screen
screen -S btc-bot
python scripts/telegram_bot_server.py
# 按 Ctrl+A, D 分离会话

# 重新连接
screen -r btc-bot

# 使用 tmux
tmux new-session -d -s btc-bot 'python scripts/telegram_bot_server.py'
tmux attach-session -t btc-bot
```

## 支持的命令

### 基础命令

| 命令 | 说明 |
|------|------|
| `/start` | 启动 Bot，显示欢迎信息 |
| `/help` | 显示所有可用命令 |

### 订阅管理

#### 时间级别订阅
```
/subscribe <时间级别>      # 订阅时间级别
  示例: /subscribe 1d 4h 1h

/unsubscribe <时间级别>    # 取消订阅
  示例: /unsubscribe 30m
```

支持的时间级别：
- `2d`, `1d` - 大周期
- `12h`, `6h`, `4h` - 中周期
- `2h`, `1h`, `30m` - 小周期

#### 币种订阅
```
/subscribe_currency <币种>  # 订阅币种
  示例: /subscribe_currency btc eth sol

/unsubscribe_currency <币种> # 取消订阅
  示例: /unsubscribe_currency eth

/my_currencies              # 查看订阅的币种
/list_currencies            # 列出所有支持的币种
```

支持的币种：
`BTC`, `ETH`, `SOL`, `BNB`, `XRP`, `ADA`, `DOGE`, `DOT`, `MATIC`, `AVAX`

#### 信号类型订阅
```
/subscribe_signal <类型>    # 订阅信号类型
  示例: /subscribe_signal divergence

/unsubscribe_signal <类型>  # 取消订阅
  示例: /unsubscribe_signal sell_signal
```

支持的信号类型：
- `divergence` - 背离信号
- `buy_signal` - 买点信号
- `sell_signal` - 卖点信号
- `discrete_control` - 分立调控

#### 查询和设置
```
/mysubscriptions            # 查看我的所有订阅
/frequency <频率>           # 设置推送频率
  示例: /frequency alerts
```

支持的频率：
- `all` - 所有推送（默认）
- `alerts` - 仅重要告警
- `daily` - 每日摘要
- `none` - 暂停推送

## 常见问题

### Q1: Bot 没有响应命令

**检查**：
1. Bot 服务器是否正在运行？
   ```bash
   ps aux | grep telegram_bot_server
   ```

2. 环境变量是否正确设置？
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   ```

3. 查看日志是否有错误
   ```bash
   # 如果使用 systemd
   journalctl -u btc-momentum-bot -f

   # 如果直接运行
   # 查看控制台输出
   ```

### Q2: 如何停止 Bot 服务器

```bash
# 如果直接运行
# 按 Ctrl+C

# 如果使用 systemd
sudo systemctl stop btc-momentum-bot

# 如果使用 Docker
docker stop btc-bot

# 如果使用 screen
screen -S btc-bot -X quit
```

### Q3: Bot 服务器崩溃了怎么办

**自动重启**：
- systemd 服务会自动重启
- Docker 可以使用 `--restart` 策略

**手动重启**：
```bash
# systemd
sudo systemctl restart btc-momentum-bot

# Docker
docker restart btc-bot
```

### Q4: 可以在没有服务器的情况下使用吗？

**是的！** 可以在本地计算机上运行：
1. 保持计算机开启
2. 运行 Bot 服务器
3. 使用 screen/tmux 保持会话

**注意事项**：
- ⚠️ 本地运行需要保持网络连接
- ⚠️ 计算机关闭后 Bot 将无法响应
- ⚠️ 不适合 24/7 运行

### Q5: 如何查看 Bot 日志

```bash
# systemd
journalctl -u btc-momentum-bot -n 100 -f

# Docker
docker logs -f btc-bot

# 本地运行（直接查看控制台）
# 或重定向到文件
python scripts/telegram_bot_server.py > bot.log 2>&1
```

## 数据持久化

订阅数据存储在 `data/subscriptions.db` 文件中。

**重要**：
- Bot 服务器和 GitHub Actions 使用同一个数据库文件
- 确保 Bot 服务器有数据库文件的读写权限
- 定期备份数据库文件

```bash
# 备份数据库
cp data/subscriptions.db data/subscriptions.db.backup.$(date +%Y%m%d)
```

## 安全建议

1. **保护 Bot Token**
   - 不要将 Bot Token 提交到代码仓库
   - 使用环境变量存储敏感信息
   - 定期更换 Bot Token

2. **限制 Bot 访问**
   - 在 BotFather 中设置隐私模式
   - 限制 Bot 只能被授权用户访问

3. **日志安全**
   - 不要在日志中记录敏感信息
   - 定期清理旧日志

## 与 GitHub Actions 的关系

```
GitHub Actions (定时运行)
  ↓
运行分析任务
  ↓
读取订阅数据库
  ↓
根据订阅推送消息
  ↓
完成

Telegram Bot 服务器 (持续运行)
  ↓
接收用户命令
  ↓
更新订阅数据库
  ↓
响应确认
  ↓
继续等待下一个命令
```

**关键点**：
- GitHub Actions 读取订阅数据库决定推送内容
- Bot 服务器接收命令并写入订阅数据库
- 两者共享同一个数据库文件

## 性能优化

### 减少轮询频率

编辑 `scripts/telegram_bot_server.py`：
```python
poll_interval = 5  # 增加到 5 秒
```

### 使用 Webhook（高级）

Webhook 比轮询更高效，但需要：
1. 公网 IP 或域名
2. HTTPS 证书
3. 开放端口

详见：https://core.telegram.org/bots/webhooks

## 测试

### 本地测试

```bash
# 运行 Bot 服务器
python scripts/telegram_bot_server.py

# 在另一个终端测试
python scripts/test_bot_commands.py
```

### 功能测试

```
1. 发送 /start
   预期: 收到欢迎消息

2. 发送 /help
   预期: 收到命令列表

3. 发送 /subscribe 1d
   预期: 订阅成功确认

4. 发送 /mysubscriptions
   预期: 显示当前订阅

5. 发送 /list_currencies
   预期: 显示支持的币种
```

## 监控和维护

### 日志监控

```bash
# 实时查看日志
tail -f bot.log

# 查看错误
grep ERROR bot.log
```

### 性能监控

```bash
# 检查内存使用
ps aux | grep telegram_bot_server

# 检查数据库大小
ls -lh data/subscriptions.db
```

### 定期维护

```bash
# 每周备份数据库
crontab -e
# 添加: 0 0 * * 0 cp data/subscriptions.db data/backups/

# 清理旧日志
find . -name "bot.log.*" -mtime +30 -delete
```

## 总结

- ✅ Bot 服务器需要持续运行
- ✅ 使用 systemd/Docker/screen 管理进程
- ✅ 与 GitHub Actions 共享数据库
- ✅ 支持完整的订阅管理命令
- ✅ 建议使用服务器运行以获得最佳体验

---

**需要帮助？** 请查看 [DEPLOYMENT.md](DEPLOYMENT.md) 或提交 Issue。
