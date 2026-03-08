-- ============================================================
-- 唤星创作中心 - 数据库表设计
-- 数据库: PostgreSQL | Schema: public
-- 前缀: hx_creator_
-- 日期: 2026-03-05
-- ============================================================

-- ============================================================
-- 1. 创作项目表
-- ============================================================
CREATE TABLE "public"."hx_creator_project" (
    "id"                bigserial PRIMARY KEY,
    "user_id"           bigint NOT NULL,
    "name"              varchar(100) NOT NULL,
    "description"       text,
    "platform"          varchar(50) NOT NULL,
    "platforms"         jsonb,
    "avatar_url"        text,
    "is_active"         boolean DEFAULT false,
    "created_time"      timestamp DEFAULT now(),
    "updated_time"      timestamp
);

COMMENT ON TABLE "public"."hx_creator_project" IS '创作项目表';
COMMENT ON COLUMN "public"."hx_creator_project"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_project"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_project"."name" IS '项目名称（如：小红书美食号）';
COMMENT ON COLUMN "public"."hx_creator_project"."description" IS '项目描述';
COMMENT ON COLUMN "public"."hx_creator_project"."platform" IS '主平台：xiaohongshu/douyin/wechat/weibo/bilibili';
COMMENT ON COLUMN "public"."hx_creator_project"."platforms" IS '多平台JSON数组';
COMMENT ON COLUMN "public"."hx_creator_project"."avatar_url" IS '项目头像URL';
COMMENT ON COLUMN "public"."hx_creator_project"."is_active" IS '是否为当前活跃项目';
COMMENT ON COLUMN "public"."hx_creator_project"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_project"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_project_user" ON "public"."hx_creator_project"("user_id");
CREATE UNIQUE INDEX "idx_hx_creator_project_active" ON "public"."hx_creator_project"("user_id") WHERE is_active = true;


-- ============================================================
-- 2. 账号画像表
-- ============================================================
CREATE TABLE "public"."hx_creator_profile" (
    "id"                        bigserial PRIMARY KEY,
    "project_id"                bigint NOT NULL REFERENCES "public"."hx_creator_project"("id") ON DELETE CASCADE,
    "user_id"                   bigint NOT NULL,
    "niche"                     varchar(100) NOT NULL,
    "sub_niche"                 varchar(100),
    "persona"                   text,
    "target_audience"           text,
    "tone"                      varchar(50),
    "keywords"                  jsonb,
    "bio"                       text,
    "content_pillars"           jsonb,
    "posting_frequency"         varchar(50),
    "best_posting_time"         varchar(100),
    "style_references"          jsonb,
    "taboo_topics"              jsonb,
    "pillar_weights"            jsonb,
    "pillar_weights_updated_at" timestamp,
    "created_time"              timestamp DEFAULT now(),
    "updated_time"              timestamp
);

COMMENT ON TABLE "public"."hx_creator_profile" IS '账号画像表';
COMMENT ON COLUMN "public"."hx_creator_profile"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_profile"."project_id" IS '关联项目ID';
COMMENT ON COLUMN "public"."hx_creator_profile"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_profile"."niche" IS '赛道/领域：美食、旅行、科技、教育';
COMMENT ON COLUMN "public"."hx_creator_profile"."sub_niche" IS '细分赛道：家常菜、烘焙、减脂餐';
COMMENT ON COLUMN "public"."hx_creator_profile"."persona" IS '人设：美食达人/料理小白/专业厨师';
COMMENT ON COLUMN "public"."hx_creator_profile"."target_audience" IS '目标受众描述';
COMMENT ON COLUMN "public"."hx_creator_profile"."tone" IS '内容调性：轻松幽默/专业严谨/温暖治愈';
COMMENT ON COLUMN "public"."hx_creator_profile"."keywords" IS '核心关键词JSON数组';
COMMENT ON COLUMN "public"."hx_creator_profile"."bio" IS '简介文案';
COMMENT ON COLUMN "public"."hx_creator_profile"."content_pillars" IS '内容支柱JSON数组';
COMMENT ON COLUMN "public"."hx_creator_profile"."posting_frequency" IS '发布频率：如每周3-4篇';
COMMENT ON COLUMN "public"."hx_creator_profile"."best_posting_time" IS '最佳发布时间';
COMMENT ON COLUMN "public"."hx_creator_profile"."style_references" IS '风格参考账号JSON数组';
COMMENT ON COLUMN "public"."hx_creator_profile"."taboo_topics" IS '避免话题JSON数组';
COMMENT ON COLUMN "public"."hx_creator_profile"."pillar_weights" IS '支柱权重JSON（根据数据反馈调整）';
COMMENT ON COLUMN "public"."hx_creator_profile"."pillar_weights_updated_at" IS '支柱权重更新时间';
COMMENT ON COLUMN "public"."hx_creator_profile"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_profile"."updated_time" IS '更新时间';

