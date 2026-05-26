# HASN 记忆系统数据库迁移报告

## 执行时间
2026-05-26

## 迁移内容

### 创建的表

本次迁移成功创建了 HASN 记忆系统的 5 个核心表：

#### 1. memory_namespace_revisions
- **用途**: 命名空间 revision 权威表
- **主键**: (sync_scope_kind, sync_scope_id, namespace)
- **说明**: 用于记忆同步的版本控制，支持 owner 和 agent 两种同步分区

#### 2. episodic_turns
- **用途**: 原始对话 turn + embedding
- **主键**: turn_id
- **说明**: 存储会话中的每一轮对话，包含 embedding 向量用于语义检索

#### 3. semantic_facts
- **用途**: 语义事实
- **主键**: fact_id
- **说明**: 存储从对话中提取的结构化事实，支持四主体（owner/agent_self/peer/world）

#### 4. memory_events
- **用途**: 时序事件
- **主键**: event_id
- **说明**: 存储时间序列事件，用于记录重要的交互历史

#### 5. memory_extraction_jobs
- **用途**: 提取任务
- **主键**: job_id
- **说明**: 管理记忆提取流水线的任务队列

## 表大小

| 表名 | 大小 |
|------|------|
| episodic_turns | 48 kB |
| memory_events | 48 kB |
| memory_extraction_jobs | 24 kB |
| memory_namespace_revisions | 16 kB |
| semantic_facts | 40 kB |

## 索引

每个表都创建了相应的索引以优化查询性能：

- **memory_namespace_revisions**: 按 (sync_scope_kind, sync_scope_id, updated_at) 索引
- **episodic_turns**: 按会话、Agent、Owner、话题分片索引
- **semantic_facts**: 按 owner/agent 维度、作用域、状态索引
- **memory_events**: 按 owner/agent 维度、事件类型、作用域索引
- **memory_extraction_jobs**: 按状态和调度时间索引

## 约束

所有表都包含适当的 CHECK 约束：

- **subject_kind**: 限制为 'owner', 'agent_self', 'peer', 'world'
- **memory_layer**: 限制为 'semantic', 'episodic' 等
- **scope_kind**: 限制为 'global', 'workspace', 'project', 'task', 'conversation', 'topic'
- **status**: 各表有不同的状态值约束

## 字段规范

- **时间字段**: 使用 `created_time`/`updated_time` (timestamptz) 和 `created_at`/`updated_at` (bigint epoch ms)
- **ID 字段**: 使用 varchar(40) 存储 ULID
- **JSON 字段**: 使用 text 类型存储 JSON 字符串
- **Embedding**: 使用 bytea 存储向量数据

## 验证结果

✅ 所有表创建成功
✅ 所有索引创建成功
✅ 所有约束创建成功
✅ 所有注释添加成功

## 后续步骤

1. **代码生成**: 使用 `fba codegen` 工具为这些表生成 model/schema/crud/service/api 代码
2. **测试**: 编写单元测试和集成测试
3. **文档**: 更新 API 文档
4. **监控**: 添加表大小和查询性能监控

## 回滚方法

如需回滚此迁移，执行以下 SQL：

```sql
DROP TABLE IF EXISTS "public"."memory_extraction_jobs";
DROP TABLE IF EXISTS "public"."memory_events";
DROP TABLE IF EXISTS "public"."semantic_facts";
DROP TABLE IF EXISTS "public"."episodic_turns";
DROP TABLE IF EXISTS "public"."memory_namespace_revisions";
```

## 相关文档

- 设计文档: `docs/hasn-node设计文档/02-记忆与知识库/04-记忆数据结构与存储.md`
- 迁移 SQL: `backend/sql/migrations/2026-05-26-memory-system-tables.sql`
- 执行脚本: `backend/sql/migrations/run_migration.py`

## 注意事项

1. 这些表目前为空表，需要通过记忆提取流水线填充数据
2. Embedding 字段目前使用 bytea 类型，后续可能需要迁移到 pgvector 扩展
3. 表结构遵循 PostgreSQL 语法，与本地 SQLite 有差异（类型映射）
4. 所有表都支持幂等创建（使用 IF NOT EXISTS）

## 问题排查

如果后端仍然报错 `relation "public.memory_namespace_revisions" does not exist`，请检查：

1. 数据库连接配置是否正确
2. 是否连接到正确的数据库（huanxing）
3. 表是否在 public schema 下
4. 应用是否需要重启以刷新连接池

可以使用以下 SQL 验证表是否存在：

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'memory_%' OR table_name LIKE '%_turns' OR table_name LIKE 'semantic_%';
```
