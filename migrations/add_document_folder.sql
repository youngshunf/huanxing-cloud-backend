-- ====================================================
-- 唤星文档目录管理 - 数据库迁移脚本
-- 1. 创建 huanxing_document_folder 表
-- 2. 给 huanxing_document 表添加 folder_id 列
-- ====================================================

-- 1. 创建目录表
CREATE TABLE IF NOT EXISTS huanxing_document_folder (
    id              BIGSERIAL       PRIMARY KEY,
    uuid            VARCHAR(36)     NOT NULL DEFAULT '',
    user_id         BIGINT          NOT NULL DEFAULT 0,
    name            VARCHAR(255)    NOT NULL DEFAULT '',
    parent_id       BIGINT          DEFAULT NULL,
    path            VARCHAR(1024)   NOT NULL DEFAULT '/',
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    icon            VARCHAR(50)     DEFAULT NULL,
    description     VARCHAR(500)    DEFAULT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ     DEFAULT NULL,
    created_time    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_time    TIMESTAMPTZ     DEFAULT NULL
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_doc_folder_user_id ON huanxing_document_folder (user_id);
CREATE INDEX IF NOT EXISTS idx_doc_folder_parent_id ON huanxing_document_folder (parent_id);
CREATE INDEX IF NOT EXISTS idx_doc_folder_path ON huanxing_document_folder (path varchar_pattern_ops);
CREATE INDEX IF NOT EXISTS idx_doc_folder_uuid ON huanxing_document_folder (uuid);
CREATE INDEX IF NOT EXISTS idx_doc_folder_deleted ON huanxing_document_folder (deleted_at);

-- 自引用外键
ALTER TABLE huanxing_document_folder
    ADD CONSTRAINT fk_doc_folder_parent
    FOREIGN KEY (parent_id)
    REFERENCES huanxing_document_folder(id)
    ON DELETE SET NULL;

-- 注释
COMMENT ON TABLE huanxing_document_folder IS '唤星文档目录表';
COMMENT ON COLUMN huanxing_document_folder.uuid IS '目录UUID';
COMMENT ON COLUMN huanxing_document_folder.user_id IS '用户ID';
COMMENT ON COLUMN huanxing_document_folder.name IS '目录名称';
COMMENT ON COLUMN huanxing_document_folder.parent_id IS '父目录ID（NULL=根目录）';
COMMENT ON COLUMN huanxing_document_folder.path IS '物化路径，如 /1/5/12/';
COMMENT ON COLUMN huanxing_document_folder.sort_order IS '排序权重';
COMMENT ON COLUMN huanxing_document_folder.icon IS '目录图标（emoji或icon名）';
COMMENT ON COLUMN huanxing_document_folder.description IS '目录描述';
COMMENT ON COLUMN huanxing_document_folder.created_at IS '创建时间';
COMMENT ON COLUMN huanxing_document_folder.updated_at IS '更新时间';
COMMENT ON COLUMN huanxing_document_folder.deleted_at IS '删除时间(软删除)';

-- 2. 给文档表添加 folder_id 列（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'huanxing_document' AND column_name = 'folder_id'
    ) THEN
        ALTER TABLE huanxing_document ADD COLUMN folder_id BIGINT DEFAULT NULL;
        COMMENT ON COLUMN huanxing_document.folder_id IS '所属目录ID（NULL=根目录）';
        CREATE INDEX idx_doc_folder_id ON huanxing_document (folder_id);
    END IF;
END $$;

-- 外键（文档→目录）
ALTER TABLE huanxing_document
    ADD CONSTRAINT fk_doc_folder
    FOREIGN KEY (folder_id)
    REFERENCES huanxing_document_folder(id)
    ON DELETE SET NULL;

SELECT 'Migration complete: huanxing_document_folder table created, folder_id column added to huanxing_document' AS status;
