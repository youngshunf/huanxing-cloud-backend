-- hasn_collection_items（收藏项）
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
