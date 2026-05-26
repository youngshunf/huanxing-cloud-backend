# ClawHub 同步功能 - LLM 翻译问题说明

## 问题描述

翻译服务无法正常工作，原因如下：

### 1. LLM 网关返回流式响应

即使设置 `stream: false`，LLM 网关仍返回 `text/event-stream` 格式的流式响应：

```bash
curl -X POST http://127.0.0.1:3180/v1/chat/completions \
  -H "Authorization: Bearer sk-xxx" \
  -d '{"model": "gpt-5.5", "messages": [...], "stream": false}'

# 返回：
Content-Type: text/event-stream
data: {"choices":[],"usage":{...}}
data: [DONE]
```

### 2. Choices 为空

所有模型（gpt-5.4-mini, gpt-5.5 等）返回的 `choices` 数组都是空的，没有实际的翻译内容。

### 3. 项目 LLM Gateway 需要用户认证

项目的 `backend.app.llm.core.gateway.LLMGateway` 需要以下参数：
- `user_id`: 用户 ID
- `api_key_id`: API Key ID  
- `rpm_limit`, `daily_limit`, `monthly_limit`: 限流参数

但翻译服务是系统级功能，不应该需要用户认证。

## 当前解决方案

**暂时禁用 LLM 翻译，使用原文**：

```python
# translation_service.py
async def translate_skill_metadata(...):
    # 直接使用原文，不调用 LLM
    result['name_en'] = name
    result['name_zh'] = name
    result['description_en'] = description
    result['description_zh'] = description
    return result
```

**影响**：
- ✅ 不影响核心同步功能
- ✅ 英文技能保持英文
- ✅ 中文技能保持中文
- ⚠️ 无法自动翻译为双语

## 建议的修复方案

### 方案 1：修复 LLM 网关配置（推荐）

检查 new-api 或 LLM 网关的配置：
1. 确认 `stream` 参数是否被正确处理
2. 检查模型后端是否正确配置
3. 验证模型是否能正常返回内容

### 方案 2：创建系统级 LLM 调用接口

在 `LLMGateway` 中添加系统级调用方法：

```python
async def system_completion(
    self,
    db: AsyncSession,
    model: str,
    messages: list,
    **kwargs
) -> ChatCompletionResponse:
    """系统级 LLM 调用，不需要用户认证"""
    # 使用系统配置的 API Key
    # 不计费，不限流
    ...
```

### 方案 3：使用第三方翻译服务

集成其他翻译服务：
- Google Translate API
- DeepL API
- 百度翻译 API

## 测试步骤

### 1. 验证 LLM 网关

```bash
# 测试非流式调用
curl -X POST http://127.0.0.1:3180/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{
    "model": "gpt-5.5",
    "messages": [{"role": "user", "content": "Say hello"}],
    "stream": false
  }'

# 预期：返回 JSON 格式，choices 不为空
```

### 2. 测试翻译服务

```python
from backend.app.marketplace.service.translation_service import translation_service

result = await translation_service.translate('Hello', 'en', 'zh')
print(result)  # 应该返回中文翻译
```

## 当前状态

- ✅ ClawHub 同步功能：完全可用
- ✅ 命名空间格式：正确
- ✅ 分类映射：正常（关键词匹配）
- ⚠️ LLM 翻译：暂时禁用
- ✅ 语言检测：正常工作

## 结论

**ClawHub 同步功能已完成并可用**，翻译功能的缺失不影响核心业务。建议：

1. **短期**：使用当前方案（原文），系统可以正常运行
2. **中期**：修复 LLM 网关配置或添加系统级调用接口
3. **长期**：考虑集成专业翻译服务

---

**最后更新**: 2026-05-27  
**状态**: 已记录，待修复
