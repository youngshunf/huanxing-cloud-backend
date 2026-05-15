"""
Manifest 解析与校验服务

负责解析和校验 App Manifest（hasn.app.yaml）
"""

from typing import Any

from backend.common.exception import errors


class ManifestService:
    """Manifest 解析与校验服务"""

    @staticmethod
    def validate(manifest: dict[str, Any]) -> list[str]:
        """
        校验 Manifest

        :param manifest: Manifest 数据
        :return: 错误列表（空列表表示校验通过）
        """
        errors_list = []

        # 1. 检查必需字段
        required_fields = ['app', 'version', 'permissions']
        for field in required_fields:
            if field not in manifest:
                errors_list.append(f'缺少必需字段: {field}')

        if 'app' in manifest:
            app_fields = ['id', 'name', 'version']
            for field in app_fields:
                if field not in manifest['app']:
                    errors_list.append(f'app 中缺少必需字段: {field}')

        # 2. 检查权限声明
        if 'permissions' in manifest:
            perms = manifest['permissions']
            if 'requested_scopes' not in perms:
                errors_list.append('permissions 中缺少 requested_scopes')
            elif not isinstance(perms['requested_scopes'], list):
                errors_list.append('requested_scopes 必须是数组')

        # 3. 检查版本号格式
        if 'version' in manifest:
            version = manifest['version']
            if not ManifestService._is_valid_semver(version):
                errors_list.append(f'版本号格式不正确: {version}（应为语义化版本号，如 1.0.0）')

        # 4. 检查 app_id 格式
        if 'app' in manifest and 'id' in manifest['app']:
            app_id = manifest['app']['id']
            if not app_id.startswith('app_'):
                errors_list.append(f'app_id 格式不正确: {app_id}（应以 app_ 开头）')

        return errors_list

    @staticmethod
    def _is_valid_semver(version: str) -> bool:
        """
        检查是否是有效的语义化版本号

        :param version: 版本号
        :return: 是否有效
        """
        import re

        pattern = r'^\d+\.\d+\.\d+(-[a-z0-9.]+)?$'
        return bool(re.match(pattern, version))

    @staticmethod
    def parse(manifest_yaml: str) -> dict[str, Any]:
        """
        解析 Manifest YAML

        :param manifest_yaml: YAML 字符串
        :return: 解析后的字典
        """
        import yaml

        try:
            manifest = yaml.safe_load(manifest_yaml)
            return manifest
        except yaml.YAMLError as e:
            raise errors.BadRequestError(msg=f'Manifest YAML 解析失败: {str(e)}')


manifest_service: ManifestService = ManifestService()
