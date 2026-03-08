-- =====================================================
-- HASN Core + Social 建表 SQL (PostgreSQL)
-- 生成于: 2026-03-09
-- 包含: hasn_humans, hasn_agents, hasn_conversations,
--       hasn_group_members, hasn_messages, hasn_notifications,
--       hasn_audit_log, hasn_contacts
-- =====================================================

-- ===== 1. hasn_humans (Human 用户表) =====
CREATE TABLE IF NOT EXISTS hasn_humans (
    id VARCHAR(36) NOT NULL,
    star_id VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    huanxing_user_id VARCHAR(64),
    bio TEXT NOT NULL DEFAULT '',
    avatar_url VARCHAR(500),
    phone VARCHAR(128),
    phone_hash VARCHAR(64),
    profile JSONB NOT NULL DEFAULT '{}',
    privacy_rules JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    last_online_at TIMESTAMP WITH TIME ZONE,
    created_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_time TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    UNIQUE (star_id),
    UNIQUE (huanxing_user_id)
);
COMMENT ON TABLE hasn_humans IS 'HASN Human 用户表';
COMMENT ON COLUMN hasn_humans.id IS 'hasn_id (h_uuid)';
COMMENT ON COLUMN hasn_humans.star_id IS '唤星号 (100001 / fuzi)';
COMMENT ON COLUMN hasn_humans.name IS '昵称/显示名';
COMMENT ON COLUMN hasn_humans.huanxing_user_id IS '关联唤星平台 user_id';
COMMENT ON COLUMN hasn_humans.bio IS '个人简介';
COMMENT ON COLUMN hasn_humans.avatar_url IS '头像URL';
COMMENT ON COLUMN hasn_humans.phone IS '手机号 (AES加密存储)';
COMMENT ON COLUMN hasn_humans.phone_hash IS '手机号 SHA256 哈希 (用于搜索)';
COMMENT ON COLUMN hasn_humans.profile IS '完整 Profile Card (JSONB)';
COMMENT ON COLUMN hasn_humans.privacy_rules IS '隐私策略配置';
COMMENT ON COLUMN hasn_humans.status IS '状态: active-活跃 / suspended-停用 / deleted-已删除';
COMMENT ON COLUMN hasn_humans.last_online_at IS '最后在线时间';
COMMENT ON COLUMN hasn_humans.created_time IS '创建时间';
COMMENT ON COLUMN hasn_humans.updated_time IS '更新时间';

CREATE UNIQUE INDEX IF NOT EXISTS idx_human_star ON hasn_humans (star_id);
CREATE INDEX IF NOT EXISTS idx_human_phone_hash ON hasn_humans (phone_hash) WHERE phone_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_human_status ON hasn_humans (status);
CREATE INDEX IF NOT EXISTS idx_human_huanxing ON hasn_humans (huanxing_user_id) WHERE huanxing_user_id IS NOT NULL;