CREATE UNIQUE INDEX "idx_hx_creator_profile_project" ON "public"."hx_creator_profile"("project_id");
CREATE INDEX "idx_hx_creator_profile_user" ON "public"."hx_creator_profile"("user_id");


-- ============================================================
-- 3. 平台账号表
-- ============================================================
CREATE TABLE "public"."hx_creator_account" (
    "id"                  bigserial PRIMARY KEY,
    "project_id"          bigint NOT NULL REFERENCES "public"."hx_creator_project"("id") ON DELETE CASCADE,
    "user_id"             bigint NOT NULL,
    "platform"            varchar(50) NOT NULL,
    "platform_uid"        varchar(100),
    "nickname"            varchar(100),
    "avatar_url"          text,
    "bio"                 text,
    "home_url"            text,
    "followers"           integer DEFAULT 0,
    "following"           integer DEFAULT 0,
    "total_likes"         integer DEFAULT 0,
    "total_favorites"     integer DEFAULT 0,
    "total_comments"      integer DEFAULT 0,
    "total_posts"         integer DEFAULT 0,
    "metrics_json"        jsonb,
    "metrics_updated_at"  timestamp,
    "auth_status"         varchar(20) DEFAULT 'not_configured',
    "is_primary"          boolean DEFAULT false,
    "notes"               text,
    "created_time"        timestamp DEFAULT now(),
    "updated_time"        timestamp
);

COMMENT ON TABLE "public"."hx_creator_account" IS '平台账号表';
COMMENT ON COLUMN "public"."hx_creator_account"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_account"."project_id" IS '关联项目ID';
COMMENT ON COLUMN "public"."hx_creator_account"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_account"."platform" IS '平台标识：xiaohongshu/douyin/wechat/weibo/bilibili';
COMMENT ON COLUMN "public"."hx_creator_account"."platform_uid" IS '平台用户ID';
COMMENT ON COLUMN "public"."hx_creator_account"."nickname" IS '平台昵称';
COMMENT ON COLUMN "public"."hx_creator_account"."avatar_url" IS '头像URL';
COMMENT ON COLUMN "public"."hx_creator_account"."bio" IS '平台简介';
COMMENT ON COLUMN "public"."hx_creator_account"."home_url" IS '主页链接';
COMMENT ON COLUMN "public"."hx_creator_account"."followers" IS '粉丝数';
COMMENT ON COLUMN "public"."hx_creator_account"."following" IS '关注数';
COMMENT ON COLUMN "public"."hx_creator_account"."total_likes" IS '总点赞数';
COMMENT ON COLUMN "public"."hx_creator_account"."total_favorites" IS '总收藏数';
COMMENT ON COLUMN "public"."hx_creator_account"."total_comments" IS '总评论数';
COMMENT ON COLUMN "public"."hx_creator_account"."total_posts" IS '总发布数';
COMMENT ON COLUMN "public"."hx_creator_account"."metrics_json" IS '更多指标JSON';
COMMENT ON COLUMN "public"."hx_creator_account"."metrics_updated_at" IS '指标更新时间';
COMMENT ON COLUMN "public"."hx_creator_account"."auth_status" IS '登录状态：not_configured/active/expired';
COMMENT ON COLUMN "public"."hx_creator_account"."is_primary" IS '是否主账号';
COMMENT ON COLUMN "public"."hx_creator_account"."notes" IS '备注';
COMMENT ON COLUMN "public"."hx_creator_account"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_account"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_account_project" ON "public"."hx_creator_account"("project_id");
CREATE INDEX "idx_hx_creator_account_user" ON "public"."hx_creator_account"("user_id");
CREATE INDEX "idx_hx_creator_account_platform" ON "public"."hx_creator_account"("platform");


