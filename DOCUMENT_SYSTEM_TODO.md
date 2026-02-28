# 唤星文档系统开发任务清单

## 已完成 ✅
- [x] 数据库表设计和建表（3个表）
- [x] 基础 CRUD 代码生成（model/schema/crud/service/api）
- [x] 菜单和字典 SQL 生成并执行
- [x] 文档创建接口增强 - 支持 tags、auto_share、自动计算 word_count/summary
- [x] 文档更新接口增强 - 支持 append、save_version、自动触发版本保存
- [x] 自动保存接口 - POST/GET /api/v1/huanxing/docs/{id}/autosave
- [x] 版本历史接口 - GET /versions、GET /versions/{version}、POST /versions/{version}/restore
- [x] JWT 认证集成 - 所有接口使用 request.user.id

## 待开发功能

### 1. 后端 API 增强

#### 1.1 文档创建接口增强 (POST /api/v1/huanxing/docs) ✅
- [x] 支持 `tags` 字段（JSON 数组）
- [x] 支持 `auto_share` 参数自动生成分享链接
  - 生成随机 `share_token`（32位随机字符串）
  - 可选设置 `share_password`（bcrypt 加密）
  - 设置 `share_permission`（view/edit）
  - 计算 `share_expires_at`（当前时间 + expires_hours）
- [x] 返回完整分享链接：`https://huanxing.ai.dcfuture.cn/share/{share_token}`
- [x] 自动计算 `word_count`（去除 Markdown 标记后的字数）
- [x] 自动生成 `summary`（截取前 200 字）

#### 1.2 文档更新接口增强 (PUT /api/v1/huanxing/docs/{id}) ✅
- [x] 支持 `content` 完整替换模式
- [x] 支持 `append` 追加模式（与 content 互斥）
- [x] 支持 `save_version` 参数手动触发版本保存
- [x] 自动触发版本保存：status 从 draft → published
- [x] 更新 `word_count` 和 `summary`
- [x] 更新 `current_version` 字段

#### 1.3 分享链接相关接口
- [ ] `POST /api/v1/huanxing/docs/{id}/share` - 生成/更新分享链接
  - 参数：permission, expires_hours, password（可选）
  - 返回：share_url, share_token
- [ ] `GET /api/v1/huanxing/share/{token}` - 访问分享文档（公开接口，无需登录）
  - 验证 token 有效性
  - 验证过期时间
  - 如有密码，需先验证密码
  - 返回文档内容（只读或可编辑，根据 permission）
- [ ] `DELETE /api/v1/huanxing/docs/{id}/share` - 取消分享

#### 1.4 版本历史接口 ✅
- [x] `GET /api/v1/huanxing/docs/{id}/versions` - 获取版本列表
- [x] `GET /api/v1/huanxing/docs/{id}/versions/{version}` - 获取指定版本内容
- [x] `POST /api/v1/huanxing/docs/{id}/versions/{version}/restore` - 恢复到指定版本
  - 先保存当前内容为新版本
  - 再用历史版本内容覆盖当前文档
  - 版本号递增

#### 1.5 自动保存接口 ✅
- [x] `POST /api/v1/huanxing/docs/{id}/autosave` - 自动保存草稿
  - 使用 UPSERT 模式（ON CONFLICT DO UPDATE）
  - 每个用户每个文档只保留一条记录
- [x] `GET /api/v1/huanxing/docs/{id}/autosave` - 获取自动保存的草稿

#### 1.6 导出接口
- [ ] `GET /api/v1/huanxing/docs/{id}/export?format=markdown` - 导出 Markdown
- [ ] `GET /api/v1/huanxing/docs/{id}/export?format=pdf` - 导出 PDF
  - 使用 weasyprint 生成
  - Markdown → HTML → PDF
- [ ] `GET /api/v1/huanxing/docs/{id}/export?format=docx` - 导出 Word
  - 使用 pandoc 转换

### 2. 前端页面开发

#### 2.1 文档列表页 (apps/web-antd/src/views/huanxing/huanxing_document/index.vue)
- [ ] 优化列表展示（标题、摘要、标签、状态、创建时间）
- [ ] 添加筛选：状态（draft/published/archived）、标签、创建来源（user/agent）
- [ ] 添加搜索：标题、内容全文搜索
- [ ] 添加操作按钮：编辑、分享、导出、删除
- [ ] 添加批量操作：批量删除、批量归档

#### 2.2 文档编辑器页 (新建)
- [ ] 集成 Vditor Markdown 编辑器
- [ ] 实时自动保存（每 30 秒）
- [ ] 标题编辑
- [ ] 标签管理（可添加/删除）
- [ ] 状态切换（草稿/发布/归档）
- [ ] 保存按钮（手动保存并创建版本）
- [ ] 分享按钮（打开分享设置弹窗）
- [ ] 导出按钮（Markdown/PDF/Word）
- [ ] 版本历史按钮（侧边栏展示版本列表）

