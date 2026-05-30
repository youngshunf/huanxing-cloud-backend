# CLAUDE.md

本仓库是唤星（HuanXing）云端后端，**独立 git 仓库**（父项目 `huanxing-project` 自 2026-04-20 起放弃 submodule，各子仓自管自 push）。完整项目上下文、技术栈、`fba codegen` 与后端开发规范见父项目 `huanxing-project/CLAUDE.md`；本仓贡献细则见 `CONTRIBUTING.md`。

- **仓性质**：**fork 仓**（基于上游 fork）。我们的**主分支是 `huanxing`**；`main` 是上游分支，**只用于跟随上游 sync，不要把我们的代码合进 `main`**。feature 合并与 `git push` 一律针对 `huanxing`。

## 多会话分支纪律（主仓恒在主分支，新建分支必走 worktree）

多会话 / 多 agent 会同时在同一个主 clone 上工作，**绝不**为了开发把主仓库 `git checkout` 到 feature 分支（会互相 reset/覆盖——曾发生 A 会话 merge、B 会话 `git reset` 撤销并清掉对方工作区改动，来回数轮差点丢工作）。

- **主仓库（主 clone）始终停在主分支 `huanxing`，不随意切换。**
- **小修复 / 小 UI 改 / 文档** → 直接在 `huanxing` 上做 → 跑最小校验 → 立即提交，不新建分支。
- **稍复杂的功能** → 从 `huanxing` `git worktree add ../<名> -b <分支>` 拉独立工作树开发，主仓库不动；完成后回 `huanxing` 合并、删 worktree。
- 一句话：**新建分支 = 必走 worktree**。提交用 `git commit -m "..." -- <你的文件>` 精确提交，发现别的会话的脏/staged 改动**不要碰**；push 前先 `git fetch origin huanxing` 整合，**禁止 force-push**。
