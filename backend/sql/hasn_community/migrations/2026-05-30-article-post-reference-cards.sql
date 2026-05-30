-- 引用卡片（reference_cards）：社区文章/帖子可引用 Agent 技能 / 任务结果 / 聊天摘要
-- 存储形状沿用 IM 卡片消息的 HasnCardResource：
--   [{ "type": "agent_skill|task_result|chat_summary",
--      "id": "...", "uri": "hasn://webui/...",
--      "title": "...", "summary": "...",
--      "access": { "visibility": "author_only|public", "readable_by": ["<author_hasn_id>"] },
--      "metadata": { ... } }]
-- 序列化时由后端按 viewer 决定是否下发可跳转 action（见 community_service 序列化）。

ALTER TABLE hasn_articles ADD COLUMN IF NOT EXISTS reference_cards JSONB NOT NULL DEFAULT '[]';
ALTER TABLE hasn_posts    ADD COLUMN IF NOT EXISTS reference_cards JSONB NOT NULL DEFAULT '[]';

COMMENT ON COLUMN hasn_articles.reference_cards IS '引用卡片数组 [{type,id,uri,title,summary,access,metadata}]，type ∈ agent_skill/task_result/chat_summary';
COMMENT ON COLUMN hasn_posts.reference_cards    IS '引用卡片数组 [{type,id,uri,title,summary,access,metadata}]，type ∈ agent_skill/task_result/chat_summary';
