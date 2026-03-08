-- =====================================================
-- 创作中心 - 字典数据初始化 SQL
-- 手动修正: 简化 name 字段使其符合 varchar(32) 限制
-- =====================================================

-- 1. 平台账号-登录状态
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES ('账号登录状态', 'creator_auth_status', '平台账号登录状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

DO $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM sys_dict_type WHERE code = 'creator_auth_status' LIMIT 1;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_auth_status' AND value = 'not_configured') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_auth_status', '未配置', 'not_configured', 'default', 1, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_auth_status' AND value = 'active') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_auth_status', '已登录', 'active', 'green', 2, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_auth_status' AND value = 'expired') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_auth_status', '已过期', 'expired', 'red', 3, 1, v_id, '', NOW());
    END IF;
END $$;

-- 2. 内容状态
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES ('内容状态', 'creator_content_status', '内容创作生命周期状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

DO $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM sys_dict_type WHERE code = 'creator_content_status' LIMIT 1;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_content_status' AND value = 'idea') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_content_status', '灵感', 'idea', 'default', 1, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_content_status' AND value = 'researching') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_content_status', '调研中', 'researching', 'processing', 2, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_content_status' AND value = 'drafting') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_content_status', '撰写中', 'drafting', 'processing', 3, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_content_status' AND value = 'reviewing') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_content_status', '审核中', 'reviewing', 'warning', 4, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_content_status' AND value = 'ready') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_content_status', '待发布', 'ready', 'cyan', 5, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_content_status' AND value = 'published') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_content_status', '已发布', 'published', 'green', 6, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_content_status' AND value = 'analyzing') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_content_status', '分析中', 'analyzing', 'blue', 7, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_content_status' AND value = 'completed') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_content_status', '已完成', 'completed', 'success', 8, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_content_status' AND value = 'archived') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_content_status', '已归档', 'archived', 'default', 9, 1, v_id, '', NOW());
    END IF;
END $$;

-- 3. 阶段产出状态
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES ('阶段产出状态', 'creator_stage_status', '内容阶段产出审批状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

DO $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM sys_dict_type WHERE code = 'creator_stage_status' LIMIT 1;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_stage_status' AND value = 'draft') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_stage_status', '草稿', 'draft', 'default', 1, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_stage_status' AND value = 'approved') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_stage_status', '已通过', 'approved', 'green', 2, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_stage_status' AND value = 'archived') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_stage_status', '已归档', 'archived', 'default', 3, 1, v_id, '', NOW());
    END IF;
END $$;

-- 4. 阶段来源类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES ('产出来源类型', 'creator_source_type', '内容阶段产出来源', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

DO $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM sys_dict_type WHERE code = 'creator_source_type' LIMIT 1;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_source_type' AND value = 'ai_generated') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_source_type', 'AI生成', 'ai_generated', 'blue', 1, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_source_type' AND value = 'human_edited') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_source_type', '人工编辑', 'human_edited', 'green', 2, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_source_type' AND value = 'imported') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_source_type', '外部导入', 'imported', 'orange', 3, 1, v_id, '', NOW());
    END IF;
END $$;

-- 5. 素材类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES ('素材类型', 'creator_media_type', '素材库资源类型', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

DO $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM sys_dict_type WHERE code = 'creator_media_type' LIMIT 1;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_media_type' AND value = 'image') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_media_type', '图片', 'image', 'blue', 1, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_media_type' AND value = 'video') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_media_type', '视频', 'video', 'purple', 2, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_media_type' AND value = 'audio') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_media_type', '音频', 'audio', 'orange', 3, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_media_type' AND value = 'template') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_media_type', '模板', 'template', 'cyan', 4, 1, v_id, '', NOW());
    END IF;
END $$;

-- 6. 发布状态
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES ('发布状态', 'creator_publish_status', '内容发布状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

DO $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM sys_dict_type WHERE code = 'creator_publish_status' LIMIT 1;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_publish_status' AND value = 'pending') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_publish_status', '待发布', 'pending', 'default', 1, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_publish_status' AND value = 'published') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_publish_status', '已发布', 'published', 'green', 2, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_publish_status' AND value = 'failed') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_publish_status', '发布失败', 'failed', 'red', 3, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_publish_status' AND value = 'deleted') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_publish_status', '已删除', 'deleted', 'default', 4, 1, v_id, '', NOW());
    END IF;
END $$;

-- 7. 选题状态
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES ('选题状态', 'creator_topic_status', '选题推荐处理状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

DO $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM sys_dict_type WHERE code = 'creator_topic_status' LIMIT 1;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_topic_status' AND value = '0') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_topic_status', '待处理', '0', 'default', 1, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_topic_status' AND value = '1') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_topic_status', '已采纳', '1', 'green', 2, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_topic_status' AND value = '2') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_topic_status', '已跳过', '2', 'default', 3, 1, v_id, '', NOW());
    END IF;
END $$;

-- 8. 爆款模式分类
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES ('爆款模式分类', 'creator_viral_category', '爆款模式分类', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

DO $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM sys_dict_type WHERE code = 'creator_viral_category' LIMIT 1;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_viral_category' AND value = 'hook') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_viral_category', '钩子', 'hook', 'red', 1, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_viral_category' AND value = 'structure') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_viral_category', '结构', 'structure', 'blue', 2, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_viral_category' AND value = 'title') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_viral_category', '标题', 'title', 'orange', 3, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_viral_category' AND value = 'cta') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_viral_category', '行动号召', 'cta', 'green', 4, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_viral_category' AND value = 'visual') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_viral_category', '视觉', 'visual', 'purple', 5, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_viral_category' AND value = 'rhythm') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_viral_category', '节奏', 'rhythm', 'cyan', 6, 1, v_id, '', NOW());
    END IF;
END $$;

-- 9. 平台类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES ('创作平台', 'creator_platform', '自媒体平台类型', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

DO $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM sys_dict_type WHERE code = 'creator_platform' LIMIT 1;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_platform' AND value = 'xiaohongshu') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_platform', '小红书', 'xiaohongshu', 'red', 1, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_platform' AND value = 'douyin') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_platform', '抖音', 'douyin', 'default', 2, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_platform' AND value = 'wechat') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_platform', '微信公众号', 'wechat', 'green', 3, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_platform' AND value = 'weibo') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_platform', '微博', 'weibo', 'orange', 4, 1, v_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_platform' AND value = 'bilibili') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time) VALUES ('creator_platform', 'B站', 'bilibili', 'blue', 5, 1, v_id, '', NOW());
    END IF;
END $$;

-- =====================================================
-- 字典数据初始化完成
-- =====================================================
