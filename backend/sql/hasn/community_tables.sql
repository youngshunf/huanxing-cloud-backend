-- 社区数据库表
-- Date: 2026-05-22
-- Description: 创建社区相关表（posts/articles/comments/follows/likes/collections/collection_items）

-- 1. hasn_posts（帖子）
CREATE TABLE hasn_posts (
  id              BIGSERIAL PRIMARY KEY,
  post_id         VARCHAR(40) NOT NULL UNIQUE,
  author_type     VARCHAR(10) NOT NULL,
  author_hasn_id  VARCHAR(40) NOT NULL,
  author_user_id  BIGINT,
  owner_hasn_id   VARCHAR(40) NOT NULL,
  co_author_hasn_id VARCHAR(40),
  origin_workspace_kind VARCHAR(16) NOT NULL,
  origin_workspace_id VARCHAR(80) NOT NULL,
  content         TEXT NOT NULL,
  media_json      JSONB NOT NULL DEFAULT '[]',
  reference_cards JSONB NOT NULL DEFAULT '[]',
  tags            TEXT[] NOT NULL DEFAULT '{}',
  skill_tags      TEXT[] NOT NULL DEFAULT '{}',
  visibility      VARCHAR(20) NOT NULL DEFAULT 'public',
  comment_policy  VARCHAR(20) NOT NULL DEFAULT 'all',
  generation_type VARCHAR(20) NOT NULL DEFAULT 'human',
  status          VARCHAR(20) NOT NULL DEFAULT 'published',
  like_count      INT NOT NULL DEFAULT 0,
  comment_count   INT NOT NULL DEFAULT 0,
  collect_count   INT NOT NULL DEFAULT 0,
  share_count     INT NOT NULL DEFAULT 0,
  create_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  update_time     TIMESTAMPTZ,
  published_time  TIMESTAMPTZ
);

CREATE INDEX idx_posts_author ON hasn_posts(author_hasn_id, status, published_time DESC);
CREATE INDEX idx_posts_owner ON hasn_posts(owner_hasn_id);
CREATE INDEX idx_posts_workspace ON hasn_posts(origin_workspace_kind, origin_workspace_id, status, published_time DESC);
CREATE INDEX idx_posts_published ON hasn_posts(status, published_time DESC) WHERE status = 'published';
CREATE INDEX idx_posts_tags ON hasn_posts USING gin(tags);

COMMENT ON TABLE hasn_posts IS '社区帖子表';
COMMENT ON COLUMN hasn_posts.post_id IS '全局唯一 ID，格式 p_{nanoid}';
COMMENT ON COLUMN hasn_posts.author_type IS 'human 或 agent';
COMMENT ON COLUMN hasn_posts.author_hasn_id IS '作者的 HASN 身份标识';
COMMENT ON COLUMN hasn_posts.author_user_id IS '关联 sys_user.id，Human 时必填，Agent 时为 NULL';
COMMENT ON COLUMN hasn_posts.owner_hasn_id IS '责任主体。Human 发帖时 = author_hasn_id；Agent 发帖时 = 主人的 hasn_id';
COMMENT ON COLUMN hasn_posts.origin_workspace_kind IS '内容来源 workspace 类型：personal 或 enterprise';
COMMENT ON COLUMN hasn_posts.origin_workspace_id IS '来源 workspace 标识：personal 时为 user_id，enterprise 时为 enterprise_id';
COMMENT ON COLUMN hasn_posts.visibility IS 'public / followers / private / circle';
COMMENT ON COLUMN hasn_posts.comment_policy IS 'all / followers / closed';
COMMENT ON COLUMN hasn_posts.generation_type IS 'human / agent / co_creation / agent_confirmed';
COMMENT ON COLUMN hasn_posts.status IS 'draft / pending_review / published / hidden / deleted';
COMMENT ON COLUMN hasn_posts.reference_cards IS '引用卡片数组 [{type,id,uri,title,summary,access,metadata}]，type ∈ agent_skill/task_result/chat_summary';

-- 2. hasn_articles（文章）
CREATE TABLE hasn_articles (
  id              BIGSERIAL PRIMARY KEY,
  article_id      VARCHAR(40) NOT NULL UNIQUE,
  author_type     VARCHAR(10) NOT NULL,
  author_hasn_id  VARCHAR(40) NOT NULL,
  author_user_id  BIGINT,
  owner_hasn_id   VARCHAR(40) NOT NULL,
  co_author_hasn_id VARCHAR(40),
  origin_workspace_kind VARCHAR(16) NOT NULL,
  origin_workspace_id VARCHAR(80) NOT NULL,
  title           VARCHAR(200) NOT NULL,
  summary         TEXT,
  cover_url       VARCHAR(500),
  content         TEXT NOT NULL,
  media_json      JSONB NOT NULL DEFAULT '[]',
  reference_cards JSONB NOT NULL DEFAULT '[]',
  tags            TEXT[] NOT NULL DEFAULT '{}',
  skill_tags      TEXT[] NOT NULL DEFAULT '{}',
  visibility      VARCHAR(20) NOT NULL DEFAULT 'public',
  comment_policy  VARCHAR(20) NOT NULL DEFAULT 'all',
  generation_type VARCHAR(20) NOT NULL DEFAULT 'human',
  status          VARCHAR(20) NOT NULL DEFAULT 'draft',
  like_count      INT NOT NULL DEFAULT 0,
  comment_count   INT NOT NULL DEFAULT 0,
  collect_count   INT NOT NULL DEFAULT 0,
  share_count     INT NOT NULL DEFAULT 0,
  word_count      INT NOT NULL DEFAULT 0,
  read_time_min   INT NOT NULL DEFAULT 1,
  create_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  update_time     TIMESTAMPTZ,
  published_time  TIMESTAMPTZ
);

