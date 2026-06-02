-- =====================================================
-- 好友请求/联系人 新增 add_source「添加来源」列
-- 记录用户从哪种方式添加(搜唤星号/昵称/手机号/社区/Agent发现/扫一扫…)，
-- 与 channel_source(IM 桥接渠道:wechat/feishu/qq/...) 正交。
-- 请求接受后 add_source 复制进 hasn_contacts，好友列表/详情可见来源。
-- 关联 decisions/engineering/2026-05-30-contact-requests-table-split.md
-- =====================================================
BEGIN;
ALTER TABLE "public"."hasn_contact_requests" ADD COLUMN IF NOT EXISTS "add_source" varchar(20);
COMMENT ON COLUMN "public"."hasn_contact_requests"."add_source" IS '添加来源 (search_star_id:搜索唤星号:blue/search_nickname:搜索昵称:cyan/search_phone:手机号搜索:green/community:社区:purple/agent_discovery:Agent发现:orange/qr_code:扫一扫:gold/system:系统:gray/other:其他:default)';

ALTER TABLE "public"."hasn_contacts" ADD COLUMN IF NOT EXISTS "add_source" varchar(20);
COMMENT ON COLUMN "public"."hasn_contacts"."add_source" IS '添加来源 (search_star_id:搜索唤星号:blue/search_nickname:搜索昵称:cyan/search_phone:手机号搜索:green/community:社区:purple/agent_discovery:Agent发现:orange/qr_code:扫一扫:gold/system:系统:gray/other:其他:default)';
COMMIT;
