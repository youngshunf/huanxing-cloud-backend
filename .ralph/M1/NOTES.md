# M1 NOTES — last updated: 2026-05-04T13:30Z

## Iteration 1 (2026-05-04)
- 完成：§5.1 全部 5/5 验收项落地
  - `HermesRuntimeClient.apply_template` (POST /runtime/v1/agents/{id}/template/apply)
  - `HermesRuntimeClient.get_template_status` (GET /runtime/v1/agents/{id}/template/status)
  - `HermesRuntimeClient.install_credential` (POST /runtime/v1/agents/{id}/credential/install)
  - `HermesRuntimeClient.uninstall_credential` (DELETE /runtime/v1/agents/{id}/credential)
  - `HermesRuntimeClient.chat_completions_stream` async iterator → SSE 透传
- 验收项进度：5.1 [5/5] / 5.2 [0/?] / 5.3 [0/?] / 5.4 [0/?] / 5.5 [0/?] / 5.6 [8/10] / 5.7 [0/2]
  - 5.6 已有 8 个 runtime client 单测（不在 §5.6 要求的 10 个 service-level case 之列，但提前覆盖了 §5.1）
- 卡点：无
- 测试 baseline：42 → 50（+8 全绿）
- commit：`82b832f feat(hermes): HermesRuntimeClient 加 template/credential 4 方法 + chat SSE 流式（M1 §5.1）`
- 下轮第一件事：§5.2 改 `backend/app/hermes/service/hermes_agent_app_service.py:create_agent` (L278-407)
  - 关注点：现有 `payload` 字段名 `soul/user_profile/auto_start_gateway`（与 PROMPT.md §5.2 描述的 `soul_content/user_content/start_gateway` 不一致）；按现有 schema 走，不改前端契约
  - 流程：byok 校验 → marketplace 查模板 → 本地 record(creating) → ensure_agent → apply_template → ensure_agent_token → install_credential → start_gateway(可选) → status='ready'
  - 失败回滚链：revoke_agent_token + uninstall_credential + runtime.delete_agent（全部 swallow）
  - 子任务拆分（避免单 commit 太大）：
    a. 加 `_resolve_template` helper（marketplace JOIN 查 latest version）
    b. 加 byok fast-fail
    c. 在现有 try 体内插入 apply_template 调用（接 ensure_agent 之后）
    d. 在现有 try 体内插入 ensure_agent_token + install_credential（接 apply_template 之后）
    e. 加回滚链 helper `_rollback_create(...)` swallow-error 包装

## 已知差异（不破坏向后兼容）
- `backend/tests/hermes/test_agent_app_service.py` 已有 7 个 stub-based service 单测（用 SimpleNamespace + InMemorySession fixture），M1 新增的 service 单测需要 mirror 此风格，但放在 `tests/hermes/test_agent_app_service.py`（top-level）
- 现 service 的 `create_agent` payload 字段：`agent_name / template / timezone / soul / user_profile / auto_start_gateway`（与 PROMPT.md 描述的 `soul_content/user_content/start_gateway/llm_mode` 不同）；§5.2 编排时新增 byok 校验通过 `getattr(payload, 'llm_mode', 'platform')` 兼容现有 schema

## 已确认决策
- 决策 1/2/3/4/5/6（owner 拍板，详见 PROMPT.md §4）
- 模板包传输：backend 推 url+hash 给 runtime（不让 runtime 直接读 marketplace 表）
- 不实现 hermes_agent_template_application 历史表
- 不支持 BYOK（payload.llm_mode='byok' fast-fail）

## TODO 队列（按优先级）
1. ~~§5.1 hermes_runtime_client.py 加 4+1 方法~~ ✅ (iter 1)
2. §5.2 hermes_agent_app_service.create_agent 9 步编排（含 byok 校验 + template lookup + credential install）
3. §5.3 delete_agent 反向 6 步
4. §5.4 新建 api/v1/app/templates.py + marketplace JOIN
5. §5.5 chat completions SSE endpoint 改造（StreamingResponse + chat_completions_stream）
6. §5.6 service-level 10 个 case（create happy/byok/template_not_found/runtime_fails/rollback；delete happy/stop_gateway_fails；templates list with-data/empty；chat SSE）
7. §5.7 验收命令两条 0 failed