-- ============================================================
-- 4. 内容主表
-- ============================================================
CREATE TABLE "public"."hx_creator_content" (
    "id"                bigserial PRIMARY KEY,
    "project_id"        bigint NOT NULL REFERENCES "public"."hx_creator_project"("id") ON DELETE CASCADE,
    "user_id"           bigint NOT NULL,
    "title"             varchar(200),
    "status"            varchar(20) NOT NULL DEFAULT 'idea',
    "target_platforms"  jsonb,
    "pipeline_mode"     varchar(20) DEFAULT 'semi-auto',
    "content_tracks"    varchar(50) DEFAULT 'article',
    "viral_pattern_id"  bigint,
    "metadata"          jsonb,
    "created_time"      timestamp DEFAULT now(),
    "updated_time"      timestamp
);

COMMENT ON TABLE "public"."hx_creator_content" IS '内容创作主表';
COMMENT ON COLUMN "public"."hx_creator_content"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_content"."project_id" IS '关联项目ID';
COMMENT ON COLUMN "public"."hx_creator_content"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_content"."title" IS '内容标题';
COMMENT ON COLUMN "public"."hx_creator_content"."status" IS '状态：idea/researching/drafting/reviewing/ready/published/analyzing/completed/archived';
COMMENT ON COLUMN "public"."hx_creator_content"."target_platforms" IS '目标平台JSON数组';
COMMENT ON COLUMN "public"."hx_creator_content"."pipeline_mode" IS '流水线模式：manual/semi-auto/auto';
COMMENT ON COLUMN "public"."hx_creator_content"."content_tracks" IS '创作轨道：article/video/article,video';
COMMENT ON COLUMN "public"."hx_creator_content"."viral_pattern_id" IS '使用的爆款模式ID';
COMMENT ON COLUMN "public"."hx_creator_content"."metadata" IS '扩展信息JSON';
COMMENT ON COLUMN "public"."hx_creator_content"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_content"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_content_project" ON "public"."hx_creator_content"("project_id");
CREATE INDEX "idx_hx_creator_content_user" ON "public"."hx_creator_content"("user_id");
CREATE INDEX "idx_hx_creator_content_status" ON "public"."hx_creator_content"("status");


-- ============================================================
-- 5. 内容阶段产出表
-- ============================================================
CREATE TABLE "public"."hx_creator_content_stage" (
    "id"            bigserial PRIMARY KEY,
    "content_id"    bigint NOT NULL REFERENCES "public"."hx_creator_content"("id") ON DELETE CASCADE,
    "user_id"       bigint NOT NULL,
    "stage"         varchar(30) NOT NULL,
    "content_text"  text,
    "file_url"      text,
    "status"        varchar(20) DEFAULT 'draft',
    "version"       integer DEFAULT 1,
    "source_type"   varchar(20),
    "metadata"      jsonb,
    "created_time"  timestamp DEFAULT now(),
    "updated_time"  timestamp
);

