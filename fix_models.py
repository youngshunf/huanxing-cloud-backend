import re
from pathlib import Path

# 映射：模型文件名 -> 主键字段名
pk_mapping = {
    'app_permission_grants.py': 'grant_id',
    'app_dynamic_permission_requests.py': 'request_id',
    'app_developers.py': 'developer_id',
    'app_versions.py': 'version_id',
    'app_listings.py': 'listing_id',
    'app_installations.py': 'installation_id',
    'app_tools.py': 'tool_id',
    'app_resources.py': 'resource_id',
    'app_events.py': 'event_id',
    'app_reviews.py': 'review_id',
    'app_entitlements.py': 'entitlement_id',
    'app_agent_bindings.py': 'binding_id',
    'app_data_records.py': 'record_id',
    'app_permission_audit_logs.py': 'log_id',
}

model_dir = Path('backend/app/app_platform/model')

for filename, pk_field in pk_mapping.items():
    filepath = model_dir / filename
    if not filepath.exists():
        print(f"跳过: {filename} (文件不存在)")
        continue
    
    content = filepath.read_text()
    
    # 删除 id: Mapped[id_key] 行
    content = re.sub(r'\s+id: Mapped\[id_key\] = mapped_column\(init=False\)\n', '', content)
    
    # 修改主键字段定义，添加 primary_key=True
    # 匹配类似: grant_id: Mapped[str | UUID] = mapped_column(sa.UUID(), default=None, comment='...')
    pattern = rf'({pk_field}: Mapped\[str \| UUID\] = mapped_column\(sa\.UUID\(\))'
    replacement = rf'\1, primary_key=True'
    content = re.sub(pattern, replacement, content)
    
    filepath.write_text(content)
    print(f"✓ 修复: {filename} (主键: {pk_field})")

print("\n所有模型已修复")
