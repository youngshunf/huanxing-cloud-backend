# 唤星 AI 后端 — API 认证与接口规范

> 版本: v1.0 | 更新时间: 2026-03-09 | 作者: 杨顺富

---

## 一、认证体系概览

后端采用 **四层认证架构**，不同调用方使用不同的认证方式：

| 层级 | 路径前缀 | 认证方式 | 调用方 | Header |
|------|---------|---------|--------|--------|
| **公开** | `/api/v1/auth/*`<br>`/api/v1/*/open/*` | 无需认证 | 任何人 | — |
| **Agent** | `/api/v1/*/agent/*` | Agent Key | OpenClaw 插件 | `X-Agent-Key: <key>` |
| **用户端** | `/api/v1/*/app/*` | JWT Bearer | 前端用户 | `Authorization: Bearer <jwt>` |
| **管理端** | `/api/v1/*/` (admin) | JWT + RBAC | 管理后台 | `Authorization: Bearer <jwt>` |
| **HASN** | `/api/v1/hasn/*` | JWT / ApiKey 双模式 | 社交网络 | `Authorization: Bearer <jwt>` 或 `Authorization: ApiKey <key>` |

### 认证流程图

```
┌─────────────────────────────────────────────────────────────┐
│                       HTTP 请求进入                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ Nginx   │
                    └────┬────┘
                         │
              ┌──────────▼──────────┐
              │  JWT Auth Middleware │
              │  (Starlette层)       │
              └──────────┬──────────┘
                         │
            ┌────────────▼────────────┐
            │  路径匹配 JWT 白名单?     │
            │  (TOKEN_REQUEST_PATH_   │
            │   EXCLUDE_PATTERN)      │
            └────┬──────────────┬─────┘
                 │ 是           │ 否
                 │              │
        ┌────────▼───┐   ┌─────▼──────┐
        │ 跳过 JWT   │   │ 验证 JWT   │
        │ 认证       │   │ Token      │
        └────────┬───┘   └─────┬──────┘
                 │              │
        ┌────────▼───────────────▼────────┐
        │       路由层认证依赖              │
        │  DependsAgentAuth / hasn_auth   │
        │  / DependsJwtAuth               │
        └─────────────────────────────────┘
```

---

## 二、Agent Key 认证（X-Agent-Key）

### 适用场景

OpenClaw 服务器上的 huanxing-cloud 插件代替 Guardian Agent 调用后端接口，用于：
- 用户注册时同步信息到后端
- 代替用户操作文档（CRUD）
- 查询/扣减用户配额

### 认证方式

```http
X-Agent-Key: wNYPBNNl61kwVLWgFW7N1yFJKb4yCqJxjSKy__RtG94
X-Server-Id: huanxing-prod-01     # 可选，标识来源服务器
X-App-Code: huanxing              # 应用标识
```

### 密钥管理

- **配置位置**: 后端 `.env` 文件的 `AGENT_SECRET_KEY` 字段
- **插件配置**: OpenClaw `openclaw.json` → `plugins.entries.huanxing-cloud.config.agentKey`
- **支持多 Key**: 逗号分隔，便于密钥轮换（如 `key1,key2`，两个 key 同时有效）
- **安全机制**: 使用 `hmac.compare_digest` 防止时序攻击

### 代码位置

```
backend/common/security/agent_auth.py
```

### 依赖注入

```python
from backend.common.security.agent_auth import DependsAgentAuth

@router.get("/xxx", dependencies=[DependsAgentAuth])
async def xxx(request: Request):
    agent_info = request.state.agent_info
    # agent_info = {"authenticated": True, "server_id": "xxx", "key_prefix": "wNYPBNNl..."}
```

---

## 三、JWT Bearer 认证

### 适用场景

前端用户（Web/App）登录后获取 JWT Token，用于访问用户端和管理端接口。

