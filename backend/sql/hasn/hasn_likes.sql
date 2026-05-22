-- hasn_likes（点赞）
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
