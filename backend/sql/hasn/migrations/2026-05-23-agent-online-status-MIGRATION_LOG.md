# Agent 在线状态管理 - 数据库迁移记录

## 迁移信息

- **迁移文件**: `backend/sql/hasn/migrations/2026-05-23-agent-online-status.sql`
- **执行时间**: 2026-05-23
- **执行状态**: ✅ 成功

## 迁移内容

### 新增字段

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `binding_node_id` | VARCHAR(64) | NULL | 当前绑定的 node ID（本地设备标识） |
| `binding_status` | VARCHAR(32) | 'unbound' | Binding 状态 (unbound/binding/bound/failed) |
| `online_status` | VARCHAR(32) | 'offline' | 在线状态 (offline/online) |
| `last_heartbeat_at` | TIMESTAMPTZ | NULL | 最后心跳时间（用于超时检测） |

### 新增索引

| 索引名 | 字段 | 说明 |
|--------|------|------|
| `idx_agents_online_status` | `online_status` | 优化在线状态查询 |
| `idx_agents_last_heartbeat` | `last_heartbeat_at` | 优化心跳超时检测 |
| `idx_agents_binding_node` | `binding_node_id` | 优化设备绑定查询（部分索引） |

## 验证结果

### 字段验证

```sql
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'hasn_agents'
AND column_name IN ('binding_node_id', 'binding_status', 'online_status', 'last_heartbeat_at')
ORDER BY column_name;
```

**结果**:
- ✅ binding_node_id: character varying (nullable: YES, default: NULL)
- ✅ binding_status: character varying (nullable: YES, default: 'unbound')
- ✅ online_status: character varying (nullable: YES, default: 'offline')
- ✅ last_heartbeat_at: timestamp with time zone (nullable: YES, default: NULL)

### 索引验证

```sql
SELECT indexname
FROM pg_indexes
WHERE tablename = 'hasn_agents'
AND indexname IN ('idx_agents_online_status', 'idx_agents_last_heartbeat', 'idx_agents_binding_node')
ORDER BY indexname;
```

**结果**:
- ✅ idx_agents_binding_node
- ✅ idx_agents_last_heartbeat
- ✅ idx_agents_online_status

### 数据验证

查询现有 agent 数据，确认字段已正确添加：

```sql
SELECT
    hasn_id,
    display_name,
    binding_node_id,
    binding_status,
    online_status,
    last_heartbeat_at
FROM hasn_agents
LIMIT 5;
```

**结果**: 所有现有 agent 的新字段都已正确初始化为默认值。

## 影响范围

### 受影响的表
- `hasn_agents` (主表)

### 受影响的代码
- Model: `backend/app/hasn/model/hasn_agents.py`
- Schema: `backend/app/hasn/schema/hasn_agents.py`
- Service: `backend/app/hasn/service/hasn_agents_service.py`
- API: `backend/app/hasn/api/v1/app/hasn_agents.py`
- Tasks: `backend/app/hasn/tasks.py`

### 向后兼容性
- ✅ 所有字段都是可空或有默认值，不影响现有数据
- ✅ 旧版本客户端不上报心跳时，字段保持默认值
- ✅ 新增索引不影响现有查询

## 回滚方案

如需回滚，执行以下 SQL：

```sql
-- 删除索引
DROP INDEX IF EXISTS idx_agents_online_status;
DROP INDEX IF EXISTS idx_agents_last_heartbeat;
DROP INDEX IF EXISTS idx_agents_binding_node;

-- 删除字段
ALTER TABLE hasn_agents DROP COLUMN IF EXISTS binding_node_id;
ALTER TABLE hasn_agents DROP COLUMN IF EXISTS binding_status;
ALTER TABLE hasn_agents DROP COLUMN IF EXISTS online_status;
ALTER TABLE hasn_agents DROP COLUMN IF EXISTS last_heartbeat_at;
```

⚠️ **注意**: 回滚会丢失所有在线状态和心跳数据。

## 后续步骤

1. ✅ 数据库迁移已完成
2. ⏳ 重启后端服务以加载新的 model 和 API
3. ⏳ 启动 Celery Beat 以运行心跳超时检测任务
4. ⏳ 重启 hasn-node daemon 以开始上报心跳
5. ⏳ 监控心跳上报和超时检测是否正常工作

## 监控建议

### 关键指标

1. **在线 agent 数量**
   ```sql
   SELECT COUNT(*) FROM hasn_agents WHERE online_status = 'online';
   ```

2. **最近心跳时间分布**
   ```sql
   SELECT
       CASE
           WHEN last_heartbeat_at IS NULL THEN '从未上报'
           WHEN last_heartbeat_at > NOW() - INTERVAL '5 minutes' THEN '5分钟内'
           WHEN last_heartbeat_at > NOW() - INTERVAL '1 hour' THEN '1小时内'
           ELSE '超过1小时'
       END AS heartbeat_status,
       COUNT(*) as count
   FROM hasn_agents
   WHERE online_status = 'online'
   GROUP BY heartbeat_status;
   ```

3. **超时 agent 检测**
   ```sql
   SELECT
       hasn_id,
       display_name,
       online_status,
       last_heartbeat_at,
       NOW() - last_heartbeat_at AS timeout_duration
   FROM hasn_agents
   WHERE
       online_status = 'online'
       AND last_heartbeat_at < NOW() - INTERVAL '1 hour';
   ```

### 告警规则

- 如果在线 agent 数量突然下降 > 50%，发送告警
- 如果心跳上报失败率 > 10%，发送告警
- 如果超时离线的 agent 数量 > 10，发送告警

## 相关文档

- 设计文档: `hasn-node/docs/agent-online-status-design.md`
- 实施总结: `hasn-node/docs/agent-online-status-implementation-summary.md`
- 迁移 SQL: `backend/sql/hasn/migrations/2026-05-23-agent-online-status.sql`
