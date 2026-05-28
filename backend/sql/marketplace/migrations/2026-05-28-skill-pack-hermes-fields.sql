-- Marketplace skill-pack Hermes bundle fields.

ALTER TABLE "public"."marketplace_template_version"
  ADD COLUMN IF NOT EXISTS "bundle_slug" varchar(100),
  ADD COLUMN IF NOT EXISTS "command_key" varchar(100),
  ADD COLUMN IF NOT EXISTS "hermes_bundle_json" jsonb,
  ADD COLUMN IF NOT EXISTS "hermes_yaml" text,
  ADD COLUMN IF NOT EXISTS "content_hash" varchar(128);

CREATE INDEX IF NOT EXISTS "idx_marketplace_template_version_bundle_slug"
  ON "public"."marketplace_template_version"("bundle_slug");
CREATE INDEX IF NOT EXISTS "idx_marketplace_template_version_content_hash"
  ON "public"."marketplace_template_version"("content_hash");

-- Backfill legacy HASN skill bundles into marketplace skill packs.
-- The legacy table stays in place for compatibility, but marketplace is the
-- v2.1 authority for Hermes-materializable skill packs.
INSERT INTO "public"."marketplace_template" (
  "template_id",
  "namespace",
  "slug",
  "template_type",
  "name",
  "description",
  "author_id",
  "pricing_type",
  "price",
  "is_private",
  "is_official",
  "download_count",
  "source_type",
  "created_time",
  "updated_time"
)
SELECT
  'hasn-skill-bundle:' || b."id" AS "template_id",
  'hasn-skill-bundle' AS "namespace",
  b."name" AS "slug",
  'skill_pack' AS "template_type",
  COALESCE(NULLIF(b."display_name", ''), b."name") AS "name",
  b."description",
  h."user_id" AS "author_id",
  'free' AS "pricing_type",
  0 AS "price",
  true AS "is_private",
  false AS "is_official",
  0 AS "download_count",
  'legacy_hasn_skill_bundle' AS "source_type",
  COALESCE(b."created_time", now()) AS "created_time",
  now() AS "updated_time"
FROM "public"."hasn_skill_bundle" b
LEFT JOIN "public"."hasn_humans" h
  ON h."hasn_id" = b."owner_id"
ON CONFLICT ("template_id") DO UPDATE SET
  "name" = EXCLUDED."name",
  "description" = EXCLUDED."description",
  "author_id" = COALESCE(EXCLUDED."author_id", "public"."marketplace_template"."author_id"),
  "template_type" = 'skill_pack',
  "is_private" = true,
  "updated_time" = now();

INSERT INTO "public"."marketplace_template_version" (
  "template_id",
  "version",
  "changelog",
  "skill_dependencies_versioned",
  "bundle_slug",
  "command_key",
  "hermes_bundle_json",
  "hermes_yaml",
  "content_hash",
  "file_hash",
  "is_latest",
  "published_at",
  "created_time",
  "updated_time"
)
SELECT
  'hasn-skill-bundle:' || b."id" AS "template_id",
  '1.0.0' AS "version",
  'Migrated from hasn_skill_bundle' AS "changelog",
  jsonb_build_object('skills', b."skill_ids") AS "skill_dependencies_versioned",
  b."name" AS "bundle_slug",
  '/' || b."name" AS "command_key",
  jsonb_build_object(
    'bundle_slug', b."name",
    'command_key', '/' || b."name",
    'skills', b."skill_ids",
    'instruction', b."instruction",
    'source_type', 'legacy_hasn_skill_bundle'
  ) AS "hermes_bundle_json",
  concat(
    'name: ', b."name", E'\n',
    'command: /', b."name", E'\n',
    'skills:', E'\n',
    COALESCE((
      SELECT string_agg('  - ' || skill.value, E'\n')
      FROM jsonb_array_elements_text(b."skill_ids") AS skill(value)
    ), ''),
    CASE
      WHEN b."instruction" IS NULL OR b."instruction" = '' THEN ''
      ELSE E'\ninstruction: |\n  ' || replace(b."instruction", E'\n', E'\n  ')
    END,
    E'\n'
  ) AS "hermes_yaml",
  'sha256:legacy-' || md5(
    concat_ws(
      '|',
      b."id"::text,
      b."owner_id",
      b."name",
      b."skill_ids"::text,
      COALESCE(b."instruction", ''),
      COALESCE(b."updated_time"::text, b."created_time"::text, '')
    )
  ) AS "content_hash",
  'sha256:legacy-' || md5(
    concat_ws(
      '|',
      b."id"::text,
      b."owner_id",
      b."name",
      b."skill_ids"::text,
      COALESCE(b."instruction", '')
    )
  ) AS "file_hash",
  true AS "is_latest",
  COALESCE(b."updated_time", b."created_time", now()) AS "published_at",
  COALESCE(b."created_time", now()) AS "created_time",
  now() AS "updated_time"
FROM "public"."hasn_skill_bundle" b
ON CONFLICT ("template_id", "version") DO UPDATE SET
  "skill_dependencies_versioned" = EXCLUDED."skill_dependencies_versioned",
  "bundle_slug" = EXCLUDED."bundle_slug",
  "command_key" = EXCLUDED."command_key",
  "hermes_bundle_json" = EXCLUDED."hermes_bundle_json",
  "hermes_yaml" = EXCLUDED."hermes_yaml",
  "content_hash" = EXCLUDED."content_hash",
  "file_hash" = EXCLUDED."file_hash",
  "is_latest" = true,
  "updated_time" = now();
