# 问题修复说明

## 已修复的问题

### 问题 1：飞书消息没有显示实时价格 ❌ → ✅

**症状**：
- 部署后，推送到飞书的消息中没有实时价格信息
- 价格显示为 "N/A" 或空值

**原因**：
- 代码重构后，价格字段从 `btc_price` 改为 `currency_price`
- 飞书机器人的 `format_analysis_card` 方法还在使用旧的字段名

**修复**：
- 更新 `src/feishu_bot.py` 中的 `format_analysis_card` 方法
- 支持新的 `currency_price` 字段
- 添加向后兼容，同时检查新旧字段
- 添加币种图标和颜色支持

**修复位置**：
```
src/feishu_bot.py:186-224
```

**验证**：
```bash
# 本地测试
python3 scripts/test_subscription.py

# 触发 GitHub Actions 并检查飞书消息
```

---

### 问题 2：Telegram Bot 无法接收命令 ❌ → ✅

**症状**：
- 在 Telegram 中发送命令（如 `/subscribe`）没有响应
- Bot 只能推送消息，无法交互

**原因**：
- 当前的 Telegram Bot 实现只是简单的 HTTP 客户端
- GitHub Actions 只是定时运行，无法持续接收消息
- 缺少 Bot 服务器来处理用户命令

**解决方案**：
创建独立的 Telegram Bot 服务器来持续运行

**实现**：

#### 1. 创建 Bot 服务器脚本
- `scripts/telegram_bot_server.py` - Bot 服务器主程序
- 支持长轮询模式（需要 python-telegram-bot）
- 支持简单轮询模式（备用方案）

#### 2. 创建启动脚本
- `scripts/start_bot.sh` - 快速启动脚本
- 自动检查环境和依赖
- 友好的提示信息

#### 3. 创建使用文档
- `TELEGRAM_BOT_SETUP.md` - 详细的设置指南
- 包含本地运行、服务器运行、Docker 部署等方案

**使用方法**：

##### 方案 A：本地运行（测试）
```bash
# 设置环境变量
export TELEGRAM_BOT_TOKEN='your_bot_token'

# 启动 Bot
./scripts/start_bot.sh

# 或直接运行
python3 scripts/telegram_bot_server.py
```

##### 方案 B：服务器运行（生产）
```bash
# 使用 systemd
sudo systemctl start btc-momentum-bot

# 使用 Docker
docker start btc-bot

# 使用 screen
screen -S btc-bot
python3 scripts/telegram_bot_server.py
```

---

## 架构说明

### 修复前的架构

```
GitHub Actions (定时运行)
  ↓
运行分析
  ↓
推送到 Telegram/飞书
  ↓
❌ 无法接收用户命令
```

### 修复后的架构

```
┌─────────────────────────────────────┐
│  GitHub Actions (定时运行)          │
│  • 运行分析                         │
│  • 读取订阅数据库                   │
│  • 推送消息                         │
└─────────────────────────────────────┘
                 ↕
         共享数据库文件
         data/subscriptions.db
                 ↕
┌─────────────────────────────────────┐
│  Telegram Bot 服务器 (持续运行)     │
│  • 接收用户命令                     │
│  • 更新订阅数据库                   │
│  • 响应确认                         │
└─────────────────────────────────────┘
```

**关键点**：
- GitHub Actions 负责运行分析和推送
- Bot 服务器负责接收命令和管理订阅
- 两者通过共享的 SQLite 数据库通信

---

## 快速修复指南

### 修复飞书价格显示

1. 拉取最新代码
   ```bash
   git pull origin main
   ```

2. 更新已部署的代码（如果使用 GitHub Actions）
   - 代码已自动推送，下次运行会生效

3. 验证修复
   - 触发一次 GitHub Actions
   - 检查飞书消息是否显示价格

### 启动 Telegram Bot 服务器

#### 方法 1：快速启动（推荐）

```bash
# 1. 设置环境变量
export TELEGRAM_BOT_TOKEN='your_bot_token'

# 2. 运行启动脚本
./scripts/start_bot.sh
```

#### 方法 2：直接运行

```bash
python3 scripts/telegram_bot_server.py
```

#### 方法 3：后台运行

```bash
# 使用 screen
screen -S btc-bot
./scripts/start_bot.sh
# 按 Ctrl+A, D 分离

# 使用 nohup
nohup ./scripts/start_bot.sh > bot.log 2>&1 &
```

---

## 测试检查清单

### 飞书价格显示测试

- [ ] 触发 GitHub Actions 运行
- [ ] 等待分析完成
- [ ] 检查飞书消息是否显示价格
- [ ] 确认价格信息正确（币种、价格、涨跌幅）

### Telegram Bot 命令测试

#### 基础功能
- [ ] 启动 Bot 服务器
- [ ] 在 Telegram 中发送 `/start`
- [ ] 检查是否收到欢迎消息
- [ ] 发送 `/help` 查看命令列表

#### 订阅功能
- [ ] 发送 `/subscribe 1d 4h`
- [ ] 检查是否成功订阅
- [ ] 发送 `/mysubscriptions`
- [ ] 确认订阅信息正确

#### 币种功能
- [ ] 发送 `/list_currencies`
- [ ] 发送 `/subscribe_currency btc eth`
- [ ] 发送 `/my_currencies`
- [ ] 确认币种订阅正确

---

## 常见问题

### Q1: Bot 启动后立即退出

**检查**：
```bash
# 查看错误信息
python3 scripts/telegram_bot_server.py
```

**可能原因**：
1. Bot Token 错误
2. 数据库文件不存在
3. 依赖未安装

**解决**：
```bash
# 1. 验证 Bot Token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# 2. 初始化数据库
python3 scripts/init_subscription_db.py

# 3. 安装依赖
pip install -r requirements.txt
```

### Q2: Bot 收到命令但没有响应

**检查日志**：
```bash
# 查看控制台输出或日志文件
tail -f bot.log
```

**可能原因**：
1. 命令格式错误
2. 数据库写入失败
3. 网络问题

**解决**：
```bash
# 测试数据库权限
sqlite3 data/subscriptions.db "SELECT * FROM subscriptions;"

# 测试命令解析
python3 -c "
from src.command_parser import CommandParser
parser = CommandParser()
result = parser.parse_command('/subscribe 1d')
print(result)
"
```

### Q3: GitHub Actions 没有读取到订阅

**检查**：
1. 确认 Bot 服务器正在运行
2. 在 Telegram 中修改订阅
3. 检查数据库文件是否更新

**验证**：
```bash
# 查看数据库修改时间
ls -lh data/subscriptions.db

# 查看订阅数据
sqlite3 data/subscriptions.db "SELECT * FROM subscriptions;"
```

---

## 相关文档

- **TELEGRAM_BOT_SETUP.md** - Bot 服务器详细设置指南
- **DEPLOYMENT.md** - 部署配置说明
- **SUBSCRIPTION_GUIDE.md** - 订阅功能使用指南

---

## 更新日志

### 2026-01-27

- ✅ 修复飞书机器人价格显示问题
- ✅ 创建 Telegram Bot 服务器
- ✅ 添加 Bot 服务器启动脚本
- ✅ 完善文档和测试指南

### 提交记录

- `e65c2c9` - feat: 添加 Bot 服务器快速启动脚本
- `309a1da` - fix: 修复飞书价格显示并添加 Telegram Bot 服务器
- `12e03e8` - feat: 添加部署验证脚本

---

**状态**：✅ 所有问题已修复并部署

**最后更新**：2026-01-27