-- ===== 2. hasn_agents (Agent 表) =====
CREATE TABLE IF NOT EXISTS hasn_agents (
    id VARCHAR(36) NOT NULL,
    star_id VARCHAR(40) NOT NULL,
    owner_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    api_key_hash VARCHAR(64) NOT NULL,
    api_key_prefix VARCHAR(16) NOT NULL,
    openclaw_agent_id VARCHAR(64),
    description TEXT NOT NULL DEFAULT '',
    role VARCHAR(20) NOT NULL DEFAULT 'primary',
    capabilities JSONB NOT NULL DEFAULT '[]',
    profile JSONB NOT NULL DEFAULT '{}',
    api_endpoint VARCHAR(500),
    pricing JSONB NOT NULL DEFAULT '{}',
    reputation_score NUMERIC(3, 2) NOT NULL DEFAULT 0.00,
    review_count INTEGER NOT NULL DEFAULT 0,
    total_interactions BIGINT NOT NULL DEFAULT 0,
    experience_credit_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    experience_shared_count INTEGER NOT NULL DEFAULT 0,
    experience_adopted_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    last_active_at TIMESTAMP WITH TIME ZONE,
    created_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_time TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    UNIQUE (star_id),
    FOREIGN KEY(owner_id) REFERENCES hasn_humans (id) ON DELETE CASCADE
);
COMMENT ON TABLE hasn_agents IS 'HASN Agent 表';
COMMENT ON COLUMN hasn_agents.id IS 'hasn_id (a_uuid)';
COMMENT ON COLUMN hasn_agents.star_id IS 'Agent 唤星号 (100001#star)';
COMMENT ON COLUMN hasn_agents.owner_id IS '所属 Human 的 hasn_id';
COMMENT ON COLUMN hasn_agents.name IS 'Agent 显示名';
COMMENT ON COLUMN hasn_agents.api_key_hash IS 'API Key 的 SHA256 哈希';
COMMENT ON COLUMN hasn_agents.api_key_prefix IS 'API Key 前16字符 (用于显示)';
COMMENT ON COLUMN hasn_agents.openclaw_agent_id IS '关联 OpenClaw Agent ID';
COMMENT ON COLUMN hasn_agents.description IS 'Agent 描述';
COMMENT ON COLUMN hasn_agents.role IS '角色: primary-主Agent / specialist-专家 / service-服务';
COMMENT ON COLUMN hasn_agents.capabilities IS '能力列表 (JSONB array)';
COMMENT ON COLUMN hasn_agents.profile IS 'Agent Profile Card (JSONB)';
COMMENT ON COLUMN hasn_agents.api_endpoint IS '外部 Agent 回调地址';
COMMENT ON COLUMN hasn_agents.pricing IS '定价信息';
COMMENT ON COLUMN hasn_agents.reputation_score IS '综合评分 (0.00~5.00)';
COMMENT ON COLUMN hasn_agents.review_count IS '评价总数';
COMMENT ON COLUMN hasn_agents.total_interactions IS '交互总次数';
COMMENT ON COLUMN hasn_agents.experience_credit_score IS '经验贡献信用分';
COMMENT ON COLUMN hasn_agents.experience_shared_count IS '分享的经验总数';
COMMENT ON COLUMN hasn_agents.experience_adopted_count IS '经验被采纳总次数';
COMMENT ON COLUMN hasn_agents.status IS '状态: active-活跃 / disabled-禁用 / revoked-撤销 / deleted-已删除';
COMMENT ON COLUMN hasn_agents.last_active_at IS '最后活跃时间';
COMMENT ON COLUMN hasn_agents.created_time IS '创建时间';
COMMENT ON COLUMN hasn_agents.updated_time IS '更新时间';

CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_star ON hasn_agents (star_id);
CREATE INDEX IF NOT EXISTS idx_agent_owner ON hasn_agents (owner_id);
CREATE INDEX IF NOT EXISTS idx_agent_role ON hasn_agents (role);
CREATE INDEX IF NOT EXISTS idx_agent_status ON hasn_agents (status);
CREATE INDEX IF NOT EXISTS idx_agent_rating ON hasn_agents (reputation_score) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_agent_openclaw ON hasn_agents (openclaw_agent_id) WHERE openclaw_agent_id IS NOT NULL;

