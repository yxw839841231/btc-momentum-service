# 🚀 部署指南 - BTC 动能分析服务

## ✅ 已完成的工作

1. ✅ **项目结构创建完成**
2. ✅ **核心模块实现**
   - 分析引擎 (`src/analyzer.py`)
   - Telegram Bot (`src/telegram_bot.py`)
   - 报告生成器 (`src/report_generator.py`)

3. ✅ **GitHub Actions 配置完成**
   - 定时任务：每小时执行
   - 自动推送到 Telegram
   - 部署到 GitHub Pages

4. ✅ **Git 仓库初始化**
   - 首次提交已完成
   - 分支已重命名为 `main`

5. ✅ **测试报告生成**
   - HTML 报告模板已验证
   - 报告位于: `reports/btc_analysis_20260127_115211.html`

## 📋 部署步骤

### 第一步：创建 GitHub 仓库

1. **在 GitHub 上创建新仓库**
   - 访问：https://github.com/new
   - 仓库名称：`btc-momentum-service`
   - 设置为 **Public**（公开仓库才能使用免费的 GitHub Actions）
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

2. **推送代码到 GitHub**
   ```bash
   # 替换 YOUR_USERNAME 为你的 GitHub 用户名
   git remote add origin https://github.com/YOUR_USERNAME/btc-momentum-service.git
   git push -u origin main
   ```

### 第二步：配置 GitHub Secrets

1. **进入仓库设置**
   - 打开你的 GitHub 仓库
   - 点击 **Settings** 标签
   - 左侧菜单找到 **Secrets and variables** → **Actions**
   - 点击 **New repository secret**

2. **添加以下 Secrets**：

   **Secret 1: TELEGRAM_BOT_TOKEN**
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: `8267482118:AAGO0VKp2Z1M_Ctf8V9N1a1uo_AUp5grohs`
   - 点击 "Add secret"

   **Secret 2: TELEGRAM_CHAT_ID**
   - Name: `TELEGRAM_CHAT_ID`
   - Value: `8462071116`
   - 点击 "Add secret"

### 第三步：启用 GitHub Pages

1. **配置 Pages**
   - 进入 **Settings** → **Pages**
   - Source 选择: **GitHub Actions**
   - 点击 "Save"

2. **更新配置文件**（重要！）

   编辑 `scripts/run_analysis.py` 第 43 行：

   ```python
   # 原来的代码
   report_url = f"https://username.github.io/btc-momentum-service/reports/{report_filename}"

   # 修改为（替换 YOUR_USERNAME）
   report_url = f"https://YOUR_USERNAME.github.io/btc-momentum-service/reports/{report_filename}"
   ```

   提交更改：
   ```bash
   git add scripts/run_analysis.py
   git commit -m "Update GitHub Pages URL"
   git push
   ```

### 第四步：测试 GitHub Actions

1. **手动触发 Workflow**
   - 进入仓库的 **Actions** 标签
   - 左侧选择 "BTC Momentum Analysis"
   - 点击 "Run workflow" 按钮
   - 点击绿色的 "Run workflow" 确认

2. **查看执行日志**
   - 点击正在运行的任务查看日志
   - 确保所有步骤都成功
   - 如果失败，查看错误信息

3. **验证 Telegram 推送**
   - 检查 Telegram 是否收到消息
   - 如果收到，说明配置成功！

### 第五步：确认定时任务

GitHub Actions 会在每小时（UTC 时间）自动运行。你可以：

1. **查看运行历史**
   - Actions → BTC Momentum Analysis
   - 查看所有的运行记录

2. **调整执行时间**（可选）
   编辑 `.github/workflows/scheduled-analysis.yml`：

   ```yaml
   schedule:
     - cron: '0 * * * *'  # 每小时（UTC）
   ```

   常用表达式：
   - `0 */4 * * *` - 每4小时
   - `0 8,20 * * *` - 每天 8:00 和 20:00 UTC
   - `0 0 * * 1` - 每周一 0:00 UTC

   **注意**：北京时间 = UTC + 8

## 🔍 验证清单

部署完成后，请确认以下项目：

- [ ] 代码已成功推送到 GitHub
- [ ] GitHub Secrets 已正确配置（2个）
- [ ] GitHub Pages 已启用（Source: GitHub Actions）
- [ ] GitHub Actions 手动运行成功
- [ ] Telegram 收到测试消息
- [ ] GitHub Pages 报告可以访问

## 📱 Telegram Bot 使用

部署成功后，你可以：

1. **接收自动推送**
   - 每小时自动收到分析摘要
   - 关键信号实时告警（开发中）

2. **手动命令**（开发中）
   - `/analyze` - 立即获取最新分析
   - `/subscribe` - 订阅特定时间级别
   - `/help` - 查看帮助

## 🛠️ 故障排查

### 问题 1: GitHub Actions 失败

**可能原因**：
- Secrets 未正确配置
- 依赖安装失败
- 网络问题

**解决方案**：
1. 检查 Actions 日志
2. 确认 Secrets 名称和值正确
3. 确保仓库是 Public 的

### 问题 2: Telegram 没有收到消息

**可能原因**：
- Bot Token 错误
- Chat ID 错误
- Bot 未启动

**解决方案**：
1. 在 Telegram 中搜索你的 Bot，发送 `/start` 命令
2. 确认 Chat ID 正确（可以通过 @userinfobot 获取）
3. 检查 GitHub Actions 日志中的错误信息

### 问题 3: GitHub Pages 报告 404

**可能原因**：
- Pages 未启用或配置错误
- URL 配置错误
- 文件未正确部署

**解决方案**：
1. 确认 Pages 设置：Source 为 GitHub Actions
2. 检查 `scripts/run_analysis.py` 中的 URL
3. 等待几分钟让 GitHub Pages 同步

## 📊 查看报告

报告会自动发布到：
```
https://YOUR_USERNAME.github.io/btc-momentum-service/reports/
```

每次分析会生成一个新的 HTML 文件，文件名包含时间戳：
```
btc_analysis_20260127_1600.html
```

## 🎯 下一步优化

部署完成后，你可以：

1. **完善动能理论分析**
   - 实现完整的分析逻辑
   - 添加背离检测算法
   - 实现单位周期判断

2. **增强功能**
   - 添加实时告警系统
   - 实现用户订阅管理
   - 添加交互式图表

3. **优化性能**
   - 添加数据缓存
   - 并行数据获取
   - 错误处理完善

## 💡 提示

- GitHub Actions 有免费额度限制：每月 2000 分钟
- Public 仓库无限制
- Telegram API 没有调用限制
- 建议定时任务不要太频繁（最少 5 分钟间隔）

---

**祝你部署顺利！** 🎉

如有问题，请查看 GitHub Actions 日志或提交 Issue。
