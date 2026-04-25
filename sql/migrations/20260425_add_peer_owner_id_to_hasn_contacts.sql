-- 20260425 · hasn_contacts 加 peer_owner_id 列
--
-- 配套 ORM 改动：backend/app/hasn/model/hasn_contacts.py
-- US-001 (HASN Contacts 三层架构统一 Phase 1) 引入此列以区分
-- "我的 agent" vs "别人的 agent"。
-- 与 alembic/versions/20260424_h1_hasn_contacts_peer_owner.py 等价；
-- 这里另存一份纯 SQL 便于审计与手工回放。
--
-- 幂等：用 IF NOT EXISTS。

ALTER TABLE hasn_contacts
    ADD COLUMN IF NOT EXISTS peer_owner_id varchar(36);

-- 部分索引：仅索引非空值，节省空间。
CREATE INDEX IF NOT EXISTS idx_contact_peer_owner
    ON hasn_contacts (peer_owner_id)
    WHERE peer_owner_id IS NOT NULL;

COMMENT ON COLUMN hasn_contacts.peer_owner_id IS
    'contact 自身的 owner hasn_id：peer_type=agent 时区分归属（"我的 agent" vs "别人的 agent"），peer_type=human 时通常 NULL';
