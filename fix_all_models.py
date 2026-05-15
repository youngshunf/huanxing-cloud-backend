from pathlib import Path

# 完整的主键映射：模型文件名 -> (主键字段名, 字段类型)
pk_mapping = {
    # UUID 主键
    'app_permission_grants.py': ('grant_id', 'UUID'),
    'app_dynamic_permission_requests.py': ('request_id', 'UUID'),
    'app_developers.py': ('developer_id', 'UUID'),
    'app_versions.py': ('version_id', 'UUID'),
    'app_listings.py': ('listing_id', 'UUID'),
    'app_reviews.py': ('review_id', 'UUID'),
    'app_entitlements.py': ('entitlement_id', 'UUID'),
    'app_agent_bindings.py': ('binding_id', 'UUID'),
    'app_scopes.py': ('id', 'UUID'),  # 特殊：使用 id
    
    # VARCHAR 主键
    'app_installations.py': ('installation_id', 'VARCHAR'),
    'app_manifests.py': ('app_id', 'VARCHAR'),
    'app_tools.py': ('tool_id', 'VARCHAR'),
    'app_resources.py': ('resource_id', 'VARCHAR'),
    'app_events.py': ('event_id', 'VARCHAR'),
    'platform_scopes.py': ('scope', 'VARCHAR'),
    
    # id 主键（使用 Base 的 id_key）
    'app_data_records.py': ('id', 'id_key'),
    'app_permission_audit_logs.py': ('id', 'id_key'),
}

model_dir = Path('backend/app/app_platform/model')

for filename, (pk_field, pk_type) in pk_mapping.items():
    filepath = model_dir / filename
    if not filepath.exists():
        print(f"跳过: {filename} (文件不存在)")
        continue
    
    content = filepath.read_text()
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # 跳过旧的 id: Mapped[id_key] 行（如果不是真正的主键）
        if 'id: Mapped[id_key]' in line and pk_field != 'id':
            continue
        
        # 为主键字段添加 primary_key=True
        if f'{pk_field}: Mapped[' in line and 'primary_key=True' not in line:
            if pk_type == 'UUID':
                # UUID 类型
                line = line.replace(
                    f'{pk_field}: Mapped[str | UUID] = mapped_column(sa.UUID(),',
                    f'{pk_field}: Mapped[str | UUID] = mapped_column(sa.UUID(), primary_key=True,'
                )
            elif pk_type == 'VARCHAR':
                # VARCHAR 类型
                line = line.replace(
                    f'{pk_field}: Mapped[str] = mapped_column(sa.String(',
                    f'{pk_field}: Mapped[str] = mapped_column(sa.String(', 
                )
                if 'primary_key=True' not in line:
                    line = line.replace('), default=', '), primary_key=True, default=')
            elif pk_type == 'id_key':
                # 保持 id_key 不变
                pass
        
        new_lines.append(line)
    
    filepath.write_text('\n'.join(new_lines))
    print(f"✓ 修复: {filename} (主键: {pk_field}, 类型: {pk_type})")

print("\n所有模型已修复")