COMMENT ON TABLE "public"."hx_creator_content_stage" IS '内容阶段产出表';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."content_id" IS '关联内容ID';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."stage" IS '阶段：research/outline/first_draft/final_draft/cover/video_script';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."content_text" IS '产出内容文本';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."file_url" IS '产出文件URL（图片/视频）';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."status" IS '状态：draft/approved/archived';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."version" IS '版本号';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."source_type" IS '来源：ai_generated/human_edited/imported';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."metadata" IS '扩展信息JSON';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_content_stage"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_content_stage_content" ON "public"."hx_creator_content_stage"("content_id");
CREATE INDEX "idx_hx_creator_content_stage_user" ON "public"."hx_creator_content_stage"("user_id");


-- ============================================================
-- 6. 发布记录表
-- ============================================================
CREATE TABLE "public"."hx_creator_publish" (
    "id"                  bigserial PRIMARY KEY,
    "content_id"          bigint NOT NULL REFERENCES "public"."hx_creator_content"("id") ON DELETE CASCADE,
    "account_id"          bigint REFERENCES "public"."hx_creator_account"("id"),
    "user_id"             bigint NOT NULL,
    "platform"            varchar(50) NOT NULL,
    "publish_url"         text,
    "status"              varchar(20) DEFAULT 'pending',
    "method"              varchar(20),
    "error_message"       text,
    "published_at"        timestamp,
    "views"               integer DEFAULT 0,
    "likes"               integer DEFAULT 0,
    "comments"            integer DEFAULT 0,
    "shares"              integer DEFAULT 0,
    "favorites"           integer DEFAULT 0,
    "metrics_json"        jsonb,
    "metrics_updated_at"  timestamp,
    "created_time"        timestamp DEFAULT now(),
    "updated_time"        timestamp
);

COMMENT ON TABLE "public"."hx_creator_publish" IS '发布记录表';
COMMENT ON COLUMN "public"."hx_creator_publish"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_publish"."content_id" IS '关联内容ID';
COMMENT ON COLUMN "public"."hx_creator_publish"."account_id" IS '关联平台账号ID';
COMMENT ON COLUMN "public"."hx_creator_publish"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_publish"."platform" IS '发布平台';
COMMENT ON COLUMN "public"."hx_creator_publish"."publish_url" IS '发布链接';
COMMENT ON COLUMN "public"."hx_creator_publish"."status" IS '状态：pending/published/failed/deleted';
COMMENT ON COLUMN "public"."hx_creator_publish"."method" IS '发布方式：manual/auto/scheduled';
COMMENT ON COLUMN "public"."hx_creator_publish"."error_message" IS '错误信息';
COMMENT ON COLUMN "public"."hx_creator_publish"."published_at" IS '发布时间';
COMMENT ON COLUMN "public"."hx_creator_publish"."views" IS '阅读量';
COMMENT ON COLUMN "public"."hx_creator_publish"."likes" IS '点赞数';
COMMENT ON COLUMN "public"."hx_creator_publish"."comments" IS '评论数';
COMMENT ON COLUMN "public"."hx_creator_publish"."shares" IS '分享数';
COMMENT ON COLUMN "public"."hx_creator_publish"."favorites" IS '收藏数';
COMMENT ON COLUMN "public"."hx_creator_publish"."metrics_json" IS '更多数据指标JSON';
COMMENT ON COLUMN "public"."hx_creator_publish"."metrics_updated_at" IS '指标更新时间';
COMMENT ON COLUMN "public"."hx_creator_publish"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_publish"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_publish_content" ON "public"."hx_creator_publish"("content_id");
CREATE INDEX "idx_hx_creator_publish_user" ON "public"."hx_creator_publish"("user_id");
CREATE INDEX "idx_hx_creator_publish_status" ON "public"."hx_creator_publish"("status");


