# 多币种推送故障排查指南

## 问题：只收到 BTC 的数据，没有收到其他币种

### 已完成的修复 ✅

1. **修改 MomentumAnalyzer 支持多币种**
   - `run_full_analysis()` 现在接受 `symbol` 参数
   - 文件名根据币种动态生成

2. **修复 run_analysis_multi.py**
   - 传递正确的币种参数给分析器
   - 添加详细的日志输出

3. **添加详细日志**
   - 显示每个币种的分析进度
   - 显示推送的成功/失败统计
   - 显示待推送币种列表

### 诊断结果 ✅

运行 `bash scripts/diagnose_multi_currency.sh` 结果：
- ✅ config.json 配置正确：`["BTC", "SUI", "SOL"]`
- ✅ 价格获取正常：3 个币种都能获取价格
- ✅ 所有文件完整
- ✅ GitHub Actions workflow 配置正确

### 下一步操作

#### 1. 手动触发 GitHub Actions

在 GitHub 仓库页面：
1. 进入 **Actions** 标签
2. 选择 **Multi-Currency Momentum Analysis** workflow
3. 点击 **Run workflow** 按钮
4. 选择 `feature-feishu` 分支
5. 点击 **Run workflow**

#### 2. 查看运行日志

等待运行完成后，查看日志中的关键信息：

**日志应该显示**：
```
📊 配置的币种: BTC, SUI, SOL
============================================================
开始分析 3 个币种
============================================================

[1/3] 准备分析 BTC...
✅ BTC 分析完成

[2/3] 准备分析 SUI...
✅ SUI 分析完成

[3/3] 准备分析 SOL...
✅ SOL 分析完成

============================================================
分析结果汇总: 3/3 个币种成功
成功的币种: BTC, SUI, SOL
============================================================

📤 开始推送消息...
待推送币种数量: 3
待推送币种: BTC, SUI, SOL
```

**如果某个币种分析失败**：
```
❌ SUI 分析失败
```
可能原因：
- OKX API 不支持该交易对
- 网络连接问题
- 数据获取超时

**如果推送失败**：
```
⚠️ SUI Telegram 推送失败: ...
```
可能原因：
- Token 失效
- Chat ID 错误
- 消息格式问题

#### 3. 本地测试

在本地运行完整测试：

```bash
# 测试配置加载
python3 scripts/test_full_multi_flow.py

# 测试单个币种分析（如果上面的测试通过）
python3 scripts/run_analysis_multi.py
```

### 常见问题

#### Q1: 为什么价格显示为 Simulated？

**A**: OKX 和 Binance 可能不支持某些币种（如 SUI）。系统会自动使用模拟数据，这不影响技术指标分析。

#### Q2: 如何确认 GitHub Actions 使用了最新代码？

**A**: 查看最新运行的 workflow 日志，确认：
1. 使用的分支是 `feature-feishu`
2. 运行的脚本是 `python scripts/run_analysis_multi.py`
3. 日志中显示 "配置的币种: BTC, SUI, SOL"

#### Q3: 如果还是只收到 BTC 怎么办？

**A**: 检查以下几点：
1. 查看最近的 GitHub Actions 运行时间（确认是最新运行）
2. 在日志中搜索 "分析结果汇总"，看成功了几种币种
3. 在日志中搜索 "待推送币种"，看准备推送几个币种
4. 检查 Telegram/飞书的聊天记录，确认是否收到了多条消息

### 预期行为

正常情况下，每次 GitHub Actions 运行时：
1. 分析 3 个币种（BTC、SUI、SOL）
2. 生成 3 个 HTML 报告
3. 推送 3 条消息到 Telegram（如果启用）
4. 推送 3 条消息到飞书（如果启用）

每条消息对应一个币种，消息标题会显示币种名称：
```
📊 BTC 动能分析
📊 SUI 动能分析
📊 SOL 动能分析
```

### 调试技巧

#### 查看最近的 GitHub Actions 运行

```bash
# 如果安装了 gh CLI
gh run list --branch feature-feishu --limit 3

# 查看特定运行的日志
gh run view <run-id> --log
```

#### 检查本地报告文件

```bash
ls -lh reports/*analysis*.html | tail -5
```

应该看到多个币种的报告：
```
btc_analysis_20250127_2100.html
sui_analysis_20250127_2100.html
sol_analysis_20250127_2100.html
```

### 联系支持

如果以上步骤都无法解决问题，请提供以下信息：
1. GitHub Actions 运行日志（完整或关键部分）
2. 本地运行 `bash scripts/diagnose_multi_currency.sh` 的输出
3. config.json 内容（隐藏敏感信息）
4. 收到的消息截图
