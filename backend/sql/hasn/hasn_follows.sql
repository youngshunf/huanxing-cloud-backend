-- hasn_follows（关注）
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
