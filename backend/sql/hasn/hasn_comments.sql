-- hasn_comments（评论）
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
