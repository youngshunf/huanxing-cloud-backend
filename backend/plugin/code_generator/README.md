# 一键代码生成器使用指南

## 🎉 功能特性

一键从 SQL 文件生成完整的前后端代码、菜单SQL和字典SQL：

- ✅ **前端代码**：Vue组件 + TypeScript配置 + API + 路由
- ✅ **后端代码**：Model + CRUD + Schema + Service + API
- ✅ **多 Scope 支持**：支持 admin/app/agent/open 四种认证模式
- ✅ **菜单SQL**：父级菜单 + 4个按钮权限
- ✅ **字典SQL**：自动识别 status/type 等字段
- ✅ **智能跳过**：已存在文件不覆盖，不报错
- ✅ **配置驱动**：所有参数通过 config.toml 管理

## 🔐 API Scope 说明

代码生成器支持 4 种 API scope，对应不同的认证方式和数据访问策略：

| Scope | 路径 | 认证方式 | 用途 |
|-------|------|----------|------|
| `admin` | `api/v1/admin/` | JWT + RBAC + Permission | 管理端，完整权限控制 |
| `app` | `api/v1/app/` | JWT（用户数据隔离） | 用户端，只操作自己的数据 |
| `agent` | `api/v1/agent/` | Agent Key + X-User-Id | Agent 调用，API Key 认证 |
| `open` | `api/v1/open/` | 无认证 | 公开只读接口 |

### 设置 Scope

在代码生成业务中设置 `api_scope` 字段：

- **单个 scope**：`"admin"` — 仅生成管理端 API
- **多个 scope**：`"admin,app"` — 同时生成管理端和用户端 API
- **全部 scope**：`"admin,app,agent,open"` — 生成所有四种 API

## 🚀 快速开始

### 基础用法

只需要两个参数就能生成完整的前后端代码：

```bash
cd clound-backend
uv run fba codegen generate --sql-file <SQL文件路径> --app <应用名>
```

**示例：**
```bash
# 基础生成（不执行SQL）
uv run fba codegen generate --sql-file backend/sql/user.sql --app user

# 生成并自动执行SQL
uv run fba codegen generate --sql-file backend/sql/user.sql --app user --execute
```

### 通过 API 导入表

```json
POST /api/v1/code-generation/generations/imports
{
    "app": "huanxing",
    "table_schema": "fba",
    "table_name": "huanxing_project",
    "api_scope": "admin,app"
}
```

## ⚙️ 配置文件

所有其他配置都在 `backend/plugin/code_generator/config.toml` 中管理：

### 路径配置
```toml
[paths]
frontend_dir = "../clound-frontend"      # 前端项目根目录
backend_app_dir = "app"                  # 后端代码生成目录
menu_sql_dir = "backend/sql/generated"   # 菜单SQL输出目录
dict_sql_dir = "backend/sql/generated"   # 字典SQL输出目录
```

### 生成行为配置
```toml
[generation]
auto_execute_menu_sql = false            # 是否自动执行菜单SQL
auto_execute_dict_sql = false            # 是否自动执行字典SQL
existing_file_behavior = "skip"          # 文件已存在时: skip/overwrite/backup
generate_backend = true                  # 是否生成后端代码
generate_frontend = true                 # 是否生成前端代码
generate_menu_sql = true                 # 是否生成菜单SQL
generate_dict_sql = true                 # 是否生成字典SQL
```

### 后端配置
```toml
[backend]
default_api_scope = "admin"              # 默认 API scope
```

## 📦 生成内容

### 后端代码结构（多 Scope）

```
backend/app/<app>/
├── model/<表名>.py             # SQLAlchemy模型
├── crud/crud_<表名>.py         # CRUD操作
├── schema/<表名>.py            # Pydantic Schema
├── service/<表名>_service.py   # 业务逻辑
├── api/
│   ├── router.py              # 路由总入口（多 scope 子路由器）
│   └── v1/
│       ├── admin/<表名>.py    # 管理端 API（JWT + RBAC）
│       ├── app/<表名>.py      # 用户端 API（JWT + 数据隔离）
│       ├── agent/<表名>.py    # Agent API（Agent Key）
│       └── open/<表名>.py     # 公开 API（无认证）
└── sql/                        # 初始化SQL（MySQL/PostgreSQL）
```

> 只有在 `api_scope` 中指定的 scope 目录才会被生成。

### 前端代码
```
clound-frontend/apps/web-antd/src/
├── views/<app>/<表名>/
│   ├── index.vue      # 主页面（列表+表单）
│   └── data.ts        # 表格列和表单配置
├── api/<app>.ts       # API接口定义
└── router/routes/modules/<app>.ts  # 路由配置
```

### SQL文件

- ✅ `backend/sql/generated/<表名>_menu.sql` - 菜单和权限
- ✅ `backend/sql/generated/<表名>_dict.sql` - 数据字典

## 🎯 使用示例

### 示例1：仅管理端

```bash
# 默认 scope 就是 admin
uv run fba codegen generate --sql-file backend/sql/users.sql --app user
```

### 示例2：管理端 + 用户端

通过 API 导入时设置 `api_scope: "admin,app"`，会同时生成：
- `api/v1/admin/users.py` — 管理端接口（JWT + RBAC）
- `api/v1/app/users.py` — 用户端接口（JWT + 数据隔离）

### 示例3：全部四种 scope

设置 `api_scope: "admin,app,agent,open"`，生成完整的四套 API。

## ❓ 常见问题

### Q1: 生成的文件位置不对？
检查 `config.toml` 中的 `frontend_dir` 和 `backend_app_dir` 配置。

### Q2: 如何修改 api_scope？
在代码生成业务列表中编辑对应业务的 `api_scope` 字段即可。

### Q3: 新增 scope 后已有文件怎么办？
已存在的文件不会被覆盖，只会生成新 scope 的 API 文件。

### Q4: scope 的认证方式能自定义吗？
可以修改 `templates/python/api_<scope>.jinja` 模板来自定义认证逻辑。

## 🔧 数据库迁移

如果从旧版本升级，需要执行：

```sql
ALTER TABLE gen_business ADD COLUMN api_scope VARCHAR(64) DEFAULT 'admin' NOT NULL COMMENT 'API scope (admin/app/agent/open)';
```

---

**需要帮助？** 查看完整文档或联系项目维护者
