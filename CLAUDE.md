# CLAUDE.md

本仓库是唤星（HuanXing）云端后端，**独立 git 仓库**（父项目 `huanxing-project` 自 2026-04-20 起放弃 submodule，各子仓自管自 push）。完整项目上下文、技术栈、`fba codegen` 与后端开发规范见父项目 `huanxing-project/CLAUDE.md`；本仓贡献细则见 `CONTRIBUTING.md`。

- **仓性质**：**fork 仓**（基于上游 fork）。我们的**主分支是 `huanxing`**；`main` 是上游分支，**只用于跟随上游 sync，不要把我们的代码合进 `main`**。feature 合并与 `git push` 一律针对 `huanxing`。

## 响应格式硬规则（统一信封，违反会让 daemon 解析炸）

**正常业务接口一律用统一返回格式**：`response_model=ResponseModel`（含子类 `ResponseSchemaModel`）+ `return response_base.success(data=...)`，产出 `{code, msg, data}` 信封。**不许**裸 `return SomeSchema(...)`（`-> SomeSchema`）——FastAPI 会直接序列化成裸对象绕过信封，而 daemon transport `.send()` → `decode_ok_envelope` 依赖信封，裸返回会让 daemon 报 `error decoding response body`（2026-06-02 权限 tab `get_scope_catalog` 事故，commit `54da4c4`）。

- **裸返回仅限"统一信封根本满足不了"的接口**：OpenAI/Anthropic 兼容代理（外部 SDK 按原生形状解析）、文件/YAML/下载/导出、重定向、第三方 webhook（须回 provider 指定文本）。图省事不算理由。
- **守卫**：`backend/tests/test_response_envelope_contract.py` 内省全部路由，断言不许新增非信封业务接口（白名单 `KNOWN_NON_ENVELOPE` 分"真例外"和"已知欠债"两段）。新接口若不走信封又非真例外 → 测试红。
- **加端点要跑真实 HTTP**（打运行中 8020），不能只跑 service 层 E2E——后者绕过 HTTP，抓不到这类外壳漂移。

## 多会话分支纪律（主仓恒在主分支，新建分支必走 worktree）

多会话 / 多 agent 会同时在同一个主 clone 上工作，**绝不**为了开发把主仓库 `git checkout` 到 feature 分支（会互相 reset/覆盖——曾发生 A 会话 merge、B 会话 `git reset` 撤销并清掉对方工作区改动，来回数轮差点丢工作）。

- **主仓库（主 clone）始终停在主分支 `huanxing`，不随意切换。**
- **小修复 / 小 UI 改 / 文档** → 直接在 `huanxing` 上做 → 跑最小校验 → 立即提交，不新建分支。
- **稍复杂的功能** → 从 `huanxing` `git worktree add ../<名> -b <分支>` 拉独立工作树开发，主仓库不动；完成后回 `huanxing` 合并、删 worktree。
- 一句话：**新建分支 = 必走 worktree**。提交用 `git commit -m "..." -- <你的文件>` 精确提交，发现别的会话的脏/staged 改动**不要碰**；push 前先 `git fetch origin huanxing` 整合，**禁止 force-push**。