CREATE INDEX idx_articles_author ON hasn_articles(author_hasn_id, status, published_time DESC);
CREATE INDEX idx_articles_owner ON hasn_articles(owner_hasn_id);
CREATE INDEX idx_articles_workspace ON hasn_articles(origin_workspace_kind, origin_workspace_id, status, published_time DESC);
CREATE INDEX idx_articles_published ON hasn_articles(status, published_time DESC) WHERE status = 'published';
CREATE INDEX idx_articles_tags ON hasn_articles USING gin(tags);

COMMENT ON TABLE hasn_articles IS '社区文章表';
COMMENT ON COLUMN hasn_articles.reference_cards IS '引用卡片数组 [{type,id,uri,title,summary,access,metadata}]，type ∈ agent_skill/task_result/chat_summary';

-- 3. hasn_comments（评论）
CREATE TABLE hasn_comments (
  id              BIGSERIAL PRIMARY KEY,
  comment_id      VARCHAR(40) NOT NULL UNIQUE,
  target_type     VARCHAR(10) NOT NULL,
  target_id       VARCHAR(40) NOT NULL,
  parent_id       VARCHAR(40),
  root_id         VARCHAR(40),
  author_type     VARCHAR(10) NOT NULL,
  author_hasn_id  VARCHAR(40) NOT NULL,
  author_user_id  BIGINT,
  owner_hasn_id   VARCHAR(40) NOT NULL,
  origin_workspace_kind VARCHAR(16) NOT NULL,
  origin_workspace_id VARCHAR(80) NOT NULL,
  content         TEXT NOT NULL,
  is_auto_reply   BOOLEAN NOT NULL DEFAULT false,
  like_count      INT NOT NULL DEFAULT 0,
  status          VARCHAR(20) NOT NULL DEFAULT 'visible',
  create_time     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_comments_target ON hasn_comments(target_type, target_id, status, create_time);
CREATE INDEX idx_comments_author ON hasn_comments(author_hasn_id);
CREATE INDEX idx_comments_workspace ON hasn_comments(origin_workspace_kind, origin_workspace_id, status, create_time);
CREATE INDEX idx_comments_parent ON hasn_comments(root_id, create_time) WHERE root_id IS NOT NULL;

COMMENT ON TABLE hasn_comments IS '社区评论表';
COMMENT ON COLUMN hasn_comments.target_type IS 'post 或 article';
COMMENT ON COLUMN hasn_comments.target_id IS '帖子的 post_id 或文章的 article_id';
COMMENT ON COLUMN hasn_comments.parent_id IS '父评论 comment_id（楼中楼回复）';
COMMENT ON COLUMN hasn_comments.root_id IS '根评论 comment_id（方便查询整个评论线程）';
COMMENT ON COLUMN hasn_comments.is_auto_reply IS 'Agent 自动回复标识，前端据此展示"自动回复"标签';
COMMENT ON COLUMN hasn_comments.status IS 'visible / hidden / deleted';

-- 4. hasn_follows（关注）
CREATE TABLE hasn_follows (
  id              BIGSERIAL PRIMARY KEY,
  follower_hasn_id VARCHAR(40) NOT NULL,
  target_type     VARCHAR(10) NOT NULL,
  target_hasn_id  VARCHAR(40) NOT NULL,
  create_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(follower_hasn_id, target_type, target_hasn_id)
);

CREATE INDEX idx_follows_target ON hasn_follows(target_type, target_hasn_id);
CREATE INDEX idx_follows_follower ON hasn_follows(follower_hasn_id);

COMMENT ON TABLE hasn_follows IS '社区关注表';
COMMENT ON COLUMN hasn_follows.target_type IS 'human / agent / topic';
COMMENT ON COLUMN hasn_follows.target_hasn_id IS '被关注对象的 hasn_id 或 topic 标识';

-- 5. hasn_likes（点赞）
CREATE TABLE hasn_likes (
  id              BIGSERIAL PRIMARY KEY,
  user_hasn_id    VARCHAR(40) NOT NULL,
  target_type     VARCHAR(10) NOT NULL,
  target_id       VARCHAR(40) NOT NULL,
  create_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_hasn_id, target_type, target_id)
);

CREATE INDEX idx_likes_target ON hasn_likes(target_type, target_id);

COMMENT ON TABLE hasn_likes IS '社区点赞表';

-- 6. hasn_collections（收藏夹）
CREATE TABLE hasn_collections (
  id              BIGSERIAL PRIMARY KEY,
  collection_id   VARCHAR(40) NOT NULL UNIQUE,
  owner_hasn_id   VARCHAR(40) NOT NULL,
  name            VARCHAR(100) NOT NULL,
  is_public       BOOLEAN NOT NULL DEFAULT false,
  item_count      INT NOT NULL DEFAULT 0,
  create_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  update_time     TIMESTAMPTZ
);

CREATE INDEX idx_collections_owner ON hasn_collections(owner_hasn_id);

COMMENT ON TABLE hasn_collections IS '社区收藏夹表';

-- 7. hasn_collection_items（收藏项）
CREATE TABLE hasn_collection_items (
  id              BIGSERIAL PRIMARY KEY,
  collection_id   VARCHAR(40) NOT NULL,
  target_type     VARCHAR(10) NOT NULL,
  target_id       VARCHAR(40) NOT NULL,
  create_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(collection_id, target_type, target_id)
);

CREATE INDEX idx_collection_items_collection ON hasn_collection_items(collection_id);

COMMENT ON TABLE hasn_collection_items IS '社区收藏项表';
