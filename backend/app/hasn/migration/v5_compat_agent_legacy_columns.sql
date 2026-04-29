-- HASN local/test schema compatibility repair
--
-- Some long-lived local dev databases were migrated to the v5 unified entity
-- shape without retaining the deprecated server_id/home_client_id columns that
-- existing DB contract tests still verify for backward compatibility. This
-- migration is intentionally additive and idempotent.

ALTER TABLE public.hasn_agents
  ADD COLUMN IF NOT EXISTS server_id varchar(50),
  ADD COLUMN IF NOT EXISTS home_client_id int8;

CREATE INDEX IF NOT EXISTS idx_hasn_agents_server
  ON public.hasn_agents (server_id);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.table_constraints
    WHERE table_schema = 'public'
      AND table_name = 'hasn_agents'
      AND constraint_name = 'fk_hasn_agents_home_client'
  ) THEN
    ALTER TABLE public.hasn_agents
      ADD CONSTRAINT fk_hasn_agents_home_client
      FOREIGN KEY (home_client_id) REFERENCES public.hasn_clients(id)
      ON DELETE SET NULL;
  END IF;
END $$;

COMMENT ON COLUMN public.hasn_agents.server_id IS '[废弃] 云端 Agent 所在服务器 ID — v5.0 后不再使用';
COMMENT ON COLUMN public.hasn_agents.home_client_id IS '[废弃] 本地 Agent 归属客户端 ID — v5.0 后被统一节点模型取代';