### 认证方式

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-App-Code: huanxing
```

### Token 获取

```
POST /api/v1/auth/login          # 账号密码登录
POST /api/v1/auth/phone-login    # 手机号验证码登录（返回 access_token）
```

### Token 生命周期

| 参数 | 值 | 说明 |
|------|---|------|
| `TOKEN_EXPIRE_SECONDS` | 86400 (1天) | Access Token 有效期 |
| `TOKEN_REFRESH_EXPIRE_SECONDS` | 604800 (7天) | Refresh Token 有效期 |
| `TOKEN_ALGORITHM` | HS256 | 签名算法 |

### Token Payload

```json
{
  "session_uuid": "uuid-v4",
  "exp": 1773100000,
  "sub": "12345"          // 用户 ID (整数)
}
```

---

## 四、HASN 社交网络认证

### 适用场景

HASN (Human-Agent Social Network) 社交网络内部通信。

### 双模式认证

```http
# 模式一：Human 用 JWT
Authorization: Bearer <hasn_jwt>

# 模式二：Agent 用 ApiKey
Authorization: ApiKey hasn_ak_xxxxxxxxxx
```

### 代码位置

```
backend/app/hasn_core/service/hasn_auth.py
```

---

## 五、JWT 白名单配置

以下路径跳过 JWT 中间件认证（在 `core/conf.py` 中配置）：

### 精确匹配白名单

| 路径 | 说明 |
|------|------|
| `/api/v1/auth/login` | 登录 |
| `/api/v1/auth/send-code` | 发送验证码 |
| `/api/v1/auth/phone-login` | 手机号登录 |

### 正则匹配白名单

| 模式 | 说明 |
|------|------|
| `/api/v1/huanxing/open/.*` | 唤星公开 API |
| `/api/v1/huanxing/agent/.*` | 唤星 Agent API（使用 X-Agent-Key） |
| `/api/v1/user_tier/agent/.*` | 订阅积分 Agent API（使用 X-Agent-Key） |
| `/api/v1/hasn/.*` | HASN 社交 API（独立认证） |
| `/api/v1/llm/proxy(/.*)?` | LLM 代理（使用 x-api-key） |
| `/api/v1/marketplace/client/.*` | 桌面端市场公开 API |

---

## 六、接口路由规范

### 路径命名规则

```
/api/v1/{模块名}/{层级}/{资源名}
```

- **模块名**: `huanxing` / `user_tier` / `hasn_core` / `hasn_social` / `pay` / `llm`
- **层级**: `admin` / `app` / `open` / `agent`
- **资源名**: 复数名词，如 `users` / `docs` / `folders` / `servers`

### 各层级职责

| 层级 | 路径示例 | 认证 | 说明 |
|------|---------|------|------|
| `admin/` | `/api/v1/huanxing/users` | JWT + RBAC | 管理后台，需要管理员权限 |
| `app/` | `/api/v1/huanxing/app/docs` | JWT | 用户端，仅能操作自己的数据 |
| `open/` | `/api/v1/huanxing/open/share/{uuid}` | 无 | 公开访问，如分享链接 |
| `agent/` | `/api/v1/huanxing/agent/docs` | X-Agent-Key | Agent 代替用户操作，需传 `user_id` 参数 |

### Agent 层级特殊规则

Agent 接口中，用户身份通过 **请求参数** 传递（而非从 JWT 中提取）：

```http
# Agent 查询用户文档
GET /api/v1/huanxing/agent/docs?user_id=12345
X-Agent-Key: wNYPBNNl61kwVLWgFW7N1yFJKb4yCqJxjSKy__RtG94

# Agent 创建文档
POST /api/v1/huanxing/agent/docs?user_id=12345
X-Agent-Key: wNYPBNNl61kwVLWgFW7N1yFJKb4yCqJxjSKy__RtG94
Content-Type: application/json

{"title": "文档标题", "content": "..."}
```

---

## 七、现有 Agent 接口清单

### 唤星模块 (`/api/v1/huanxing/agent/`)

#### 用户同步

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/agent/users` | 注册时同步用户信息到后端 |
| `PUT` | `/agent/users/{user_id}` | 更新用户信息 |

**POST /agent/users 请求体:**
```json
{
  "user_id": "uuid-string",
  "server_id": "huanxing-prod-01",
  "agent_id": "001-18611348367-assistant",
  "star_name": "小星",
  "template": "assistant",
  "channel_type": "qq",
  "channel_peer_id": "BC21944A...",
  "workspace_path": "/opt/huanxing/users/001-18611348367-assistant"
}
```