-- ============================================================
-- 7. 竞品账号表
-- ============================================================
CREATE TABLE "public"."hx_creator_competitor" (
    "id"              bigserial PRIMARY KEY,
    "project_id"      bigint NOT NULL REFERENCES "public"."hx_creator_project"("id") ON DELETE CASCADE,
    "user_id"         bigint NOT NULL,
    "name"            varchar(100) NOT NULL,
    "platform"        varchar(50) NOT NULL,
    "url"             text,
    "follower_count"  integer,
    "avg_likes"       integer,
    "content_style"   text,
    "strengths"       text,
    "notes"           text,
    "tags"            jsonb,
    "last_analyzed"   timestamp,
    "created_time"    timestamp DEFAULT now(),
    "updated_time"    timestamp
);

COMMENT ON TABLE "public"."hx_creator_competitor" IS '竞品账号表';
COMMENT ON COLUMN "public"."hx_creator_competitor"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_competitor"."project_id" IS '关联项目ID';
COMMENT ON COLUMN "public"."hx_creator_competitor"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_competitor"."name" IS '竞品名称';
COMMENT ON COLUMN "public"."hx_creator_competitor"."platform" IS '平台';
COMMENT ON COLUMN "public"."hx_creator_competitor"."url" IS '主页链接';
COMMENT ON COLUMN "public"."hx_creator_competitor"."follower_count" IS '粉丝数';
COMMENT ON COLUMN "public"."hx_creator_competitor"."avg_likes" IS '平均点赞';
COMMENT ON COLUMN "public"."hx_creator_competitor"."content_style" IS '内容风格';
COMMENT ON COLUMN "public"."hx_creator_competitor"."strengths" IS '优势';
COMMENT ON COLUMN "public"."hx_creator_competitor"."notes" IS '备注';
COMMENT ON COLUMN "public"."hx_creator_competitor"."tags" IS '标签JSON数组';
COMMENT ON COLUMN "public"."hx_creator_competitor"."last_analyzed" IS '最后分析时间';
COMMENT ON COLUMN "public"."hx_creator_competitor"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_competitor"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_competitor_project" ON "public"."hx_creator_competitor"("project_id");
CREATE INDEX "idx_hx_creator_competitor_user" ON "public"."hx_creator_competitor"("user_id");


-- ============================================================
-- 8. 草稿箱表
-- ============================================================
CREATE TABLE "public"."hx_creator_draft" (
    "id"                bigserial PRIMARY KEY,
    "project_id"        bigint NOT NULL REFERENCES "public"."hx_creator_project"("id") ON DELETE CASCADE,
    "user_id"           bigint NOT NULL,
    "title"             varchar(200),
    "content"           text NOT NULL,
    "media"             jsonb DEFAULT '[]',
    "tags"              jsonb,
    "target_platforms"  jsonb,
    "metadata"          jsonb,
    "created_time"      timestamp DEFAULT now(),
    "updated_time"      timestamp
);

COMMENT ON TABLE "public"."hx_creator_draft" IS '草稿箱表';
COMMENT ON COLUMN "public"."hx_creator_draft"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_draft"."project_id" IS '关联项目ID';
COMMENT ON COLUMN "public"."hx_creator_draft"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_draft"."title" IS '标题';
COMMENT ON COLUMN "public"."hx_creator_draft"."content" IS '内容';
COMMENT ON COLUMN "public"."hx_creator_draft"."media" IS '媒体文件JSON数组';
COMMENT ON COLUMN "public"."hx_creator_draft"."tags" IS '标签JSON数组';
COMMENT ON COLUMN "public"."hx_creator_draft"."target_platforms" IS '目标平台JSON数组';
COMMENT ON COLUMN "public"."hx_creator_draft"."metadata" IS '扩展信息JSON';
COMMENT ON COLUMN "public"."hx_creator_draft"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_draft"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_draft_project" ON "public"."hx_creator_draft"("project_id");
CREATE INDEX "idx_hx_creator_draft_user" ON "public"."hx_creator_draft"("user_id");


