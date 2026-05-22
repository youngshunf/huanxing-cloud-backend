-- hasn_collections（收藏夹）
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
