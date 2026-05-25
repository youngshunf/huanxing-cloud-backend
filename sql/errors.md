# HASN P0 错误码合并表

> 状态：P0 contract draft
> 归属：`huanxing-cloud-backend` 服务端控制面；协议错误码事实源仍是 `docs/HASN-centralized/HASN-Protocol/Appendix/A1-错误码.md`
> 目的：冻结 hasn-node ↔ server 在 P0 阶段共同依赖的错误码边界，尤其区分消息投递错误与 Runtime 调度错误。

---

## 1. 编码域

| 范围 | 归属 | 含义 | P0 处理方式 |
|---|---|---|---|
| `1xxx–7xxx` | HASN Protocol | 传输、身份、关系、权限、消息语义等协议错误 | server 透传协议语义，不重定义 |
| `8xxx` | huanxing-cloud-backend | 服务端控制面 / Owner Binding / Node 连接 / REST API 错误 | server 权威定义，P0 冻结给 hasn-node 使用 |
| `9xxx` | HASN Protocol | 系统与协议层错误 | 以 A1 为事实源 |
| `10xxx–13xxx` | HASN Protocol | 消息筛选、计费、仲裁、信用评分 | P0 只引用，不扩展 |
| `14xxx` | HASN Protocol Core/06 | 反滥用与节点信誉 | 以 Core/06 + A1 为事实源 |

---

## 2. P0 硬边界

### 2.1 RuntimeUnavailable 不是消息投递失败

以下概念禁止混用：

```text
RuntimeUnavailable != MessageDeliveryFailed
RuntimeUnavailable != AgentOffline
RuntimeUnavailable != HumanOffline
RuntimeUnavailable != ConversationSplit
```

只要消息已经写入 Human/Owner inbox、Agent inbox、owner copy 或 suppressed_inbox，就不得把 Runtime 缺失/离线/不可调度标记为消息投递失败。

### 2.2 消息投递失败只表示 inbox 不可达

`MessageDeliveryFailed` 只用于以下场景：

- 无权限进入目标 inbox；
- 目标 Human / Agent / Group 不存在；
- 被反滥用或封禁策略阻断，且消息未进入任何可拉取 inbox；
- 服务端持久化失败，消息未形成可恢复记录。

### 2.3 suppressed_inbox 是可达状态

`suppressed_inbox` 是已入箱但暂不自动执行的待处理状态。常见原因：

- Runtime 缺失；
- Runtime 离线；
- RuntimeAdapter 未注册；
- RuntimeHandle 不可用；
- 需要 owner 人工确认；
- 策略允许收信但禁止自动执行。

---

## 3. 服务端 8xxx 控制面错误码

| Code | Name | HTTP | Retryable | 含义 |
|---:|---|---:|---|---|
| 8000 | `ERR_HASN_SERVER_INTERNAL` | 500 | true | HASN 服务端内部错误 |
| 8001 | `ERR_HASN_BAD_REQUEST` | 400 | false | 请求格式错误或缺少必要字段 |
| 8002 | `ERR_HASN_UNAUTHORIZED` | 401 | false | 未登录或 token 无效 |
| 8003 | `ERR_HASN_FORBIDDEN` | 403 | false | 当前主体无权访问目标资源 |
| 8004 | `ERR_HASN_NOT_FOUND` | 404 | false | 目标资源不存在 |
| 8005 | `ERR_HASN_CONFLICT` | 409 | false | 幂等/并发冲突 |
| 8006 | `ERR_HASN_VERSION_CONFLICT` | 409 | true | revision / cursor / schema version 冲突 |
| 8007 | `ERR_HASN_CONTRACT_VERSION_UNSUPPORTED` | 426 | false | 客户端协议或 contracts tag 不受支持 |
| 8008 | `ERR_OWNER_ALREADY_BOUND` | 409 | false | Owner 已绑定到其它 Node |
| 8009 | `ERR_OWNER_BINDING_NOT_FOUND` | 404 | false | Owner Binding 不存在 |
| 8010 | `ERR_OWNER_BINDING_EXPIRED` | 401 | false | Owner Binding 已过期 |
| 8011 | `ERR_OWNER_BINDING_REVOKED` | 403 | false | Owner Binding 已吊销 |
| 8012 | `ERR_OWNER_NOT_BOUND_TO_NODE` | 403 | false | Owner 未绑定当前 Node |
| 8013 | `ERR_NODE_NOT_FOUND` | 404 | false | Node 不存在 |
| 8014 | `ERR_AGENT_NOT_FOUND` | 404 | false | Agent 不存在 |
| 8015 | `ERR_AGENT_ALREADY_ONLINE_ELSEWHERE` | 409 | false | Agent 已在另一 Node 在线 |
| 8016 | `ERR_AGENT_NOT_OWNED_BY_OWNER` | 403 | false | Agent 不属于当前 Owner |
| 8017 | `ERR_OWNER_PROOF_SCOPE_INSUFFICIENT` | 403 | false | Owner proof scope 不足 |
| 8018 | `ERR_OWNER_PROOF_NODE_MISMATCH` | 403 | false | Owner proof 绑定了其它 Node |
| 8019 | `ERR_ONBOARDING_PENDING_INTENT_EXPIRED` | 410 | false | pending intent 已过期 |
| 8020 | `ERR_ONBOARDING_DEFAULT_AGENT_FAILED` | 500 | true | 默认 Agent ensure 失败 |
| 8021 | `ERR_SYNC_CURSOR_INVALID` | 400 | false | sync cursor 无效 |
| 8022 | `ERR_SYNC_REVISION_CONFLICT` | 409 | true | sync revision 冲突 |
| 8023 | `ERR_INBOX_CURSOR_INVALID` | 400 | false | inbox cursor 无效 |
| 8024 | `ERR_MESSAGE_DELIVERY_FAILED` | 500 | true | 消息未能进入任何目标 inbox；不得用于 RuntimeUnavailable |
| 8025 | `ERR_MESSAGE_TARGET_NOT_FOUND` | 404 | false | 消息目标不存在 |
| 8026 | `ERR_MESSAGE_PERMISSION_DENIED` | 403 | false | 消息因权限被拒绝且未进入 inbox |
| 8027 | `ERR_SANDBOX_NOT_FOUND` | 404 | false | Sandbox 不存在 |
| 8028 | `ERR_SANDBOX_STATE_CONFLICT` | 409 | true | Sandbox 状态冲突 |
| 8029 | `ERR_SANDBOX_PROVISION_FAILED` | 500 | true | Sandbox 创建/唤醒失败 |
| 8030 | `ERR_CHANNEL_BINDING_NOT_FOUND` | 404 | false | Channel Binding 不存在 |
| 8031 | `ERR_CHANNEL_BINDING_CONFLICT` | 409 | false | Channel Binding 冲突 |
| 8032 | `ERR_CHANNEL_INBOUND_REJECTED` | 400 | false | 第三方渠道入站消息被拒绝 |
| 8033 | `ERR_RUNTIME_REPORT_INVALID` | 400 | false | Runtime status report 格式或语义无效 |
| 8034 | `ERR_RUNTIME_PRIVATE_METADATA_REJECTED` | 400 | false | 客户端试图上传 Runtime 私有本地元数据 |
| 8035 | `ERR_MEMORY_SYNC_SCOPE_INVALID` | 400 | false | 记忆同步载荷缺少 sync_scope_kind / sync_scope_id / namespace |

