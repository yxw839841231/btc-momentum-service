# BTC 动能分析服务

基于自定义动能理论的 BTC 多时间级别分析服务，支持定时分析、Telegram 推送和 Web 报告查看。

## 功能特性

- ✅ **多时间级别分析**：8个时间级别（2d/1d/12h/6h/4h/2h/1h/30m）
- ✅ **动能理论分析**：线段分类、背离检测、单位周期判断
- ✅ **自动推送**：每小时推送到 Telegram
- ✅ **Web 报告**：美观的 HTML 报告托管在 GitHub Pages
- ✅ **零成本部署**：基于 GitHub Actions，完全免费
- ✅ **实时告警**：检测到关键信号立即通知（开发中）

## 项目结构

```
btc-momentum-service/
├── .github/
│   └── workflows/
│       └── scheduled-analysis.yml    # GitHub Actions 配置
├── scripts/
│   ├── fetch_btc_data.py             # 获取 BTC 数据
│   ├── calculate_indicators.py       # 计算技术指标
│   ├── generate_chart_html.py        # 生成图表
│   ├── database_manager.py           # 数据库管理
│   └── run_analysis.py               # 主分析脚本
├── src/
│   ├── __init__.py
│   ├── analyzer.py                   # 分析引擎
│   ├── telegram_bot.py               # Telegram Bot
│   └── report_generator.py           # 报告生成器
├── templates/                         # HTML 模板（待添加）
├── reports/                           # HTML 报告输出
├── data/                              # 数据缓存目录
├── logs/                              # 日志目录
├── config.yaml                        # 配置文件
├── requirements.txt                   # Python 依赖
└── README.md                          # 本文档
```

## 快速开始

### 1. 准备工作

#### 获取 Telegram Bot Token

1. 在 Telegram 中搜索 [@BotFather](https://t.me/botfather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称
4. 保存返回的 Bot Token（格式：`123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`）

#### 获取 Chat ID

1. 在 Telegram 中搜索 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息
3. 保存返回的 Chat ID（数字）

### 2. 本地测试

```bash
# 克隆项目
cd btc-momentum-service

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id'

# 运行分析
python scripts/run_analysis.py
```

### 3. 部署到 GitHub

#### 步骤 1：创建 GitHub 仓库并推送代码

```bash
# 初始化 git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: BTC momentum analysis service"

# 推送到 GitHub
git branch -M main
git remote add origin https://github.com/USERNAME/btc-momentum-service.git
git push -u origin main
```

#### 步骤 2：配置 GitHub Secrets

1. 打开 GitHub 仓库页面
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 添加以下 Secrets：
   - `TELEGRAM_BOT_TOKEN`: 你的 Bot Token
   - `TELEGRAM_CHAT_ID`: 你的 Chat ID

#### 步骤 3：启用 GitHub Pages

1. 进入 **Settings** → **Pages**
2. Source 选择：`GitHub Actions`
3. 保存设置

#### 步骤 4：测试 GitHub Actions

1. 进入 **Actions** 标签页
2. 选择 "BTC Momentum Analysis" workflow
3. 点击 "Run workflow" 按钮手动触发
4. 查看执行日志，确保成功

#### 步骤 5：验证定时任务

GitHub Actions 会在每小时（UTC 时间）自动运行分析任务。你可以：
- 在 Actions 页面查看运行历史
- 在 Telegram 接收推送消息
- 通过 GitHub Pages 查看报告

### 4. 更新 GitHub Pages URL

编辑 `scripts/run_analysis.py`，将以下行：

```python
report_url = f"https://username.github.io/btc-momentum-service/reports/{report_filename}"
```

替换为你的实际 GitHub Pages URL：

```python
report_url = f"https://YOUR_USERNAME.github.io/btc-momentum-service/reports/{report_filename}"
```

## 配置说明

### config.yaml

```yaml
# Telegram Bot 配置
telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  default_chat_id: "${TELEGRAM_CHAT_ID}"

# 数据获取配置
data:
  symbol: "BTC-USDT"
  exchange: "okx"
  timeframes: ["2d", "1d", "12h", "6h", "4h", "2h", "1h", "30m"]
  limit: 200

# 调度配置
scheduler:
  timezone: "UTC"
  cron_expression: "0 * * * *"  # 每小时
```

### GitHub Actions 定时

修改 `.github/workflows/scheduled-analysis.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 * * * *'  # 每小时（UTC）
```

常用表达式：
- `0 */4 * * *` - 每4小时
- `0 8,20 * * *` - 每天 8:00 和 20:00
- `0 0 * * 1` - 每周一 0:00

**注意**：GitHub Actions 的最小间隔是 5 分钟，且使用 UTC 时间。

## 功能说明

### 动能理论分析

本项目实现了基于 MACD 的多时间级别动能分析理论：

1. **线段分类**
   - 上涨线段（DEA > 0）
   - 下跌线段（DEA < 0）
   - 过渡期

2. **背离检测**
   - 连续跳空背离
   - 黄白线背离（DIF vs DEA）

3. **单位调整周期**
   - 识别当前处于第几个调整周期

4. **分立调控**
   - 检测离散的动能调整模式

5. **多时间级别联动**
   - 上级对下级的影响分析
   - 多周期共振确认

### Telegram 消息格式

```
📊 BTC 动能分析

时间: 2025-01-27 16:00:00

【大周期】2日线 ↑ 1日线 ↑
【中周期】12h ⚠️  6h 调整 4h ↓
【小周期】2h ↓ 1h ↓ 30m ⟲

🔴 关键信号:
• 12h 出现顶背离
• 30m 柱状图收敛，可能反转

📈 完整报告: https://username.github.io/.../btc_analysis_20250127_1600.html

💡 操作建议: 观望
```

### Web 报告

HTML 报告包含：
- 8个时间级别的完整指标数据
- 交互式卡片展示
- 关键信号高亮
- 响应式设计（支持移动端）

## 开发计划

### ✅ 已完成

- [x] 项目结构搭建
- [x] 分析引擎框架
- [x] Telegram Bot 基础功能
- [x] HTML 报告生成
- [x] GitHub Actions 部署

### 🚧 开发中

- [ ] 完整的动能理论分析逻辑
- [ ] 实时告警系统
- [ ] 订阅管理功能

- [ ] 数据库持久化
- [ ] 交互式图表（ECharts）

### 📋 计划中

- [ ] Web API 接口
- [ ] 用户订阅管理
- [ ] 历史数据对比
- [ ] 性能优化

## 故障排查

### 问题 1：Telegram Bot 无响应

**解决方案**：
1. 检查 Bot Token 是否正确
2. 检查 Chat ID 是否正确
3. 确保 Bot 已启动（发送 /start 给 Bot）
4. 查看 GitHub Actions 日志

### 问题 2：GitHub Pages 报告 404

**解决方案**：
1. 确保 GitHub Pages 已启用
2. 检查 `run_analysis.py` 中的 URL 是否正确
3. 等待几分钟让 GitHub Pages 同步

### 问题 3：定时任务不执行

**解决方案**：
1. GitHub Actions 有最低 5 分钟间隔限制
2. 检查 cron 表达式是否正确（使用 UTC 时间）
3. 确保仓库有 commits（空的仓库不会触发定时任务）

## 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。加密货币交易有风险，投资需谨慎。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

---

**祝你使用愉快！** 🚀
