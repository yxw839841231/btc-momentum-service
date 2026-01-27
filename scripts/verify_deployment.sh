#!/bin/bash
# 部署验证脚本
# 用于验证订阅管理功能和 GitHub Actions 配置是否正常

set -e

echo "================================================"
echo "  BTC 动能分析服务 - 部署验证"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. 检查文件结构
echo "1. 检查文件结构..."
echo "   正在检查核心文件..."

files=(
    "src/subscription_manager.py"
    "src/command_parser.py"
    "src/currency_config.py"
    "scripts/init_subscription_db.py"
    "scripts/test_subscription.py"
    ".github/workflows/scheduled-analysis.yml"
    "DEPLOYMENT.md"
    "SUBSCRIPTION_GUIDE.md"
)

all_files_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        check_pass "文件存在: $file"
    else
        check_fail "文件缺失: $file"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = true ]; then
    check_pass "所有核心文件完整"
else
    check_fail "部分文件缺失"
    exit 1
fi

echo ""

# 2. 检查数据库
echo "2. 检查订阅数据库..."
if [ -f "data/subscriptions.db" ]; then
    size=$(ls -lh data/subscriptions.db | awk '{print $5}')
    check_pass "数据库文件存在 (大小: $size)"

    # 检查数据库表
    if python3 -c "import sqlite3; conn = sqlite3.connect('data/subscriptions.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); tables = cursor.fetchall(); conn.close(); exit(0 if len(tables) >= 3 else 1)" 2>/dev/null; then
        check_pass "数据库表结构完整"
    else
        check_fail "数据库表结构异常"
    fi
else
    check_warn "数据库文件不存在，将自动创建"
fi

echo ""

# 3. 检查 Python 依赖
echo "3. 检查 Python 依赖..."
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    python_version=$(python3 --version)
    check_pass "Python 版本: $python_version"
else
    check_fail "Python 版本过低（需要 >= 3.8）"
    exit 1
fi

# 检查关键依赖
dependencies=("requests" "sqlite3")
for dep in "${dependencies[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        check_pass "依赖已安装: $dep"
    else
        check_fail "依赖缺失: $dep"
    fi
done

echo ""

# 4. 运行单元测试
echo "4. 运行功能测试..."
if python3 scripts/test_subscription.py > /dev/null 2>&1; then
    check_pass "订阅管理功能测试通过"
else
    check_fail "订阅管理功能测试失败"
fi

echo ""

# 5. 检查 Git 配置
echo "5. 检查 Git 配置..."
if git remote get-url origin > /dev/null 2>&1; then
    remote_url=$(git remote get-url origin)
    check_pass "Git 远程仓库: $remote_url"
else
    check_fail "未配置 Git 远程仓库"
fi

echo ""

# 6. 环境变量检查
echo "6. 检查环境变量..."
env_vars=(
    "TELEGRAM_BOT_TOKEN"
    "TELEGRAM_CHAT_ID"
    "FEISHU_WEBHOOK_URL"
)

missing_vars=0
for var in "${env_vars[@]}"; do
    if [ -z "${!var}" ]; then
        check_warn "环境变量未设置: $var"
        missing_vars=$((missing_vars + 1))
    else
        check_pass "环境变量已设置: $var"
    fi
done

if [ $missing_vars -eq 3 ]; then
    check_warn "未配置任何消息推送平台"
elif [ $missing_vars -gt 0 ]; then
    check_warn "部分环境变量未设置"
else
    check_pass "所有环境变量已配置"
fi

echo ""

# 7. GitHub Actions 检查
echo "7. 检查 GitHub Actions 配置..."
if grep -q "初始化订阅数据库" .github/workflows/scheduled-analysis.yml 2>/dev/null; then
    check_pass "数据库初始化步骤已配置"
else
    check_fail "数据库初始化步骤未配置"
fi

if grep -q "提交订阅数据库到仓库" .github/workflows/scheduled-analysis.yml 2>/dev/null; then
    check_pass "数据库自动提交步骤已配置"
else
    check_fail "数据库自动提交步骤未配置"
fi

echo ""

# 8. .gitignore 配置
echo "8. 检查 .gitignore 配置..."
if grep -q "data/test_*.db" .gitignore 2>/dev/null; then
    check_pass "测试数据库已配置为忽略"
else
    check_warn "测试数据库未配置忽略"
fi

echo ""

# 总结
echo "================================================"
echo "  验证总结"
echo "================================================"
echo ""

# 检查是否有失败的检查
if [ $missing_vars -eq 0 ] && [ "$all_files_exist" = true ]; then
    echo -e "${GREEN}🎉 所有检查通过！系统已准备就绪。${NC}"
    echo ""
    echo "下一步："
    echo "  1. 测试 Telegram Bot 命令"
    echo "  2. 在 GitHub Actions 中手动触发 workflow"
    echo "  3. 验证数据库自动提交功能"
else
    echo -e "${YELLOW}⚠️  部分检查未通过，请查看上述详情。${NC}"
    echo ""
    echo "建议："
    if [ $missing_vars -gt 0 ]; then
        echo "  • 设置环境变量（GitHub Secrets 或本地 .env）"
    fi
    if [ "$all_files_exist" = false ]; then
        echo "  • 确保所有文件已正确部署"
    fi
fi

echo ""
echo "详细文档："
echo "  • 部署指南: DEPLOYMENT.md"
echo "  • 订阅指南: SUBSCRIPTION_GUIDE.md"
echo ""