---

## 4. Runtime 调度状态码不是投递错误码

Runtime 调度结果优先作为 `dispatch_status` / warning / audit 表达，不作为 message delivery error。

| Dispatch status | 含义 | 是否阻断消息投递 | 推荐 error/warning |
|---|---|---|---|
| `not_required` | Human 消息或无需自动执行 | 否 | 无 |
| `pending_runtime` | 已入 inbox，等待 Runtime | 否 | 无 |
| `dispatched` | 已派发 Runtime | 否 | 无 |
| `runtime_unavailable` | Runtime 缺失/离线/Adapter/Handle 不可用 | 否 | warning：`ERR_RUNTIME_UNAVAILABLE_NON_BLOCKING` |
| `dispatch_failed` | Runtime 执行失败 | 否 | warning：`ERR_RUNTIME_DISPATCH_FAILED_NON_BLOCKING` |
| `suppressed_by_policy` | 策略允许收信但禁止自动执行 | 否 | warning：`ERR_RUNTIME_SUPPRESSED_BY_POLICY` |

P0 约定的 warning names：

| Name | 含义 |
|---|---|
| `ERR_RUNTIME_UNAVAILABLE_NON_BLOCKING` | Runtime 不可用，但消息已经可达 |
| `ERR_RUNTIME_DISPATCH_FAILED_NON_BLOCKING` | Runtime 派发/执行失败，但消息已经可达 |
| `ERR_RUNTIME_SUPPRESSED_BY_POLICY` | 策略禁止自动执行，但消息已经可达 |

---

## 5. 与协议错误码的映射

| 场景 | 使用错误域 | 说明 |
|---|---|---|
| HASN frame 格式错误 | 协议 `9xxx` | 以 A1 / A2 / schemas 为准 |
| 权限/关系拒绝 | 协议 `2xxx/3xxx/4xxx` 或 server `8026` | Wire 层优先协议码；REST 控制面可用 `8026` |
| Node/Owner binding 问题 | server `8008–8018` | 兼容现有服务端 HASN binding 错误 |
| 消息未入任何 inbox | server `8024` | 真正投递失败 |
| Runtime 不可用 | dispatch warning | 不使用 `8024` |
| 反滥用封禁/限流 | 协议 `14xxx` 或 `9004` | 以 Core/06 + A1 为准 |

---

## 6. P0 验收要求

1. `openapi-hasn-cloud-v1.yaml` 的 `ErrorObject` 与本表字段兼容。
2. `ERR_MESSAGE_DELIVERY_FAILED` 的说明必须保留 “不得用于 RuntimeUnavailable”。
3. `dispatch_status` 必须覆盖 `runtime_unavailable`、`dispatch_failed`、`suppressed_by_policy`。
4. 服务端实现前，Ralph 不得新增 8xxx 错误码；发现缺口必须提交 `CONTRACT_GAP`。
5. contracts tag 冻结后，本文件变更必须走 ADR。
