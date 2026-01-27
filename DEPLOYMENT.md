# GitHub Actions 部署配置说明

## 数据库持久化方案

### 方案概述

本项目使用**方案 A：将数据库提交到 Git 仓库**来实现数据持久化。

**优点**：
- ✅ 实现简单，无需额外配置
- ✅ 数据版本可追溯
- ✅ 自动备份到 GitHub
- ✅ 适合小规模使用（订阅数据库通常 < 1MB）

**工作原理**：
1. GitHub Actions 每次运行时自动初始化数据库（如果不存在）
2. 分析完成后自动提交数据库更新
3. 使用 `[skip ci]` 标记避免触发新的 workflow

### 配置细节

#### GitHub Actions 工作流

在 `.github/workflows/scheduled-analysis.yml` 中添加了两个关键步骤：

**1. 数据库初始化**
```yaml
- name: 初始化订阅数据库
  run: |
    if [ ! -f data/subscriptions.db ]; then
      echo "数据库不存在，初始化数据库..."
      python scripts/init_subscription_db.py
    else
      echo "数据库已存在，跳过初始化"
    fi
```

**2. 数据库自动提交**
```yaml
- name: 提交订阅数据库到仓库
  if: success() && always()
  run: |
    # 配置 git
    git config --local user.email "github-actions[bot]@users.noreply.github.com"
    git config --local user.name "github-actions[bot]"

    # 检查数据库是否有变化
    if [ -f data/subscriptions.db ]; then
      git add data/subscriptions.db

      # 检查是否有新的更改
      if git diff --cached --quiet; then
        echo "数据库无变化，跳过提交"
      else
        echo "数据库有更新，提交更改..."
        git commit -m "chore: 更新订阅数据库 [skip ci]"
        git push
        echo "✅ 数据库已提交到仓库"
      fi
    else
      echo "⚠️ 数据库文件不存在"
    fi
```

#### Git 忽略配置

在 `.gitignore` 中配置：
```
# 忽略测试数据库
data/test_*.db

# 保留生产数据库（已注释，表示需要提交）
# data/subscriptions.db
```

## 部署步骤

### 1. 首次部署

**步骤 1：初始化本地数据库**
```bash
cd btc-momentum-service
python scripts/init_subscription_db.py
```

**步骤 2：提交到 GitHub**
```bash
git add data/subscriptions.db
git commit -m "chore: 初始化订阅数据库"
git push origin main
```

**步骤 3：验证 GitHub Actions**
1. 进入 GitHub 仓库的 Actions 页面
2. 手动触发 workflow 运行
3. 检查日志确保成功

### 2. 验证部署

**检查清单**：

- [ ] 数据库文件已提交到仓库
- [ ] GitHub Actions 成功运行
- [ ] 数据库自动提交功能正常
- [ ] Telegram Bot 命令响应正常

### 3. 测试订阅功能

在 Telegram 中测试：

```
/start                      # 启动 Bot
/help                       # 查看帮助
/subscribe 1d 4h           # 订阅时间级别
/mysubscriptions           # 查看订阅
```

然后查看 GitHub 仓库，确认 `data/subscriptions.db` 文件已更新。

## 工作流程

### 正常运行流程

```
1. GitHub Actions 触发
   ↓
2. 拉取最新代码（包括数据库）
   ↓
3. 检查数据库是否存在
   ├─ 存在 → 跳过初始化
   └─ 不存在 → 初始化数据库
   ↓
4. 运行分析（可能更新数据库）
   ↓
5. 部署到 GitHub Pages
   ↓
6. 提交数据库更新（如果有变化）
   ↓
7. 完成
```

### 数据库更新时机

数据库会在以下情况下更新：
- 用户通过 Telegram Bot 修改订阅
- 用户订阅新的币种或时间级别
- 用户修改推送频率设置

### [skip ci] 的作用

提交信息中的 `[skip ci]` 标记告诉 GitHub：
- **不要**因为这个提交而触发新的 workflow
- 避免无限循环：提交 → 触发 → 提交 → 触发...

## 监控和维护

### 查看数据库更新

```bash
# 查看最近的数据库提交
git log --oneline -- data/subscriptions.db

# 查看数据库大小
ls -lh data/subscriptions.db

# 查看数据库内容（使用 SQLite 工具）
sqlite3 data/subscriptions.db "SELECT * FROM subscriptions;"
```

