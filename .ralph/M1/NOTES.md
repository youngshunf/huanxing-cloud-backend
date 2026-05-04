# M1 NOTES — last updated: 2026-05-04 (placeholder)

> 首轮起点占位。ralph 第 1 轮迭代开始时把本文件覆盖为真实进度笔记。

## Iteration 0 (placeholder)
- 完成：—（owner 起草 PROMPT.md，等待 ralph 启动）
- 验收项进度：5.1 [0/5] / 5.2 [0/?] / 5.3 [0/?] / 5.4 [0/?] / 5.5 [0/?] / 5.6 [0/10] / 5.7 [0/2]
- 卡点：无
- 下轮第一件事：跑 `NO_PROXY=127.0.0.1,localhost,::1 uv run pytest tests/ -q` 拿到 baseline 测试数；再读 `hermes_runtime_client.py` 现有 21 个方法，加 4 个新方法（apply_template/get_template_status/install_credential/uninstall_credential）

## 已确认决策
- 决策 1/2/3/4/5/6（owner 拍板，详见 PROMPT.md §4）
- 模板包传输：backend 推 url+hash 给 runtime（不让 runtime 直接读 marketplace 表）
- 不实现 hermes_agent_template_application 历史表
- 不支持 BYOK（payload.llm_mode='byok' fast-fail）

## TODO 队列（按优先级）
1. `hermes_runtime_client.py` 加 4 个方法 + 1 个 chat_completions_stream
2. `hermes_agent_app_service.create_agent` 重构为 9 步编排
3. `hermes_agent_app_service.delete_agent` 重构为反向 6 步
4. 新建 `api/v1/app/templates.py` + `marketplace_app+app_version` JOIN 查询
5. `agents.py:hermes_chat_completions` 改造 SSE
6. 新建 `tests/hermes/test_agent_app_service.py`（10 个 case）
7. 跑 baseline + 10 测试通过