-- ============================================================
-- 9. 素材库表
-- ============================================================
CREATE TABLE "public"."hx_creator_media" (
    "id"              bigserial PRIMARY KEY,
    "project_id"      bigint NOT NULL REFERENCES "public"."hx_creator_project"("id") ON DELETE CASCADE,
    "user_id"         bigint NOT NULL,
    "type"            varchar(20) NOT NULL,
    "url"             text NOT NULL,
    "filename"        varchar(200) NOT NULL,
    "size"            integer,
    "width"           integer,
    "height"          integer,
    "duration"        integer,
    "thumbnail_url"   text,
    "tags"            jsonb,
    "description"     text,
    "created_time"    timestamp DEFAULT now(),
    "updated_time"    timestamp
);

COMMENT ON TABLE "public"."hx_creator_media" IS '素材库表';
COMMENT ON COLUMN "public"."hx_creator_media"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_media"."project_id" IS '关联项目ID';
COMMENT ON COLUMN "public"."hx_creator_media"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_media"."type" IS '类型：image/video/audio/template';
COMMENT ON COLUMN "public"."hx_creator_media"."url" IS '文件URL';
COMMENT ON COLUMN "public"."hx_creator_media"."filename" IS '文件名';
COMMENT ON COLUMN "public"."hx_creator_media"."size" IS '文件大小（字节）';
COMMENT ON COLUMN "public"."hx_creator_media"."width" IS '宽度（像素）';
COMMENT ON COLUMN "public"."hx_creator_media"."height" IS '高度（像素）';
COMMENT ON COLUMN "public"."hx_creator_media"."duration" IS '时长（秒）';
COMMENT ON COLUMN "public"."hx_creator_media"."thumbnail_url" IS '缩略图URL';
COMMENT ON COLUMN "public"."hx_creator_media"."tags" IS '标签JSON数组';
COMMENT ON COLUMN "public"."hx_creator_media"."description" IS '描述';
COMMENT ON COLUMN "public"."hx_creator_media"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_media"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_media_project" ON "public"."hx_creator_media"("project_id");
CREATE INDEX "idx_hx_creator_media_user" ON "public"."hx_creator_media"("user_id");
CREATE INDEX "idx_hx_creator_media_type" ON "public"."hx_creator_media"("type");


-- ============================================================
-- 10. 爆款模式库表
-- ============================================================
CREATE TABLE "public"."hx_creator_viral_pattern" (
    "id"              bigserial PRIMARY KEY,
    "project_id"      bigint REFERENCES "public"."hx_creator_project"("id") ON DELETE SET NULL,
    "user_id"         bigint,
    "platform"        varchar(50),
    "category"        varchar(30) NOT NULL,
    "name"            varchar(100) NOT NULL,
    "description"     text,
    "template"        text,
    "examples"        jsonb,
    "source"          varchar(20),
    "usage_count"     integer DEFAULT 0,
    "success_rate"    real,
    "tags"            jsonb,
    "created_time"    timestamp DEFAULT now(),
    "updated_time"    timestamp
);

COMMENT ON TABLE "public"."hx_creator_viral_pattern" IS '爆款模式库表';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."project_id" IS '关联项目ID（NULL为全局模式）';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."user_id" IS '关联用户ID（NULL为系统级）';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."platform" IS '适用平台';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."category" IS '分类：hook/structure/title/cta/visual/rhythm';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."name" IS '模式名称';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."description" IS '模式描述';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."template" IS '模式模板';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."examples" IS '示例JSON数组';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."source" IS '来源：manual/ai_extracted/community/system';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."usage_count" IS '使用次数';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."success_rate" IS '成功率';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."tags" IS '标签JSON数组';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_viral_pattern"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_viral_pattern_category" ON "public"."hx_creator_viral_pattern"("category");
CREATE INDEX "idx_hx_creator_viral_pattern_platform" ON "public"."hx_creator_viral_pattern"("platform");