-- ===== 3. hasn_conversations (对话/会话表) =====
CREATE TABLE IF NOT EXISTS hasn_conversations (
    id VARCHAR(36) NOT NULL,
    type VARCHAR(10) NOT NULL,
    participant_a VARCHAR(36),
    participant_b VARCHAR(36),
    name VARCHAR(100),
    group_star_id VARCHAR(20),
    group_avatar VARCHAR(500),
    group_description TEXT,
    agent_policy VARCHAR(20) NOT NULL DEFAULT 'free',
    max_members INTEGER NOT NULL DEFAULT 500,
    creator_id VARCHAR(36),
    last_message_at TIMESTAMP WITH TIME ZONE,
    last_message_preview TEXT,
    message_count BIGINT NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_time TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    UNIQUE (group_star_id)
);
COMMENT ON TABLE hasn_conversations IS 'HASN 对话/会话表';
COMMENT ON COLUMN hasn_conversations.id IS '会话ID (UUID)';
COMMENT ON COLUMN hasn_conversations.type IS '类型: direct-私聊 / group-群聊';
COMMENT ON COLUMN hasn_conversations.participant_a IS '参与者A hasn_id';
COMMENT ON COLUMN hasn_conversations.participant_b IS '参与者B hasn_id';
COMMENT ON COLUMN hasn_conversations.name IS '群名称';
COMMENT ON COLUMN hasn_conversations.group_star_id IS '群唤星号 (g:500001)';
COMMENT ON COLUMN hasn_conversations.group_avatar IS '群头像';
COMMENT ON COLUMN hasn_conversations.group_description IS '群描述';
COMMENT ON COLUMN hasn_conversations.agent_policy IS 'Agent发言策略: free-自由 / mention_only-仅@时 / silent-静默 / no_agent-禁止';
COMMENT ON COLUMN hasn_conversations.max_members IS '群最大成员数';
COMMENT ON COLUMN hasn_conversations.creator_id IS '群创建者 hasn_id';
COMMENT ON COLUMN hasn_conversations.last_message_at IS '最后消息时间';
COMMENT ON COLUMN hasn_conversations.last_message_preview IS '最后消息预览';
COMMENT ON COLUMN hasn_conversations.message_count IS '消息总数';
COMMENT ON COLUMN hasn_conversations.status IS '状态: active-活跃 / archived-归档 / deleted-已删除';
COMMENT ON COLUMN hasn_conversations.created_time IS '创建时间';
COMMENT ON COLUMN hasn_conversations.updated_time IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_conv_participant_a ON hasn_conversations (participant_a) WHERE type = 'direct';
CREATE INDEX IF NOT EXISTS idx_conv_participant_b ON hasn_conversations (participant_b) WHERE type = 'direct';
CREATE INDEX IF NOT EXISTS idx_conv_group_star ON hasn_conversations (group_star_id) WHERE group_star_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_conv_last_msg ON hasn_conversations (last_message_at);

-- 1v1 对话唯一约束
CREATE UNIQUE INDEX IF NOT EXISTS idx_conv_direct ON hasn_conversations(
    LEAST(participant_a, participant_b), GREATEST(participant_a, participant_b))
    WHERE type = 'direct';

-- ===== 4. hasn_group_members (群成员表) =====
CREATE TABLE IF NOT EXISTS hasn_group_members (
    id BIGSERIAL NOT NULL,
    conversation_id VARCHAR(36) NOT NULL,
    member_id VARCHAR(36) NOT NULL,
    member_type VARCHAR(10) NOT NULL,
    member_star_id VARCHAR(40) NOT NULL,
    member_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    muted BOOLEAN NOT NULL DEFAULT FALSE,
    joined_at TIMESTAMP WITH TIME ZONE,
    invited_by VARCHAR(36),
    created_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_time TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    CONSTRAINT uq_hasn_group_member UNIQUE (conversation_id, member_id),
    FOREIGN KEY(conversation_id) REFERENCES hasn_conversations (id) ON DELETE CASCADE
);
COMMENT ON TABLE hasn_group_members IS 'HASN 群成员表';
COMMENT ON COLUMN hasn_group_members.id IS '主键 ID';
COMMENT ON COLUMN hasn_group_members.conversation_id IS '群会话ID';
COMMENT ON COLUMN hasn_group_members.member_id IS '成员 hasn_id';
COMMENT ON COLUMN hasn_group_members.member_type IS '成员类型: human-用户 / agent-Agent';
COMMENT ON COLUMN hasn_group_members.member_star_id IS '成员唤星号';
COMMENT ON COLUMN hasn_group_members.member_name IS '成员名称(冗余，方便查询)';
COMMENT ON COLUMN hasn_group_members.role IS '角色: owner-群主 / admin-管理员 / member-成员';
COMMENT ON COLUMN hasn_group_members.muted IS '是否免打扰';
COMMENT ON COLUMN hasn_group_members.joined_at IS '加入时间';
COMMENT ON COLUMN hasn_group_members.invited_by IS '邀请者 hasn_id';
COMMENT ON COLUMN hasn_group_members.created_time IS '创建时间';
COMMENT ON COLUMN hasn_group_members.updated_time IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_group_member_conv ON hasn_group_members (conversation_id);
CREATE INDEX IF NOT EXISTS idx_group_member_user ON hasn_group_members (member_id);

