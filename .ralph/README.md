# `.ralph/` — Hermes Backend Ralph 任务存档

> 参考 `hasn-node/webui/.ralph/` 与 `huanxing-hermes-runtime/.ralph/` 的约定。每个 ralph wiggum 任务独占一个子目录，PROMPT.md 落盘以便追溯。

## 目录约定

```
.ralph/
├── README.md             # 本文件
├── <CODE>/
│   ├── PROMPT.md         # 给 ralph 的提示词原文（10 节标准结构）
│   ├── NOTES.md          # ralph 自己每轮迭代结束更新的进度笔记
│   └── RETRO.md          # （可选）人类回头写的复盘
```

## `<CODE>` 命名

按 MVP 规划的整合任务编号：

- `M1` — backend Hermes Agent 编排串通（runtime client 4 方法 + create/delete 编排 + templates list + chat SSE）
- 历史归档代号（已完成，未存档 PROMPT，仅记录在此）：
  - **B3-1** — `hermes_agent_llm_token` 表 + `LlmNewapiUserMappingService` 4 方法
  - **B3-2** — internal endpoints `POST /api/v1/hermes/internal/llm/{issue,revoke,rotate}-credential` + `usage/summary?agent_id=`

## 已完成 wiggum

| Code | 状态 | 主要 commit / 文件 |
|---|---|---|
| B3-1 | ✅ | `backend/sql/tables/hermes_agent_llm_token.sql` + `app/llm/service/llm_newapi_user_mapping_service.py:279-461` |
| B3-2 | ✅ | `app/llm/api/v1/internal/llm_credential.py` |

## 待跑 wiggum

| Code | 状态 | 一句话 | 依赖 |
|---|---|---|---|
| M1 | 待 owner 审 PROMPT | backend Hermes Agent 编排串通 + templates list + chat SSE | runtime M2 已完成 |

## 启动方式

```bash
# 在 backend 仓根目录
/ralph-loop "$(cat .ralph/M1/PROMPT.md)" --completion-promise "M1_DONE" --max-iterations 30
```

## 跑前 checklist

1. baseline 测试通过（`uv run pytest tests/ -q`）
2. working tree 干净
3. M2（runtime template apply）已 done — M1 调 runtime 的 `/template/apply` + `/credential/install`
4. ralph 跑完后人类验收：
   - 跑 pytest 看新增测试数对
   - 跑 dev server `uv run python -m backend` 验证 endpoint 真起来
   - **不轻信 commit message 里的"Tested: ..."**（详见 hermes-runtime 仓 `.ralph/A1/RETRO.md` proxy 假阳性事故）
