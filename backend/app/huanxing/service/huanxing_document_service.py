from typing import Any, Sequence
import re
import secrets
import json
import uuid
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from backend.app.huanxing.crud.crud_huanxing_document import huanxing_document_dao
from backend.app.huanxing.model import HuanxingDocument
from backend.app.huanxing.schema.huanxing_document import CreateHuanxingDocumentParam, DeleteHuanxingDocumentParam, UpdateHuanxingDocumentParam, AutosaveParam
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.utils.timezone import timezone as tz

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_share_token() -> str:
    """生成分享token"""
    return secrets.token_urlsafe(24)


def hash_password(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def calculate_word_count(markdown_content: str) -> int:
    """计算字数（去除Markdown标记）"""
    text = re.sub(r'[#*`\[\]()_~>-]', '', markdown_content)
    text = re.sub(r'\n+', ' ', text)
    return len(text.strip())


def generate_summary(markdown_content: str, max_length: int = 200) -> str:
    """生成摘要"""
    text = re.sub(r'[#*`\[\]()_~>-]', '', markdown_content)
    text = re.sub(r'\n+', ' ', text).strip()
    return text[:max_length] + ('...' if len(text) > max_length else '')


class HuanxingDocumentService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HuanxingDocument:
        """
        获取唤星文档

        :param db: 数据库会话
        :param pk: 唤星文档 ID
        :return:
        """
        huanxing_document = await huanxing_document_dao.get(db, pk)
        if not huanxing_document:
            raise errors.NotFoundError(msg='唤星文档不存在')
        return huanxing_document

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取唤星文档列表

        :param db: 数据库会话
        :return:
        """
        huanxing_document_select = await huanxing_document_dao.get_select()
        return await paging_data(db, huanxing_document_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HuanxingDocument]:
        """
        获取所有唤星文档

        :param db: 数据库会话
        :return:
        """
        huanxing_documents = await huanxing_document_dao.get_all(db)
        return huanxing_documents

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHuanxingDocumentParam, user_id: int) -> dict:
        """
        创建唤星文档

        :param db: 数据库会话
        :param obj: 创建唤星文档参数
        :param user_id: 用户ID
        :return: 包含文档ID和分享链接的字典
        """
        # 计算字数和摘要
        word_count = calculate_word_count(obj.content)
        summary = generate_summary(obj.content)
        
        # 处理标签
        tags_str = json.dumps(obj.tags) if obj.tags else None
        
        # 准备文档数据
        doc_data = {
            'uuid': str(uuid.uuid4()),
            'user_id': user_id,
            'title': obj.title,
            'content': obj.content,
            'tags': tags_str,
            'word_count': word_count,
            'summary': summary,
            'status': obj.status,
            'created_by': 'user',
            'current_version': 1
        }
        
        # 处理自动分享
        share_url = None
        if obj.auto_share:
            doc_data['share_token'] = generate_share_token()
            doc_data['share_permission'] = obj.auto_share.permission
            doc_data['share_expires_at'] = tz.now() + timedelta(hours=obj.auto_share.expires_hours)
            if obj.auto_share.password:
                doc_data['share_password'] = hash_password(obj.auto_share.password)
            share_url = f"https://huanxing.ai.dcfuture.cn/share/{doc_data['share_token']}"
        
        # 创建文档
        doc = await huanxing_document_dao.create(db, doc_data)
        
        return {
            'id': doc.id,
            'uuid': doc.uuid,
            'share_url': share_url
        }

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHuanxingDocumentParam, user_id: int) -> int:
        """
        更新唤星文档

        :param db: 数据库会话
        :param pk: 唤星文档 ID
        :param obj: 更新唤星文档参数
        :param user_id: 用户ID
        :return:
        """
        # 获取旧文档
        old_doc = await huanxing_document_dao.get(db, pk)
        if not old_doc:
            raise errors.NotFoundError(msg='唤星文档不存在')
        
        # 处理 append 模式
        if obj.append:
            obj.content = old_doc.content + obj.append
            obj.append = None
        
        # 判断是否需要保存版本
        should_save_version = (
            obj.save_version or 
            (old_doc.status == 'draft' and obj.status == 'published')
        )
        
        if should_save_version:
            # 保存当前版本到历史表
            from backend.app.huanxing.crud.crud_huanxing_document_version import huanxing_document_version_dao
            await huanxing_document_version_dao.create(db, {
                'document_id': pk,
                'version_number': old_doc.current_version,
                'title': old_doc.title,
                'content': old_doc.content,
                'created_by': user_id
            })
            obj.current_version = old_doc.current_version + 1
        
        # 更新 word_count 和 summary
        update_data = obj.dict(exclude_unset=True)
        if obj.content:
            update_data['word_count'] = calculate_word_count(obj.content)
            update_data['summary'] = generate_summary(obj.content)
        
        # 处理标签
        if obj.tags is not None:
            update_data['tags'] = json.dumps(obj.tags)
        
        count = await huanxing_document_dao.update(db, pk, update_data)
        return count
    
    @staticmethod
    async def autosave(*, db: AsyncSession, document_id: int, user_id: int, content: str) -> None:
        """
        自动保存文档草稿（UPSERT）

        :param db: 数据库会话
        :param document_id: 文档ID
        :param user_id: 用户ID
        :param content: 文档内容
        :return:
        """
        stmt = text("""
            INSERT INTO huanxing_document_autosave (document_id, user_id, content, saved_at)
            VALUES (:doc_id, :user_id, :content, NOW())
            ON CONFLICT (document_id, user_id)
            DO UPDATE SET content = EXCLUDED.content, saved_at = NOW()
        """)
        await db.execute(stmt, {"doc_id": document_id, "user_id": user_id, "content": content})
        await db.commit()
    
    @staticmethod
    async def get_autosave(*, db: AsyncSession, document_id: int, user_id: int) -> dict | None:
        """
        获取自动保存的草稿

        :param db: 数据库会话
        :param document_id: 文档ID
        :param user_id: 用户ID
        :return:
        """
        stmt = text("""
            SELECT content, saved_at 
            FROM huanxing_document_autosave 
            WHERE document_id = :doc_id AND user_id = :user_id
        """)
        result = await db.execute(stmt, {"doc_id": document_id, "user_id": user_id})
        row = result.fetchone()
        if row:
            return {'content': row[0], 'saved_at': row[1]}
        return None
    
    @staticmethod
    async def get_versions(*, db: AsyncSession, document_id: int) -> list[dict]:
        """
        获取文档版本历史列表

        :param db: 数据库会话
        :param document_id: 文档ID
        :return: 版本列表
        """
        from backend.app.huanxing.crud.crud_huanxing_document_version import huanxing_document_version_dao
        stmt = text("""
            SELECT id, version_number, title, created_at, created_by
            FROM huanxing_document_version
            WHERE document_id = :doc_id
            ORDER BY version_number DESC
        """)
        result = await db.execute(stmt, {"doc_id": document_id})
        rows = result.fetchall()
        return [
            {
                'id': row[0],
                'version_number': row[1],
                'title': row[2],
                'created_at': row[3],
                'created_by': row[4]
            }
            for row in rows
        ]
    
    @staticmethod
    async def get_version_detail(*, db: AsyncSession, document_id: int, version_number: int) -> dict | None:
        """
        获取指定版本的详细内容

        :param db: 数据库会话
        :param document_id: 文档ID
        :param version_number: 版本号
        :return: 版本详情
        """
        stmt = text("""
            SELECT id, version_number, title, content, created_at, created_by
            FROM huanxing_document_version
            WHERE document_id = :doc_id AND version_number = :ver_num
        """)
        result = await db.execute(stmt, {"doc_id": document_id, "ver_num": version_number})
        row = result.fetchone()
        if row:
            return {
                'id': row[0],
                'version_number': row[1],
                'title': row[2],
                'content': row[3],
                'created_at': row[4],
                'created_by': row[5]
            }
        return None
    
    @staticmethod
    async def restore_version(*, db: AsyncSession, document_id: int, version_number: int, user_id: int) -> int:
        """
        恢复到指定版本

        :param db: 数据库会话
        :param document_id: 文档ID
        :param version_number: 版本号
        :param user_id: 用户ID
        :return: 更新行数
        """
        # 获取目标版本
        version = await HuanxingDocumentService.get_version_detail(db=db, document_id=document_id, version_number=version_number)
        if not version:
            raise errors.NotFoundError(msg='版本不存在')
        
        # 获取当前文档
        current_doc = await huanxing_document_dao.get(db, document_id)
        if not current_doc:
            raise errors.NotFoundError(msg='文档不存在')
        
        # 保存当前版本到历史（使用下一个可用的版本号，避免重复）
        from backend.app.huanxing.crud.crud_huanxing_document_version import huanxing_document_version_dao
        max_ver_stmt = text("""
            SELECT COALESCE(MAX(version_number), 0) FROM huanxing_document_version
            WHERE document_id = :doc_id
        """)
        max_ver_result = await db.execute(max_ver_stmt, {"doc_id": document_id})
        max_version = max_ver_result.scalar() or 0
        next_version = max(current_doc.current_version, max_version + 1)
        
        await huanxing_document_version_dao.create(db, {
            'document_id': document_id,
            'version_number': next_version,
            'title': current_doc.title,
            'content': current_doc.content,
            'created_by': user_id
        })
        
        # 恢复到目标版本
        update_data = {
            'title': version['title'],
            'content': version['content'],
            'word_count': calculate_word_count(version['content']),
            'summary': generate_summary(version['content']),
            'current_version': next_version + 1
        }
        
        count = await huanxing_document_dao.update(db, document_id, update_data)
        return count
    
    @staticmethod
    async def get_shared_document(*, db: AsyncSession, share_token: str, password: str | None = None) -> dict:
        """
        通过分享链接访问文档（公开接口）

        :param db: 数据库会话
        :param share_token: 分享token
        :param password: 分享密码（如果需要）
        :return: 文档内容
        """
        # 查询文档
        stmt = text("""
            SELECT id, uuid, title, content, summary, tags, share_permission, 
                   share_password, share_expires_at, created_at, updated_at
            FROM huanxing_document
            WHERE share_token = :token AND deleted_at IS NULL
        """)
        result = await db.execute(stmt, {"token": share_token})
        row = result.fetchone()
        
        if not row:
            raise errors.NotFoundError(msg='分享链接不存在或已失效')
        
        # 检查过期时间（统一使用 aware datetime 比较）
        expires_at = row[8]  # share_expires_at
        if expires_at:
            now = tz.now()
            # 如果 DB 返回的是 aware datetime，直接比较；否则转为 naive
            if expires_at.tzinfo is None:
                now = now.replace(tzinfo=None)
            if now > expires_at:
                raise errors.ForbiddenError(msg='分享链接已过期')
        
        # 验证密码
        if row[7]:  # share_password
            if not password:
                raise errors.ForbiddenError(msg='需要密码才能访问')
            if not pwd_context.verify(password, row[7]):
                raise errors.ForbiddenError(msg='密码错误')
        
        # 返回文档内容
        return {
            'id': row[0],
            'uuid': row[1],
            'title': row[2],
            'content': row[3],
            'summary': row[4],
            'tags': json.loads(row[5]) if row[5] else [],
            'permission': row[6],  # view 或 edit
            'created_at': row[9],
            'updated_at': row[10]
        }
    
    @staticmethod
    async def update_share_settings(*, db: AsyncSession, document_id: int, permission: str, expires_hours: int, password: str | None = None) -> str:
        """
        更新分享设置

        :param db: 数据库会话
        :param document_id: 文档ID
        :param permission: 权限（view/edit）
        :param expires_hours: 过期时间（小时）
        :param password: 密码（可选）
        :return: 分享链接
        """
        doc = await huanxing_document_dao.get(db, document_id)
        if not doc:
            raise errors.NotFoundError(msg='文档不存在')
        
        # 生成或复用 token
        share_token = doc.share_token or generate_share_token()
        
        update_data = {
            'share_token': share_token,
            'share_permission': permission,
            'share_expires_at': tz.now() + timedelta(hours=expires_hours)
        }
        
        if password:
            update_data['share_password'] = hash_password(password)
        else:
            update_data['share_password'] = None
        
        await huanxing_document_dao.update(db, document_id, update_data)
        
        return f"https://huanxing.ai.dcfuture.cn/share/{share_token}"
    
    @staticmethod
    async def cancel_share(*, db: AsyncSession, document_id: int) -> int:
        """
        取消分享

        :param db: 数据库会话
        :param document_id: 文档ID
        :return: 更新行数
        """
        update_data = {
            'share_token': None,
            'share_password': None,
            'share_permission': None,
            'share_expires_at': None
        }
        count = await huanxing_document_dao.update(db, document_id, update_data)
        return count
    
    @staticmethod
    async def export_document(*, db: AsyncSession, document_id: int, format: str) -> tuple[bytes, str, str]:
        """
        导出文档

        :param db: 数据库会话
        :param document_id: 文档ID
        :param format: 导出格式（markdown/pdf/docx）
        :return: (文件内容, 文件名, MIME类型)
        """
        doc = await huanxing_document_dao.get(db, document_id)
        if not doc:
            raise errors.NotFoundError(msg='文档不存在')
        
        filename = f"{doc.title}_{tz.now().strftime('%Y%m%d')}"
        
        if format == 'markdown':
            content = doc.content.encode('utf-8')
            return content, f"{filename}.md", "text/markdown"
        
        elif format == 'pdf':
            # Markdown → HTML → PDF
            import markdown
            from weasyprint import HTML
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{doc.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1, h2, h3 {{ color: #333; }}
                    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
                    pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                </style>
            </head>
            <body>
                {markdown.markdown(doc.content, extensions=['fenced_code', 'tables'])}
            </body>
            </html>
            """
            
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes, f"{filename}.pdf", "application/pdf"
        
        elif format == 'docx':
            # 使用 pandoc 转换
            import subprocess
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as md_file:
                md_file.write(doc.content)
                md_path = md_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx_file:
                docx_path = docx_file.name
            
            try:
                subprocess.run(
                    ['pandoc', md_path, '-o', docx_path],
                    check=True,
                    capture_output=True
                )
                
                with open(docx_path, 'rb') as f:
                    docx_bytes = f.read()
                
                return docx_bytes, f"{filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            finally:
                import os
                os.unlink(md_path)
                os.unlink(docx_path)
        
        else:
            raise errors.BadRequestError(msg='不支持的导出格式')

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHuanxingDocumentParam) -> int:
        """
        删除唤星文档

        :param db: 数据库会话
        :param obj: 唤星文档 ID 列表
        :return:
        """
        count = await huanxing_document_dao.delete(db, obj.pks)
        return count


huanxing_document_service: HuanxingDocumentService = HuanxingDocumentService()
