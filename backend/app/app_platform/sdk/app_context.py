#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Context

应用运行时上下文，包含身份信息和隔离键
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppContext:
    """
    应用运行时上下文

    包含应用运行所需的所有身份信息和隔离键
    """

    # 核心身份
    owner_id: str
    app_id: str
    installation_id: str

    # 可选身份
    agent_id: Optional[str] = None
    developer_id: Optional[str] = None
    listing_id: Optional[str] = None
    entitlement_id: Optional[str] = None

    # 唤星扩展：安装目标
    install_target_type: Optional[str] = None  # 'agent', 'constellation', etc.
    install_target_id: Optional[str] = None

    # 请求上下文
    request_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

    def get_isolation_key(self) -> str:
        """
        获取数据隔离键

        格式：owner_id:app_id:installation_id[:install_target_type:install_target_id]
        """
        base_key = f"{self.owner_id}:{self.app_id}:{self.installation_id}"

        if self.install_target_type and self.install_target_id:
            return f"{base_key}:{self.install_target_type}:{self.install_target_id}"

        return base_key

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'owner_id': self.owner_id,
            'app_id': self.app_id,
            'installation_id': self.installation_id,
            'agent_id': self.agent_id,
            'developer_id': self.developer_id,
            'listing_id': self.listing_id,
            'entitlement_id': self.entitlement_id,
            'install_target_type': self.install_target_type,
            'install_target_id': self.install_target_id,
            'request_id': self.request_id,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AppContext':
        """从字典创建"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
