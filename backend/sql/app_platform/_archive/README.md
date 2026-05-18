# app_platform/_archive/

> 本目录保存设计阶段产出的历史 SQL 草稿，**不再用于 fba codegen 落表**。
>
> 落表事实源已迁移到 [`../mvp/`](../mvp/README.md)（[P0]）。

## 1. 归档原因

设计阶段早期产出了多份单表 SQL 草稿，在迭代过程中出现：

- **SQL 语法错误**：如 `app_installations.sql` 第 23 行 `TIMESTAMP WITH TIME ZONE WITH TIME ZONE WITH TIME ZONE` 重复三次，PostgreSQL 解析失败
- **空文件**：`006_app_manifests.sql` 是 0 字节
- **重复定义**：`006_app_data_records.sql` 与 `006_create_app_data_records.sql` 同表两份
- **跨阶段污染**：单表草稿混合了 [P0]/[P1]/[P2] 字段，无法直接作为某一阶段的最小集
- **外键提前**：[P0] 表外键引用了 [P1+] 才会落表的 `app_resources / app_listings` 等

为符合 `decisions/architecture/2026-05-18-ai-native-app-platform-phasing.md` 钉死的"完整设计、分阶段落表"原则，全部归档。

## 2. 处理规则

- `fba codegen` **不应**扫描本目录。如果代码生成命令意外读取这里的 SQL，请检查 codegen 配置是否限定了 `--sql-file` 路径。
- 任何**新增 SQL** 必须放到 `../mvp/`（[P0]）或将来的 `../phase1/`（[P1]）等子目录，不得复活本目录文件。
- 仅当需要追溯"为什么早期设计是这样"时阅读本目录。

## 3. 归档清单

| 文件 | 原计划承载的能力 | 当前替代 |
|---|---|---|
| `001_create_permission_tables.sql` | [P1] 权限表早期草稿 | `../mvp/002_app_installations.sql.granted_scopes` JSONB（[P0]）；[P1] 时新建 `../phase1/` |
| `002_app_scopes.sql` | [P1] 应用 scope 注册 | manifest_jsonb.requested_scopes（[P0]） |
| `003_app_permission_grants.sql` | [P1] grant 拆表 | `../mvp/002_app_installations.sql.granted_scopes`（[P0]） |
| `004_app_dynamic_permission_requests.sql` | [P1] 动态权限请求 | [P0] 不实现 |
| `005_create_app_core_tables.sql` | [P0] 核心表（早期版本，含语法错误） | `../mvp/001-004` |
| `006_app_data_records.sql` / `006_create_app_data_records.sql` | [P0] 数据记录（重复定义） | `../mvp/003_app_data_records.sql` |
| `006_app_manifests.sql` | [P0] App 本体（空文件） | `../mvp/001_app_manifests.sql` |
| `007_app_permission_audit_logs.sql` / `007_create_app_permission_audit_logs.sql` | [P1] 独立权限审计表 | `../mvp/004_app_audit_logs.sql` 统一记录（[P0]） |
| `999_rename_timestamp_columns.sql` | 列名修正脚本 | mvp/ 已直接采用 `created_time / updated_time` 命名 |
| `app_agent_bindings.sql` | [P2] Agent 绑定 | manifest_jsonb + installation.install_target_*（[P0]） |
| `app_entitlements.sql` | [P2] 购买凭证 | mvp/002_app_installations.sql.entitlement_id 字段占位 |
| `app_events.sql` | [P1] Event 定义 | manifest_jsonb.events[]（[P0]） |
| `app_installations.sql` | [P0] 安装记录（含 SQL 语法错误） | `../mvp/002_app_installations.sql` |
| `app_listings.sql` | [P2] 应用市场 listing | mvp/002_app_installations.sql.listing_id 字段占位 |
| `app_manifests.sql` | [P0] App 本体（早期单表版） | `../mvp/001_app_manifests.sql` |
| `app_resources.sql` | [P1] Resource 定义 | manifest_jsonb.resources[]（[P0]） |
| `app_reviews.sql` | [P2] 审核记录 | [P0] 不实现 |
| `app_tools.sql` | [P1] Tool 定义 | manifest_jsonb.tools[]（[P0]） |
| `app_versions.sql` | [P1] 版本历史 | manifest_jsonb.version 字段（[P0]） |

## 4. 删除时机

待 [P1] 实施完成后，本目录可以删除（git 历史保留即可）。