#### 2.3 分享设置弹窗
- [ ] 权限选择：只读/可编辑
- [ ] 过期时间选择：24h/72h/7天/30天/永久
- [ ] 密码保护（可选）
- [ ] 生成分享链接并复制
- [ ] 取消分享按钮

#### 2.4 版本历史侧边栏
- [ ] 版本列表（版本号、创建时间、创建者）
- [ ] 点击版本预览内容（diff 对比）
- [ ] 恢复到指定版本按钮

#### 2.5 分享页面（公开访问）
- [ ] 路由：`/share/:token`
- [ ] 密码验证（如有）
- [ ] 文档预览（Markdown 渲染）
- [ ] 只读模式：禁用编辑
- [ ] 可编辑模式：允许编辑并保存

#### 2.6 Dashboard 集成
- [ ] 在侧边栏添加"我的文档"菜单项
- [ ] 路由配置：`/huanxing/documents`

### 3. OpenClaw 插件工具开发

#### 3.1 工具函数实现（~/.openclaw/extensions/huanxing-cloud/tools/）
- [ ] `huanxing_doc_create(title, content, tags?, auto_share?)` - 创建文档
- [ ] `huanxing_doc_list(status?, tags?, limit?)` - 列出文档
- [ ] `huanxing_doc_get(doc_id)` - 获取文档详情
- [ ] `huanxing_doc_update(doc_id, content?, append?, title?, tags?, save_version?)` - 更新文档
- [ ] `huanxing_doc_share(doc_id, permission?, expires_hours?, password?)` - 生成分享链接
- [ ] `huanxing_doc_export(doc_id, format)` - 导出文档

#### 3.2 工具配置
- [ ] 在 `TOOL.md` 中定义工具描述和参数
- [ ] 配置 API 基础 URL：`https://huanxing.ai.dcfuture.cn/api/v1/huanxing`
- [ ] 配置 JWT Token 认证

### 4. 部署和依赖

#### 4.1 后端依赖安装
- [ ] `pip install weasyprint` - PDF 生成
- [ ] `pip install python-markdown` - Markdown 解析
- [ ] 安装 pandoc（系统级）：`brew install pandoc`（macOS）或 `apt install pandoc`（Ubuntu）

#### 4.2 Nginx 配置
- [ ] 配置分享页面路由：`/share/*` → 前端
- [ ] 配置 API 路由：`/api/*` → 后端

#### 4.3 前端构建和部署
- [ ] 构建前端：`pnpm build`
- [ ] 部署到 `/var/www/huanxing`

## 开发优先级

### P0（核心功能，必须完成）
1. 文档创建/更新/列表 API 增强
2. 文档编辑器页面（含 Vditor 集成）
3. 自动保存功能
4. Dashboard 菜单集成

### P1（重要功能）
1. 分享链接生成和访问
2. 版本历史功能
3. 导出功能（Markdown/PDF/Word）

### P2（增强功能）
1. OpenClaw 插件工具
2. 前端列表页优化（搜索、筛选）
3. 分享页面（公开访问）

## 技术要点

### 版本保存触发逻辑
```python
# 在 service 层实现
async def update_document(db, pk, obj):
    old_doc = await get(db, pk)
    
    # 判断是否需要保存版本
    should_save_version = (
        obj.save_version  # 手动触发
        or (old_doc.status == 'draft' and obj.status == 'published')  # 自动触发
    )
    
    if should_save_version:
        await create_version(db, document_id=pk, 
                            version_number=old_doc.current_version + 1,
                            title=old_doc.title,
                            content=old_doc.content,
                            created_by=current_user.id)
        obj.current_version = old_doc.current_version + 1
    
    # 更新文档
    await crud.update(db, pk, obj)
```

### 自动保存 UPSERT
```python
# 在 service 层实现
async def autosave(db, document_id, user_id, content):
    stmt = text("""
        INSERT INTO huanxing_document_autosave (document_id, user_id, content, saved_at)
        VALUES (:doc_id, :user_id, :content, NOW())
        ON CONFLICT (document_id, user_id)
        DO UPDATE SET content = EXCLUDED.content, saved_at = NOW()
    """)
    await db.execute(stmt, {"doc_id": document_id, "user_id": user_id, "content": content})
```

### 分享链接生成
```python
import secrets
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_share_token():
    return secrets.token_urlsafe(24)  # 32字符

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
```

## 参考文档
- 设计文档：`/Users/mac/openclaw-workspace/huanxing/huanxing-project/docs/唤星文档系统架构设计.md`
- 建表 SQL：`/Users/mac/openclaw-workspace/huanxing/huanxing-project/ai-clound-backend/backend/sql/huanxing_document_tables.sql`
- 生成的代码：`/Users/mac/openclaw-workspace/huanxing/huanxing-project/ai-clound-backend/backend/app/huanxing/`
