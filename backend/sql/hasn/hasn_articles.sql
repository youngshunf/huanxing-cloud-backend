-- hasn_articles（文章）
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