-- ===== 5. hasn_messages (消息表) =====
CREATE TABLE IF NOT EXISTS hasn_messages (
    id BIGSERIAL NOT NULL,
    conversation_id VARCHAR(36) NOT NULL,
    from_id VARCHAR(36) NOT NULL,
    from_type SMALLINT NOT NULL,
    content TEXT NOT NULL,
    content_type SMALLINT NOT NULL DEFAULT 1,
    metadata JSONB,
    reply_to BIGINT,
    status SMALLINT NOT NULL DEFAULT 1,
    created_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_time TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
);
COMMENT ON TABLE hasn_messages IS 'HASN 消息表 (MVP单表，后期按月分区)';
COMMENT ON COLUMN hasn_messages.id IS '消息ID (BIGINT 自增)';
COMMENT ON COLUMN hasn_messages.conversation_id IS '会话ID';
COMMENT ON COLUMN hasn_messages.from_id IS '发送者 hasn_id';
COMMENT ON COLUMN hasn_messages.from_type IS '发送者类型: 1=human 2=agent 3=system';
COMMENT ON COLUMN hasn_messages.content IS '消息内容';
COMMENT ON COLUMN hasn_messages.content_type IS '内容类型: 1=text 2=image 3=file 4=voice 5=rich 6=capability';
COMMENT ON COLUMN hasn_messages.metadata IS '可选元数据 (JSONB)';
COMMENT ON COLUMN hasn_messages.reply_to IS '引用消息ID';
COMMENT ON COLUMN hasn_messages.status IS '状态: 1=sent 2=delivered 3=read 4=deleted';
COMMENT ON COLUMN hasn_messages.created_time IS '创建时间';
COMMENT ON COLUMN hasn_messages.updated_time IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_msg_conv_time ON hasn_messages (conversation_id, created_time);
CREATE INDEX IF NOT EXISTS idx_msg_undelivered ON hasn_messages (conversation_id, status) WHERE status = 1;

-- ===== 6. hasn_notifications (通知队列表) =====
CREATE TABLE IF NOT EXISTS hasn_notifications (
    id BIGSERIAL NOT NULL,
    target_id VARCHAR(36) NOT NULL,
    type VARCHAR(30) NOT NULL,
    title VARCHAR(200) NOT NULL,
    body TEXT,
    data JSONB NOT NULL DEFAULT '{}',
    read BOOLEAN NOT NULL DEFAULT FALSE,
    created_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_time TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
);
COMMENT ON TABLE hasn_notifications IS 'HASN 通知队列表';
COMMENT ON COLUMN hasn_notifications.id IS '主键 ID';
COMMENT ON COLUMN hasn_notifications.target_id IS '通知目标 hasn_id';
COMMENT ON COLUMN hasn_notifications.type IS '类型: contact_request-好友请求 / message_summary-消息摘要 / event_reminder-事件提醒 / system-系统';
COMMENT ON COLUMN hasn_notifications.title IS '通知标题';
COMMENT ON COLUMN hasn_notifications.body IS '通知正文';
COMMENT ON COLUMN hasn_notifications.data IS '附加数据 (JSONB)';
COMMENT ON COLUMN hasn_notifications.read IS '是否已读';
COMMENT ON COLUMN hasn_notifications.created_time IS '创建时间';
COMMENT ON COLUMN hasn_notifications.updated_time IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_notif_target ON hasn_notifications (target_id, read, created_time);

-- ===== 7. hasn_audit_log (审计日志表) =====
CREATE TABLE IF NOT EXISTS hasn_audit_log (
    id BIGSERIAL NOT NULL,
    actor_id VARCHAR(36) NOT NULL,
    actor_type VARCHAR(10) NOT NULL,
    action VARCHAR(50) NOT NULL,
    target_type VARCHAR(20),
    target_id VARCHAR(36),
    details JSONB NOT NULL DEFAULT '{}',
    ip_address VARCHAR(45),
    created_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_time TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
);
COMMENT ON TABLE hasn_audit_log IS 'HASN 审计日志表';
COMMENT ON COLUMN hasn_audit_log.id IS '主键 ID';
COMMENT ON COLUMN hasn_audit_log.actor_id IS '操作者 hasn_id';
COMMENT ON COLUMN hasn_audit_log.actor_type IS '操作者类型: human-用户 / agent-Agent / system-系统';
COMMENT ON COLUMN hasn_audit_log.action IS '操作: register-注册 / login-登录 / send_message-发消息 / add_contact-添加联系人';
COMMENT ON COLUMN hasn_audit_log.target_type IS '目标类型';
COMMENT ON COLUMN hasn_audit_log.target_id IS '目标ID';
COMMENT ON COLUMN hasn_audit_log.details IS '操作详情 (JSONB)';
COMMENT ON COLUMN hasn_audit_log.ip_address IS 'IP地址';
COMMENT ON COLUMN hasn_audit_log.created_time IS '创建时间';
COMMENT ON COLUMN hasn_audit_log.updated_time IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_audit_actor ON hasn_audit_log (actor_id, created_time);
CREATE INDEX IF NOT EXISTS idx_audit_action ON hasn_audit_log (action, created_time);

