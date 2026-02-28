from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.huanxing.crud.crud_huanxing_document_version import huanxing_document_version_dao
from backend.app.huanxing.model import HuanxingDocumentVersion
from backend.app.huanxing.schema.huanxing_document_version import CreateHuanxingDocumentVersionParam, DeleteHuanxingDocumentVersionParam, UpdateHuanxingDocumentVersionParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HuanxingDocumentVersionService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HuanxingDocumentVersion:
        """
        获取文档版本历史

        :param db: 数据库会话
        :param pk: 文档版本历史 ID
        :return:
        """
        huanxing_document_version = await huanxing_document_version_dao.get(db, pk)
        if not huanxing_document_version:
            raise errors.NotFoundError(msg='文档版本历史不存在')
        return huanxing_document_version

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取文档版本历史列表

        :param db: 数据库会话
        :return:
        """
        huanxing_document_version_select = await huanxing_document_version_dao.get_select()
        return await paging_data(db, huanxing_document_version_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HuanxingDocumentVersion]:
        """
        获取所有文档版本历史

        :param db: 数据库会话
        :return:
        """
        huanxing_document_versions = await huanxing_document_version_dao.get_all(db)
        return huanxing_document_versions

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHuanxingDocumentVersionParam) -> None:
        """
        创建文档版本历史

        :param db: 数据库会话
        :param obj: 创建文档版本历史参数
        :return:
        """
        await huanxing_document_version_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHuanxingDocumentVersionParam) -> int:
        """
        更新文档版本历史

        :param db: 数据库会话
        :param pk: 文档版本历史 ID
        :param obj: 更新文档版本历史参数
        :return:
        """
        count = await huanxing_document_version_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHuanxingDocumentVersionParam) -> int:
        """
        删除文档版本历史

        :param db: 数据库会话
        :param obj: 文档版本历史 ID 列表
        :return:
        """
        count = await huanxing_document_version_dao.delete(db, obj.pks)
        return count


huanxing_document_version_service: HuanxingDocumentVersionService = HuanxingDocumentVersionService()
