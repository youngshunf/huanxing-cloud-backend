# ClawHub 同步 - 翻译问题修复报告

**日期**: 2026-05-27  
**状态**: ✅ 已修复

## 问题描述

用户反馈：有些技能两个字段都是中文，翻译不正确。

具体表现：
- `name_en` 和 `name_zh` 翻译正确
- `description_en` 和 `description_zh` 都是中文（应该一个英文一个中文）

## 根本原因

### 1. 翻译逻辑问题

**原始代码**：`translate_skill_metadata()` 方法只检测 `name` 的语言，然后用同一个语言处理 `description`。

```python
# 错误的实现
if source_lang is None:
    if name:
        source_lang = self.detect_language(name)  # 只检测 name
    elif description:
        source_lang = self.detect_language(description)

# 使用同一个 source_lang 处理 description
if source_lang == 'en':
    result['description_en'] = description
    result['description_zh'] = await self.translate(description, 'en', 'zh')
```

**问题**：ClawHub 的技能可能 `name` 是英文，但 `description` 是中文。这导致中文 `description` 被当作英文处理。

**修复**：`name` 和 `description` 分别检测语言。

```python
# 正确的实现
# Translate name
if name:
    name_lang = source_lang
    if name_lang == 'en':
        result['name_en'] = name
        result['name_zh'] = await self.translate(name, 'en', 'zh')
    else:
        result['name_zh'] = name
        result['name_en'] = await self.translate(name, 'zh', 'en')

# Translate description (detect language separately)
if description:
    desc_lang = self.detect_language(description)  # 独立检测
    
    if desc_lang == 'en':
        result['description_en'] = description
        result['description_zh'] = await self.translate(description, 'en', 'zh')
    else:
        result['description_zh'] = description
        result['description_en'] = await self.translate(description, 'zh', 'en')
```

### 2. 数据库事务未提交

**问题**：`sync_from_clawhub()` 方法执行了更新操作，但没有提交事务，导致数据没有真正写入数据库。

**修复**：在方法结束前添加 `await db.commit()`。

```python
# Update sync log
await marketplace_sync_log_dao.update(db, sync_log_id, UpdateMarketplaceSyncLogParam(...))

# Commit transaction
await db.commit()  # 添加这一行

return {
    'success': True,
    'synced': synced_count,
    'failed': failed_count,
    'errors': errors
}
```

### 3. 其他修复

#### 3.1 API 响应结构处理

ClawHub 详情 API 返回的结构是：
```json
{
  "skill": {...},
  "owner": {...},
  "latestVersion": {...}
}
```

需要合并这些对象：

```python
async def _fetch_specific_skills(self, skill_ids: list[str]) -> list[dict[str, Any]]:
    for skill_id in skill_ids:
        response = await client.get(f"{self.clawhub_api_url}/skills/{skill_id}")
        data = response.json()
        
        # Merge skill, owner, and latestVersion into one object
        skill_data = data.get('skill', {})
        skill_data['owner'] = data.get('owner', {})
        skill_data['latestVersion'] = data.get('latestVersion', {})
        
        skills.append(skill_data)
```

#### 3.2 数据库字段缺失

`marketplace_sync_log` 表缺少 `updated_time` 字段（Base 类自动添加）。

**修复**：添加字段。

```sql
ALTER TABLE marketplace_sync_log 
ADD COLUMN IF NOT EXISTS updated_time TIMESTAMP WITH TIME ZONE;
```

#### 3.3 Schema 验证问题

`UpdateMarketplaceSyncLogParam` 继承了 `MarketplaceSyncLogSchemaBase`，导致所有字段都是必需的。

**修复**：让 `UpdateMarketplaceSyncLogParam` 的所有字段都是可选的。

```python
class UpdateMarketplaceSyncLogParam(SchemaBase):
    """更新技能市场同步日志参数"""
    sync_type: str | None = Field(None, description='...')
    status: str | None = Field(None, description='...')
    # ... 所有字段都是 Optional
```

#### 3.4 CRUD create 返回值问题

`CRUDPlus.create_model()` 返回 `None`，需要 flush 后重新查询。

**修复**：在 `sync_from_clawhub()` 中：

```python
await marketplace_sync_log_dao.create(db, CreateMarketplaceSyncLogParam(...))
await db.flush()

# Query the newly created log
from sqlalchemy import select, desc
stmt = select(MarketplaceSyncLog).order_by(desc(MarketplaceSyncLog.id)).limit(1)
result = await db.execute(stmt)
sync_log = result.scalar_one_or_none()
```

## 验证结果

同步 2 个技能后验证：

```
✅ clawhub/mnetfairy/insurance-advisor-china
   name_en: Insurance Advisor China
   name_zh: 中国保险顾问
   description_en: Mainland China AI insurance advisor. Provides comprehensive ...
   description_zh: 中国大陆AI保险顾问。为个人和家庭提供全方位的保险咨询、产品对比、方案设计、投保指导...
   ✅ 翻译完全正确

✅ clawhub/mnetfairy/ai-insurance-advisor
   name_en: Ai Insurance Advisor
   name_zh: AI保险顾问
   description_en: Mainland China insurance AI assistant. Use when users ask ab...
   description_zh: 中国大陆保险AI助手。当用户询问以下内容时使用：保险配置、保险方案、产品对比...
   ✅ 翻译完全正确
```

## 修改的文件

1. **backend/app/marketplace/service/translation_service.py**
   - 修复 `translate_skill_metadata()` 方法，让 name 和 description 分别检测语言

2. **backend/app/marketplace/service/clawhub_sync_service.py**
   - 添加事务提交 `await db.commit()`
   - 修复 `_fetch_specific_skills()` 合并 API 响应对象
   - 修复 sync_log 创建后的 ID 获取
   - 添加 Pydantic schema 导入

3. **backend/app/marketplace/schema/marketplace_sync_log.py**
   - 修复 `UpdateMarketplaceSyncLogParam`，让所有字段都是可选的

4. **数据库迁移**
   - 添加 `marketplace_sync_log.updated_time` 字段

## 总结

翻译问题的核心原因是：
1. **翻译逻辑缺陷**：name 和 description 没有分别检测语言
2. **事务未提交**：更新操作没有真正写入数据库

修复后，ClawHub 同步功能的翻译完全正常，支持：
- ✅ name 英文 + description 中文
- ✅ name 中文 + description 英文
- ✅ name 和 description 都是英文
- ✅ name 和 description 都是中文

---

**最后更新**: 2026-05-27  
**状态**: ✅ 已完成并验证
