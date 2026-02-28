from typing import Any, Sequence
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.huanxing.crud.crud_huanxing_document_folder import huanxing_document_folder_dao
from backend.app.huanxing.model.huanxing_document_folder import HuanxingDocumentFolder
from backend.app.huanxing.schema.huanxing_document_folder import CreateFolderParam, UpdateFolderParam
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.utils.timezone import timezone as tz

MAX_DEPTH = 5  # 目录最大层级


class HuanxingDocumentFolderService:

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HuanxingDocumentFolder:
        folder = await huanxing_document_folder_dao.get(db, pk)
        if not folder:
            raise errors.NotFoundError(msg='目录不存在')
        return folder

    @staticmethod
    async def get_list(db: AsyncSession, user_id: int | None = None) -> dict[str, Any]:
        """获取目录列表（管理端，分页）"""
        folder_select = await huanxing_document_folder_dao.get_select()
        if user_id is not None:
            folder_select = folder_select.where(
                HuanxingDocumentFolder.user_id == user_id
            )
        return await paging_data(db, folder_select)

    @staticmethod
    async def get_tree(*, db: AsyncSession, user_id: int) -> list[dict]:
        """
        获取用户完整目录树（含每个目录下的文档计数）
        一次查出所有目录 → 内存构建树
        """
        # 查所有目录
        folders = await huanxing_document_folder_dao.get_by_user(db, user_id)

        # 查每个目录的文档数
        doc_count_stmt = text("""
            SELECT folder_id, COUNT(*) as cnt
            FROM huanxing_document
            WHERE user_id = :user_id AND deleted_at IS NULL AND folder_id IS NOT NULL
            GROUP BY folder_id
        """)
        result = await db.execute(doc_count_stmt, {"user_id": user_id})
        doc_counts = {row[0]: row[1] for row in result.fetchall()}

        # 根目录文档数
        root_doc_stmt = text("""
            SELECT COUNT(*) FROM huanxing_document
            WHERE user_id = :user_id AND deleted_at IS NULL AND folder_id IS NULL
        """)
        root_result = await db.execute(root_doc_stmt, {"user_id": user_id})
        root_doc_count = root_result.scalar() or 0

        # 构建树
        folder_map: dict[int, dict] = {}
        for f in folders:
            folder_map[f.id] = {
                'id': f.id,
                'uuid': f.uuid,
                'name': f.name,
                'icon': f.icon,
                'parent_id': f.parent_id,
                'sort_order': f.sort_order,
                'doc_count': doc_counts.get(f.id, 0),
                'children': [],
            }

        # 组装父子关系
        tree: list[dict] = []
        for fid, node in folder_map.items():
            pid = node['parent_id']
            if pid and pid in folder_map:
                folder_map[pid]['children'].append(node)
            else:
                tree.append(node)

        # 排序
        def sort_tree(nodes: list[dict]):
            nodes.sort(key=lambda n: (n['sort_order'], n['name']))
            for n in nodes:
                sort_tree(n['children'])

        sort_tree(tree)

        return tree

    @staticmethod
    async def get_folder_contents(*, db: AsyncSession, folder_id: int | None, user_id: int) -> dict:
        """获取目录内容：子目录列表 + 文档列表"""
        # 子目录
        if folder_id is not None:
            # 校验目录存在且归属正确
            folder = await huanxing_document_folder_dao.get(db, folder_id)
            if not folder or folder.user_id != user_id:
                raise errors.NotFoundError(msg='目录不存在')

        sub_folders_raw = await huanxing_document_folder_dao.get_children(db, folder_id, user_id)
        sub_folders = [
            {
                'id': f.id,
                'uuid': f.uuid,
                'name': f.name,
                'icon': f.icon,
                'sort_order': f.sort_order,
            }
            for f in sub_folders_raw
        ]
        sub_folders.sort(key=lambda x: (x['sort_order'], x['name']))

        # 文档列表
        if folder_id is not None:
            doc_stmt = text("""
                SELECT id, uuid, title, summary, tags, word_count, status, created_by, agent_id,
                       share_token, current_version, created_at, updated_at, folder_id
                FROM huanxing_document
                WHERE user_id = :user_id AND folder_id = :folder_id AND deleted_at IS NULL
                ORDER BY updated_at DESC
            """)
            result = await db.execute(doc_stmt, {"user_id": user_id, "folder_id": folder_id})
        else:
            doc_stmt = text("""
                SELECT id, uuid, title, summary, tags, word_count, status, created_by, agent_id,
                       share_token, current_version, created_at, updated_at, folder_id
                FROM huanxing_document
                WHERE user_id = :user_id AND folder_id IS NULL AND deleted_at IS NULL
                ORDER BY updated_at DESC
            """)
            result = await db.execute(doc_stmt, {"user_id": user_id})

        docs = [
            {
                'id': row[0], 'uuid': row[1], 'title': row[2], 'summary': row[3],
                'tags': row[4], 'word_count': row[5], 'status': row[6], 'created_by': row[7],
                'agent_id': row[8], 'share_token': row[9], 'current_version': row[10],
                'created_at': row[11], 'updated_at': row[12], 'folder_id': row[13],
            }
            for row in result.fetchall()
        ]

        return {
            'folder_id': folder_id,
            'sub_folders': sub_folders,
            'documents': docs,
        }

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateFolderParam, user_id: int) -> dict:
        """创建目录，自动计算 path"""
        parent_path = '/'
        if obj.parent_id:
            parent = await huanxing_document_folder_dao.get(db, obj.parent_id)
            if not parent or parent.user_id != user_id:
                raise errors.NotFoundError(msg='父目录不存在')
            parent_path = parent.path
            # 检查层级限制
            depth = parent_path.strip('/').count('/') + 1 if parent_path.strip('/') else 0
            if depth >= MAX_DEPTH:
                raise errors.BadRequestError(msg=f'目录层级不能超过{MAX_DEPTH}层')

        folder_data = {
            'uuid': str(uuid.uuid4()),
            'user_id': user_id,
            'name': obj.name,
            'parent_id': obj.parent_id,
            'path': '/',  # 临时，创建后更新
            'sort_order': 0,
            'icon': obj.icon,
            'description': obj.description,
        }
        folder = await huanxing_document_folder_dao.create(db, folder_data)

        # 更新 path（需要 id）
        new_path = f"{parent_path.rstrip('/')}/{folder.id}/"
        await huanxing_document_folder_dao.update(db, folder.id, {'path': new_path})

        return {
            'id': folder.id,
            'uuid': folder.uuid,
            'name': folder.name,
            'path': new_path,
        }

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateFolderParam, user_id: int) -> int:
        """更新目录（重命名、图标等）"""
        folder = await huanxing_document_folder_dao.get(db, pk)
        if not folder or folder.user_id != user_id:
            raise errors.NotFoundError(msg='目录不存在')

        update_data = obj.model_dump(exclude_unset=True)
        if not update_data:
            return 0
        return await huanxing_document_folder_dao.update(db, pk, update_data)

    @staticmethod
    async def move_folder(*, db: AsyncSession, folder_id: int, target_parent_id: int | None, user_id: int) -> int:
        """移动目录到新的父目录，更新所有后代的 path"""
        folder = await huanxing_document_folder_dao.get(db, folder_id)
        if not folder or folder.user_id != user_id:
            raise errors.NotFoundError(msg='目录不存在')

        # 不能移动到自己
        if target_parent_id == folder_id:
            raise errors.BadRequestError(msg='不能移动到自身')

        # 计算新 path
        new_parent_path = '/'
        if target_parent_id:
            target_parent = await huanxing_document_folder_dao.get(db, target_parent_id)
            if not target_parent or target_parent.user_id != user_id:
                raise errors.NotFoundError(msg='目标目录不存在')

            # 防止环路：目标不能是自己的后代
            if target_parent.path.startswith(folder.path):
                raise errors.BadRequestError(msg='不能移动到自身的子目录下')

            new_parent_path = target_parent.path

            # 检查层级
            # 当前目录自身在 path 中的深度
            folder_depth = folder.path.strip('/').count('/') + 1 if folder.path.strip('/') else 0
            # 当前目录子树的最大深度
            max_subtree_stmt = text("""
                SELECT MAX(LENGTH(path) - LENGTH(REPLACE(path, '/', '')))
                FROM huanxing_document_folder
                WHERE path LIKE :prefix AND user_id = :user_id AND deleted_at IS NULL
            """)
            result = await db.execute(max_subtree_stmt, {
                "prefix": f"{folder.path}%",
                "user_id": user_id
            })
            max_subtree_depth = (result.scalar() or 0)
            target_depth = new_parent_path.strip('/').count('/') + 1 if new_parent_path.strip('/') else 0
            subtree_height = max_subtree_depth - folder_depth
            if target_depth + 1 + subtree_height > MAX_DEPTH:
                raise errors.BadRequestError(msg=f'移动后目录层级会超过{MAX_DEPTH}层')

        old_path = folder.path
        new_path = f"{new_parent_path.rstrip('/')}/{folder_id}/"

        # 更新所有后代的 path
        update_stmt = text("""
            UPDATE huanxing_document_folder
            SET path = :new_prefix || SUBSTRING(path FROM :old_len + 1),
                parent_id = CASE WHEN id = :folder_id THEN :target_parent_id ELSE parent_id END,
                updated_at = NOW()
            WHERE path LIKE :old_prefix_like AND user_id = :user_id AND deleted_at IS NULL
        """)
        result = await db.execute(update_stmt, {
            "new_prefix": new_path,
            "old_len": len(old_path),
            "folder_id": folder_id,
            "target_parent_id": target_parent_id,
            "old_prefix_like": f"{old_path}%",
            "user_id": user_id,
        })

        # 更新自身的 parent_id 和 path
        await huanxing_document_folder_dao.update(db, folder_id, {
            'parent_id': target_parent_id,
            'path': new_path,
        })

        return result.rowcount

    @staticmethod
    async def delete(*, db: AsyncSession, folder_id: int, user_id: int, recursive: bool = False) -> int:
        """删除目录
        recursive=False：只删除空目录
        recursive=True：递归删除目录及其所有后代目录和文档
        """
        folder = await huanxing_document_folder_dao.get(db, folder_id)
        if not folder or folder.user_id != user_id:
            raise errors.NotFoundError(msg='目录不存在')

        if not recursive:
            # 检查是否有子目录
            children = await huanxing_document_folder_dao.get_children(db, folder_id, user_id)
            if children:
                raise errors.BadRequestError(msg='目录下有子目录，请先删除或使用递归删除')

            # 检查是否有文档
            doc_count_stmt = text("""
                SELECT COUNT(*) FROM huanxing_document
                WHERE folder_id = :folder_id AND user_id = :user_id AND deleted_at IS NULL
            """)
            result = await db.execute(doc_count_stmt, {"folder_id": folder_id, "user_id": user_id})
            if (result.scalar() or 0) > 0:
                raise errors.BadRequestError(msg='目录下有文档，请先移走或使用递归删除')

            return await huanxing_document_folder_dao.delete(db, [folder_id])
        else:
            # 递归删除：所有后代目录 + 后代文档
            # 1. 将后代目录下的文档标记删除
            delete_docs_stmt = text("""
                UPDATE huanxing_document SET deleted_at = NOW()
                WHERE folder_id IN (
                    SELECT id FROM huanxing_document_folder
                    WHERE path LIKE :prefix AND user_id = :user_id
                ) AND deleted_at IS NULL
            """)
            await db.execute(delete_docs_stmt, {
                "prefix": f"{folder.path}%",
                "user_id": user_id,
            })

            # 2. 当前目录下的直接文档也标记删除
            delete_direct_docs_stmt = text("""
                UPDATE huanxing_document SET deleted_at = NOW()
                WHERE folder_id = :folder_id AND user_id = :user_id AND deleted_at IS NULL
            """)
            await db.execute(delete_direct_docs_stmt, {
                "folder_id": folder_id,
                "user_id": user_id,
            })

            # 3. 删除所有后代目录
            delete_folders_stmt = text("""
                DELETE FROM huanxing_document_folder
                WHERE path LIKE :prefix AND user_id = :user_id
            """)
            result = await db.execute(delete_folders_stmt, {
                "prefix": f"{folder.path}%",
                "user_id": user_id,
            })

            # 4. 删除自身
            await huanxing_document_folder_dao.delete(db, [folder_id])

            return result.rowcount + 1

    @staticmethod
    async def move_document(*, db: AsyncSession, document_id: int, target_folder_id: int | None, user_id: int) -> int:
        """移动文档到指定目录"""
        # 校验文档归属
        from backend.app.huanxing.crud.crud_huanxing_document import huanxing_document_dao
        doc = await huanxing_document_dao.get(db, document_id)
        if not doc or doc.user_id != user_id:
            raise errors.NotFoundError(msg='文档不存在')

        # 校验目标目录归属
        if target_folder_id is not None:
            folder = await huanxing_document_folder_dao.get(db, target_folder_id)
            if not folder or folder.user_id != user_id:
                raise errors.NotFoundError(msg='目标目录不存在')

        return await huanxing_document_dao.update(db, document_id, {'folder_id': target_folder_id})


huanxing_document_folder_service: HuanxingDocumentFolderService = HuanxingDocumentFolderService()