-- ============================================================
-- 11. 热榜快照表
-- ============================================================
CREATE TABLE "public"."hx_creator_hot_topic" (
    "id"              bigserial PRIMARY KEY,
    "platform_id"     varchar(50) NOT NULL,
    "platform_name"   varchar(50) NOT NULL,
    "title"           varchar(200) NOT NULL,
    "url"             text,
    "rank"            integer,
    "heat_score"      real,
    "fetch_source"    varchar(50) NOT NULL,
    "fetched_at"      timestamp NOT NULL,
    "batch_date"      varchar(10) NOT NULL,
    "created_time"    timestamp DEFAULT now(),
    "updated_time"    timestamp
);

COMMENT ON TABLE "public"."hx_creator_hot_topic" IS '热榜快照表';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."platform_id" IS '平台标识';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."platform_name" IS '平台名称';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."title" IS '热点标题';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."url" IS '热点链接';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."rank" IS '排名';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."heat_score" IS '热度分数';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."fetch_source" IS '数据来源';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."fetched_at" IS '抓取时间';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."batch_date" IS '批次日期';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_hot_topic"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_hot_topic_batch" ON "public"."hx_creator_hot_topic"("batch_date");
CREATE UNIQUE INDEX "idx_hx_creator_hot_topic_dedup" ON "public"."hx_creator_hot_topic"("platform_id", "url", "batch_date");


-- ============================================================
-- 12. 选题推荐表
-- ============================================================
CREATE TABLE "public"."hx_creator_topic" (
    "id"                bigserial PRIMARY KEY,
    "project_id"        bigint NOT NULL REFERENCES "public"."hx_creator_project"("id") ON DELETE CASCADE,
    "user_id"           bigint NOT NULL,
    "title"             varchar(200) NOT NULL,
    "potential_score"   real,
    "heat_index"        real,
    "reason"            text,
    "keywords"          jsonb,
    "creative_angles"   jsonb,
    "status"            smallint NOT NULL DEFAULT 0,
    "content_id"        bigint,
    "batch_date"        varchar(10),
    "source_uid"        varchar(100),
    "created_time"      timestamp DEFAULT now(),
    "updated_time"      timestamp
);

COMMENT ON TABLE "public"."hx_creator_topic" IS '选题推荐表';
COMMENT ON COLUMN "public"."hx_creator_topic"."id" IS '主键ID';
COMMENT ON COLUMN "public"."hx_creator_topic"."project_id" IS '关联项目ID';
COMMENT ON COLUMN "public"."hx_creator_topic"."user_id" IS '关联用户ID';
COMMENT ON COLUMN "public"."hx_creator_topic"."title" IS '选题标题';
COMMENT ON COLUMN "public"."hx_creator_topic"."potential_score" IS '潜力评分';
COMMENT ON COLUMN "public"."hx_creator_topic"."heat_index" IS '热度指数';
COMMENT ON COLUMN "public"."hx_creator_topic"."reason" IS '推荐理由';
COMMENT ON COLUMN "public"."hx_creator_topic"."keywords" IS '关键词JSON数组';
COMMENT ON COLUMN "public"."hx_creator_topic"."creative_angles" IS '创作角度JSON';
COMMENT ON COLUMN "public"."hx_creator_topic"."status" IS '状态：0-待处理 1-已采纳 2-已跳过';
COMMENT ON COLUMN "public"."hx_creator_topic"."content_id" IS '采纳后关联的内容ID';
COMMENT ON COLUMN "public"."hx_creator_topic"."batch_date" IS '批次日期';
COMMENT ON COLUMN "public"."hx_creator_topic"."source_uid" IS '来源标识';
COMMENT ON COLUMN "public"."hx_creator_topic"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hx_creator_topic"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_creator_topic_project" ON "public"."hx_creator_topic"("project_id");
CREATE INDEX "idx_hx_creator_topic_user" ON "public"."hx_creator_topic"("user_id");
CREATE INDEX "idx_hx_creator_topic_status" ON "public"."hx_creator_topic"("status");