### 数据库备份

数据库会自动随每次更新备份到 GitHub，但你也可以手动备份：

```bash
# 导出数据库
cp data/subscriptions.db data/subscriptions.db.backup

# 或使用 SQLite 导出 SQL
sqlite3 data/subscriptions.db .dump > backup.sql
```

### 清理历史提交

如果数据库文件变大导致仓库臃肿，可以考虑：

**方案 A：使用 git-filter-rebe**
```bash
# 需要谨慎操作，建议先备份
git filter-repo --path data/subscriptions.db --invert-paths
```

**方案 B：迁移到 Artifacts（推荐用于大规模）**

当订阅用户超过 1000 个时，考虑迁移到 GitHub Actions Artifacts。

## 故障排查

### 问题 1：数据库文件未提交

**症状**：Actions 显示"数据库无变化，跳过提交"

**原因**：
- 数据库确实没有变化（正常）
- 或者没有新的订阅操作

**解决**：
- 这是正常的，无需处理
- 或者手动测试订阅命令触发更新

### 问题 2：数据库提交失败

**症状**：Actions 日志显示 git push 失败

**原因**：
- 权限问题
- 分支保护规则

**解决**：
1. 检查仓库设置 → Actions → General → Workflow permissions
2. 确保选择了 "Read and write permissions"
3. 如果有分支保护，需要调整规则

### 问题 3：数据库被覆盖

**症状**：订阅丢失或重置

**原因**：
- 多次提交冲突
- 手动覆盖了数据库

**解决**：
1. 查看提交历史：`git log -- data/subscriptions.db`
2. 恢复到正确的版本：`git checkout <commit> -- data/subscriptions.db`

### 问题 4：数据库锁定

**症状**：SQLite 数据库锁定错误

**原因**：
- 多个进程同时访问数据库

**解决**：
- SQLite 支持并发读，但写操作会锁定
- GitHub Actions 中通常不会出现此问题
- 如果出现，添加重试逻辑

## 性能考虑

### 数据库大小

- **空数据库**：~20 KB
- **100 个订阅用户**：~50 KB
- **1000 个订阅用户**：~200 KB
- **10000 个订阅用户**：~1-2 MB

### 提交频率

- **无订阅变化**：不会提交（正常）
- **有订阅变化**：每次 Actions 运行后提交
- **建议**：可以接受，因为数据库很小

### 网络流量

- 每次 push：~20-200 KB（取决于订阅数量）
- 每次 pull：~20-200 KB
- **结论**：对 GitHub 流量影响微乎其微

## 安全建议

### 数据库访问控制

1. **仓库设置为私有**（如果包含敏感信息）
2. **定期审查订阅列表**
3. **监控异常订阅活动**

### 数据库加密

如果需要加密订阅数据：

```python
# 使用 SQLCipher
# pip install pysqlcipher3
```

但通常不需要，因为订阅数据本身不包含敏感信息。

## 迁移指南

### 从方案 A 迁移到方案 B（Artifacts）

当订阅用户超过 1000 个时：

**步骤 1：修改 workflow**
```yaml
- name: 下载上次的数据库
  uses: actions/download-artifact@v4
  with:
    name: subscription-database
    path: data/

- name: 运行分析...

- name: 上传数据库
  uses: actions/upload-artifact@v4
  with:
    name: subscription-database
    path: data/subscriptions.db
    retention-days: 90
```

**步骤 2：更新 .gitignore**
```gitignore
# 忽略生产数据库
data/subscriptions.db
```

**步骤 3：移除已提交的数据库**
```bash
git rm --cached data/subscriptions.db
git commit -m "chore: 停止追踪数据库文件"
```

## 总结

当前配置适合：
- ✅ 小到中等规模（< 1000 用户）
- ✅ 不需要额外配置
- ✅ 自动版本控制
- ✅ 简单可靠

未来如果需要：
- 🔄 迁移到 Artifacts（大规模用户）
- 🔄 使用外部数据库（PostgreSQL, MySQL）
- 🔄 实现 Web 管理界面

---

**部署完成！** 🎉

如有问题，请查看 GitHub Actions 日志或提交 Issue。