#### 文档操作

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/agent/docs?user_id=N` | 文档列表 |
| `POST` | `/agent/docs?user_id=N` | 创建文档 |
| `GET` | `/agent/docs/{pk}?user_id=N` | 文档详情 |
| `PUT` | `/agent/docs/{pk}?user_id=N` | 更新文档 |
| `DELETE` | `/agent/docs/{pk}?user_id=N` | 删除文档 |
| `POST` | `/agent/docs/{pk}/move?user_id=N` | 移动文档 |

#### 目录操作

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/agent/docs/folders?user_id=N` | 目录树 |
| `POST` | `/agent/docs/folders?user_id=N` | 创建目录 |
| `POST` | `/agent/docs/folders/{id}/move?user_id=N` | 移动目录 |
| `DELETE` | `/agent/docs/folders/{id}?user_id=N` | 删除目录 |

### 订阅积分模块 (`/api/v1/user_tier/agent/`)

#### 配额查询

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/agent/quota/{user_id}` | 查询用户配额和积分 |
| `POST` | `/agent/quota/deduct` | 扣减用户积分 |

---

## 八、通用响应格式

### 成功响应

```json
{
  "code": 200,
  "msg": "请求成功",
  "data": { ... }
}
```

### 错误响应

```json
{
  "code": 401,
  "msg": "Agent Key 无效。请在请求头中提供 X-Agent-Key。",
  "data": null
}
```

### 常见状态码

| code | 含义 |
|------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败（Token/Key 无效或缺失） |
| 403 | 权限不足（如操作他人资源） |
| 404 | 资源不存在 |
| 422 | 请求体校验失败 |
| 500 | 服务器内部错误 |

---

## 九、OpenClaw 插件配置参考

OpenClaw 服务器 `openclaw.json` 中的 huanxing-cloud 插件配置：

```json5
{
  "plugins": {
    "entries": {
      "huanxing-cloud": {
        "enabled": true,
        "config": {
          // 后端 API 地址
          "apiBaseUrl": "https://api.huanxing.dcfuture.cn",
          // Agent Key（与后端 .env 的 AGENT_SECRET_KEY 一致）
          "agentKey": "wNYPBNNl61kwVLWgFW7N1yFJKb4yCqJxjSKy__RtG94",
          // LLM 网关地址（用户 Agent 的模型请求地址）
          "llmBaseUrl": "https://llm.dcfuture.cn",
          // 服务器标识
          "serverId": "huanxing-prod-01",
          // 服务器 IP
          "serverIp": "115.191.47.200"
        }
      }
    }
  }
}
```

### 插件请求头映射

| 配置字段 | Header | 用途 |
|----------|--------|------|
| `agentKey` | `X-Agent-Key` | Agent 接口认证 |
| `serverId` | `X-Server-Id` | 标识来源服务器 |
| — | `X-App-Code: huanxing` | 应用标识（固定值） |

---

## 十、安全注意事项

1. **Agent Key 不可泄露** — 拥有 Agent Key 等同于拥有所有用户数据的操作权限
2. **密钥轮换** — `AGENT_SECRET_KEY` 支持逗号分隔多 Key，轮换时先添加新 Key，待所有服务更新后再删除旧 Key
3. **Agent 层 user_id 可信** — Agent Key 认证通过即信任 `user_id` 参数，不做二次校验
4. **传输安全** — 生产环境必须使用 HTTPS
5. **日志脱敏** — Agent Key 在日志中仅显示前 8 位（`wNYPBNNl...`）

---

## 附录：文件索引

| 文件 | 职责 |
|------|------|
| `backend/common/security/agent_auth.py` | Agent Key 认证模块 |
| `backend/common/security/jwt.py` | JWT 认证模块 |
| `backend/app/hasn_core/service/hasn_auth.py` | HASN 双模式认证 |
| `backend/middleware/jwt_auth_middleware.py` | JWT 中间件 |
| `backend/middleware/app_context_middleware.py` | 应用上下文中间件（X-App-Code） |
| `backend/core/conf.py` | 全局配置（白名单、密钥等） |
| `backend/app/huanxing/api/v1/agent/` | 唤星 Agent 接口目录 |
| `backend/app/user_tier/api/v1/agent/` | 订阅积分 Agent 接口目录 |