-- ===== 8. hasn_contacts (联系人关系表 - 三维权限矩阵) =====
CREATE TABLE IF NOT EXISTS hasn_contacts (
    id BIGSERIAL NOT NULL,
    owner_id VARCHAR(36) NOT NULL,
    peer_id VARCHAR(36) NOT NULL,
    peer_type VARCHAR(10) NOT NULL,
    relation_type VARCHAR(20) NOT NULL DEFAULT 'social',
    trust_level SMALLINT NOT NULL DEFAULT 1,
    scope JSONB,
    custom_permissions JSONB NOT NULL DEFAULT '{}',
    nickname VARCHAR(100),
    tags VARCHAR(200)[],
    subscription BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    request_message TEXT,
    auto_expire TIMESTAMP WITH TIME ZONE,
    connected_at TIMESTAMP WITH TIME ZONE,
    last_interaction_at TIMESTAMP WITH TIME ZONE,
    interaction_count INTEGER NOT NULL DEFAULT 0,
    created_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_time TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id),
    CONSTRAINT uq_hasn_contact_relation UNIQUE (owner_id, peer_id, relation_type)
);
COMMENT ON TABLE hasn_contacts IS 'HASN 联系人关系表 (三维权限矩阵)';
COMMENT ON COLUMN hasn_contacts.id IS '主键 ID';
COMMENT ON COLUMN hasn_contacts.owner_id IS '关系拥有者 hasn_id';
COMMENT ON COLUMN hasn_contacts.peer_id IS '对方 hasn_id';
COMMENT ON COLUMN hasn_contacts.peer_type IS '对方类型: human-用户 / agent-Agent';
COMMENT ON COLUMN hasn_contacts.relation_type IS '关系类型: social-社交 / commerce-商业 / service-服务 / professional-专业 / platform-平台';
COMMENT ON COLUMN hasn_contacts.trust_level IS '信任等级: 0=blocked 1=stranger 2=normal 3=trusted 4=owner';
COMMENT ON COLUMN hasn_contacts.scope IS '关系作用域 (JSONB)';
COMMENT ON COLUMN hasn_contacts.custom_permissions IS '自定义权限覆盖';
COMMENT ON COLUMN hasn_contacts.nickname IS '备注名';
COMMENT ON COLUMN hasn_contacts.tags IS '分组标签';
COMMENT ON COLUMN hasn_contacts.subscription IS '是否订阅';
COMMENT ON COLUMN hasn_contacts.status IS '状态: pending-待处理 / connected-已连接 / blocked-已拉黑 / archived-已归档';
COMMENT ON COLUMN hasn_contacts.request_message IS '好友请求附言';
COMMENT ON COLUMN hasn_contacts.auto_expire IS '自动过期时间';
COMMENT ON COLUMN hasn_contacts.connected_at IS '建立连接时间';
COMMENT ON COLUMN hasn_contacts.last_interaction_at IS '最后互动时间';
COMMENT ON COLUMN hasn_contacts.interaction_count IS '互动次数';
COMMENT ON COLUMN hasn_contacts.created_time IS '创建时间';
COMMENT ON COLUMN hasn_contacts.updated_time IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_contact_owner ON hasn_contacts (owner_id);
CREATE INDEX IF NOT EXISTS idx_contact_peer ON hasn_contacts (peer_id);
CREATE INDEX IF NOT EXISTS idx_contact_type ON hasn_contacts (owner_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_contact_level ON hasn_contacts (owner_id, relation_type, trust_level);
CREATE INDEX IF NOT EXISTS idx_contact_status ON hasn_contacts (status);
CREATE INDEX IF NOT EXISTS idx_contact_expire ON hasn_contacts (auto_expire) WHERE auto_expire IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contact_subscription ON hasn_contacts (owner_id) WHERE subscription = TRUE;

-- =====================================================
-- HASN 建表完成 (共 8 张表)
-- =====================================================
