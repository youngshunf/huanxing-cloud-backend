#!/bin/bash

# =====================================================
# HASN 记忆系统数据库迁移执行脚本
# =====================================================

set -e

# 数据库连接配置
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-15432}"
DB_NAME="${DB_NAME:-huanxing}"
DB_USER="${DB_USER:-postgres}"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}HASN 记忆系统数据库迁移${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "数据库配置:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# 检查 psql 是否可用
if ! command -v psql &> /dev/null; then
    echo -e "${RED}错误: psql 命令未找到，请安装 PostgreSQL 客户端${NC}"
    exit 1
fi

# 执行迁移
MIGRATION_FILE="2026-05-26-memory-system-tables.sql"

echo -e "${YELLOW}执行迁移: $MIGRATION_FILE${NC}"
echo ""

if PGPASSWORD="${DB_PASSWORD}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"; then
    echo ""
    echo -e "${GREEN}✓ 迁移执行成功！${NC}"
    echo ""

    # 验证表是否创建成功
    echo -e "${YELLOW}验证表创建...${NC}"
    PGPASSWORD="${DB_PASSWORD}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
        SELECT
            table_name,
            pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN (
            'memory_namespace_revisions',
            'episodic_turns',
            'semantic_facts',
            'memory_events',
            'memory_extraction_jobs'
        )
        ORDER BY table_name;
    "

    echo ""
    echo -e "${GREEN}✓ 所有表创建成功！${NC}"
else
    echo ""
    echo -e "${RED}✗ 迁移执行失败${NC}"
    exit 1
fi
