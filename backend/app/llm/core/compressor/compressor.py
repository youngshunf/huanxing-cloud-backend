"""上下文压缩器核心逻辑
@author Guardian

当对话历史 token 数接近模型上下文限制时，自动将历史消息压缩为
结构化摘要，保留最近消息原文。支持增量压缩和缓存复用。

Phase 2 新增：
- 二次压缩（摘要块合并）
- 降级保留消息数（6→4→2）
- 摘要生成超时保护
- 摘要生成失败重试
- Redis 故障完整降级路径
"""

import asyncio
import json
import time

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from backend.common.log import log

from .cache import CompressCache, SummaryBlock
from .config import CompressConfig, get_threshold_ratio
from .prompts import (
    SUMMARY_PREAMBLE,
    build_batch_summary_prompt,
    build_merge_summary_prompt,
    build_summary_prompt,
)
from .token_utils import estimate_input_tokens

UTC = timezone.utc


@dataclass
class CompressResult:
    """压缩结果"""

    messages: list[dict]
    original_count: int
    compressed_count: int
    summary_block_count: int
    original_tokens: int
    compressed_tokens: int
    cache_hit: bool
    summary_generation_ms: int  # 缓存命中时为 0
    secondary_compression: bool = False  # 是否经过二次压缩
    degraded_keep_count: int | None = None  # 如果降级了，实际保留的消息数


class ContextCompressor:
    """上下文压缩器"""

    def __init__(self, config: CompressConfig) -> None:
        self.config = config
        self.cache = CompressCache(config)

    # ----------------------------------------------------------------
    # 公开 API
    # ----------------------------------------------------------------

    def needs_compression(
        self,
        messages: list[dict],
        system: str | list | None,
        max_context_length: int,
        api_key_metadata: dict | None = None,
    ) -> tuple[bool, int, int]:
        """
        判断是否需要压缩。

        Returns:
            (需要压缩, 估算token数, 消息数)
        """
        token_count = estimate_input_tokens(messages, system)
        message_count = len(messages)

        ratio = get_threshold_ratio(self.config, api_key_metadata)
        threshold = int(max_context_length * ratio)

        needs = (token_count > threshold) or (message_count > self.config.message_threshold)
        return needs, token_count, message_count

    async def compress_if_needed(
        self,
        messages: list[dict],
        system: str | list | None,
        max_context_length: int,
        summarizer: Callable,
        api_key_metadata: dict | None = None,
    ) -> CompressResult | None:
        """
        如果需要则执行压缩。

        Args:
            messages: 原始消息列表 (list[dict])
            system: system prompt
            max_context_length: 模型上下文长度
            summarizer: async (content: str, model: str) -> str
            api_key_metadata: API Key 级别配置

        Returns:
            CompressResult 或 None（不需要压缩）
        """
        # 1. 检查是否需要压缩
        needs, token_count, msg_count = self.needs_compression(
            messages, system, max_context_length, api_key_metadata
        )
        if not needs:
            return None

        log.info(
            f'[智能压缩] 触发 - Token={token_count}/{int(max_context_length * get_threshold_ratio(self.config, api_key_metadata))} '
            f'消息={msg_count}/{self.config.message_threshold}'
        )

        # 2. 查 Redis 缓存（Redis 故障时 existing_blocks=None, matched_count=0）
        existing_blocks, matched_count = await self.cache.find_matching(messages)
        cache_hit = existing_blocks is not None and matched_count > 0

        # 3. 如果有缓存，先尝试复用
        if cache_hit:
            remaining = messages[matched_count:]
            compressed_msgs = self._build_compressed_messages(existing_blocks, remaining)
            needs2, new_token_count, _ = self.needs_compression(
                compressed_msgs, system, max_context_length, api_key_metadata
            )
            if not needs2:
                log.info(
                    f'[智能压缩] 缓存复用完成 - Token: {token_count}→{new_token_count}, '
                    f'消息: {len(messages)}→{len(compressed_msgs)}'
                )
                return CompressResult(
                    messages=compressed_msgs,
                    original_count=len(messages),
                    compressed_count=len(compressed_msgs),
                    summary_block_count=len(existing_blocks),
                    original_tokens=token_count,
                    compressed_tokens=new_token_count,
                    cache_hit=True,
                    summary_generation_ms=0,
                )

        # 4. 增量压缩
        start_idx = matched_count if cache_hit else 0
        work_messages = messages[start_idx:]
        history, keep = self._split_messages(work_messages)

        if not history:
            if existing_blocks:
                compressed_msgs = self._build_compressed_messages(existing_blocks, work_messages)
                new_token_count = estimate_input_tokens(compressed_msgs, system)
                return CompressResult(
                    messages=compressed_msgs,
                    original_count=len(messages),
                    compressed_count=len(compressed_msgs),
                    summary_block_count=len(existing_blocks),
                    original_tokens=token_count,
                    compressed_tokens=new_token_count,
                    cache_hit=True,
                    summary_generation_ms=0,
                )
            return None

        log.info(
            f'[智能压缩] 增量压缩 {len(history)} 条新消息'
            f'（索引 {start_idx}-{start_idx + len(history)}），保留 {len(keep)} 条最新'
        )

        # 5. 生成新摘要（带超时和重试）
        t0 = time.monotonic()
        summary = await self._generate_summary_safe(history, summarizer)
        if summary is None:
            log.warning('[智能压缩] 摘要生成失败（含重试），降级为不压缩')
            return None
        generation_ms = int((time.monotonic() - t0) * 1000)

        # 6. 创建新摘要块
        new_block = SummaryBlock(
            block_id=f'blk_{int(time.time() * 1000)}',
            msg_start_idx=start_idx,
            msg_end_idx=start_idx + len(history),
            summary=summary,
            token_count=estimate_input_tokens([{'role': 'user', 'content': summary}], None),
            created_at=datetime.now(UTC).isoformat(),
        )

        all_blocks = (existing_blocks or []) + [new_block]

        # 7. 保存到 Redis（失败不影响流程）
        await self.cache.save(messages, start_idx + len(history), all_blocks)

        # 8. 构建压缩后的消息列表
        compressed_msgs = self._build_compressed_messages(all_blocks, keep)
        compressed_token_count = estimate_input_tokens(compressed_msgs, system)

        # 9. 检查压缩后是否仍超限 → 二次压缩 / 降级
        still_needs, _, _ = self.needs_compression(
            compressed_msgs, system, max_context_length, api_key_metadata
        )
        secondary = False
        degraded_keep = None

        if still_needs:
            log.info(
                f'[智能压缩] 首次压缩后仍超限 (token={compressed_token_count}), '
                f'尝试二次压缩和降级...'
            )
            result = await self._post_compress_recovery(
                messages=messages,
                system=system,
                max_context_length=max_context_length,
                api_key_metadata=api_key_metadata,
                all_blocks=all_blocks,
                keep_messages=keep,
                summarizer=summarizer,
                original_token_count=token_count,
                generation_ms=generation_ms,
                cache_hit=cache_hit,
            )
            if result is not None:
                return result
            # 所有恢复手段都失败了，仍返回首次压缩结果（比原始消息好）
            log.warning('[智能压缩] 二次压缩和降级均未能压到阈值内，返回首次压缩结果')

        log.info(
            f'[智能压缩] 完成: {len(messages)}→{len(compressed_msgs)} 条消息, '
            f'token: {token_count}→{compressed_token_count}, '
            f'摘要块: {len(all_blocks)}, 耗时: {generation_ms}ms'
        )

        return CompressResult(
            messages=compressed_msgs,
            original_count=len(messages),
            compressed_count=len(compressed_msgs),
            summary_block_count=len(all_blocks),
            original_tokens=token_count,
            compressed_tokens=compressed_token_count,
            cache_hit=cache_hit,
            summary_generation_ms=generation_ms,
            secondary_compression=secondary,
            degraded_keep_count=degraded_keep,
        )

    # ----------------------------------------------------------------
    # Phase 2: 二次压缩与降级恢复
    # ----------------------------------------------------------------

    async def _post_compress_recovery(
        self,
        *,
        messages: list[dict],
        system: str | list | None,
        max_context_length: int,
        api_key_metadata: dict | None,
        all_blocks: list[SummaryBlock],
        keep_messages: list[dict],
        summarizer: Callable,
        original_token_count: int,
        generation_ms: int,
        cache_hit: bool,
    ) -> CompressResult | None:
        """
        压缩后仍超限时的恢复策略：
        1. 二次压缩（合并所有摘要块为一个精简摘要）
        2. 降级保留消息数（6→4→2）
        3. 两者组合
        """
        # 策略 1: 二次压缩 —— 合并多个摘要块
        if self.config.enable_secondary_compression and len(all_blocks) > 1:
            log.info(f'[智能压缩] 尝试二次压缩: 合并 {len(all_blocks)} 个摘要块')
            t0 = time.monotonic()
            merged = await self._merge_summary_blocks(all_blocks, summarizer)
            merge_ms = int((time.monotonic() - t0) * 1000)

            if merged is not None:
                merged_block = SummaryBlock(
                    block_id=f'blk_merged_{int(time.time() * 1000)}',
                    msg_start_idx=all_blocks[0].msg_start_idx,
                    msg_end_idx=all_blocks[-1].msg_end_idx,
                    summary=merged,
                    token_count=estimate_input_tokens([{'role': 'user', 'content': merged}], None),
                    created_at=datetime.now(UTC).isoformat(),
                )

                compressed_msgs = self._build_compressed_messages([merged_block], keep_messages)
                compressed_tokens = estimate_input_tokens(compressed_msgs, system)
                needs, _, _ = self.needs_compression(
                    compressed_msgs, system, max_context_length, api_key_metadata
                )

                if not needs:
                    log.info(
                        f'[智能压缩] 二次压缩成功 - token: {original_token_count}→{compressed_tokens}, '
                        f'合并耗时: {merge_ms}ms'
                    )
                    return CompressResult(
                        messages=compressed_msgs,
                        original_count=len(messages),
                        compressed_count=len(compressed_msgs),
                        summary_block_count=1,
                        original_tokens=original_token_count,
                        compressed_tokens=compressed_tokens,
                        cache_hit=cache_hit,
                        summary_generation_ms=generation_ms + merge_ms,
                        secondary_compression=True,
                    )
                # 二次压缩后仍超限 → 用合并后的 block 继续降级
                all_blocks = [merged_block]

        # 策略 2: 降级保留消息数
        for degraded_count in self.config.degraded_keep_counts:
            if degraded_count >= len(keep_messages):
                continue  # 无法进一步减少

            log.info(f'[智能压缩] 降级保留消息数: {len(keep_messages)}→{degraded_count}')

            # 重新分割（用更少的保留数）
            total_work = list(keep_messages)  # 当前保留的消息
            if degraded_count < len(total_work):
                new_keep = total_work[-degraded_count:]
            else:
                new_keep = total_work

            compressed_msgs = self._build_compressed_messages(all_blocks, new_keep)
            compressed_tokens = estimate_input_tokens(compressed_msgs, system)
            needs, _, _ = self.needs_compression(
                compressed_msgs, system, max_context_length, api_key_metadata
            )

            if not needs:
                log.info(
                    f'[智能压缩] 降级成功 - 保留 {degraded_count} 条消息, '
                    f'token: {original_token_count}→{compressed_tokens}'
                )
                return CompressResult(
                    messages=compressed_msgs,
                    original_count=len(messages),
                    compressed_count=len(compressed_msgs),
                    summary_block_count=len(all_blocks),
                    original_tokens=original_token_count,
                    compressed_tokens=compressed_tokens,
                    cache_hit=cache_hit,
                    summary_generation_ms=generation_ms,
                    secondary_compression=len(all_blocks) == 1 and self.config.enable_secondary_compression,
                    degraded_keep_count=degraded_count,
                )

        return None

    async def _merge_summary_blocks(
        self, blocks: list[SummaryBlock], summarizer: Callable
    ) -> str | None:
        """合并多个摘要块为一个精简摘要"""
        blocks_text_parts = []
        for i, block in enumerate(blocks):
            blocks_text_parts.append(
                f'=== 摘要块 {i + 1} (消息 {block.msg_start_idx + 1}-{block.msg_end_idx}) ==='
            )
            blocks_text_parts.append(block.summary)
            blocks_text_parts.append('')
        blocks_text = '\n'.join(blocks_text_parts)

        # 目标字数：所有块总 token 的 60%（压缩率 40%）
        total_tokens = sum(b.token_count for b in blocks)
        max_chars = int(total_tokens * 0.6 * 1.5)  # token → 中文字符
        max_chars = max(max_chars, 2000)  # 至少 2000 字

        prompt = build_merge_summary_prompt(blocks_text, max_chars)

        try:
            return await self._call_summarizer_safe(prompt, summarizer)
        except Exception as e:
            log.warning(f'[智能压缩] 二次压缩（摘要合并）失败: {e}')
            return None

    # ----------------------------------------------------------------
    # 消息分割
    # ----------------------------------------------------------------

    def _split_messages(
        self, messages: list[dict], keep_count: int | None = None
    ) -> tuple[list[dict], list[dict]]:
        """
        分割为 (待压缩历史, 保留的最新消息)。
        保证 tool_use 和 tool_result 不被拆开。
        """
        actual_keep = keep_count or self.config.keep_message_count

        if len(messages) <= actual_keep:
            return [], messages

        split_idx = len(messages) - actual_keep
        split_idx = self._find_safe_split_point(messages, split_idx)

        return messages[:split_idx], messages[split_idx:]

    def _find_safe_split_point(self, messages: list[dict], proposed_idx: int) -> int:
        """找到安全的分割点，保护工具调用完整性"""
        # 收集保留区域内的 tool_result 的 tool_use_id
        pending_tool_use_ids: set[str] = set()

        for i in range(proposed_idx, len(messages)):
            tool_result_ids = self._extract_tool_result_ids(messages[i].get('content'))
            pending_tool_use_ids.update(tool_result_ids)

        if not pending_tool_use_ids:
            return proposed_idx

        # 向前扫描，找到所有相关的 tool_use
        for i in range(proposed_idx - 1, max(-1, proposed_idx - self.config.max_tool_lookback - 1), -1):
            tool_use_ids = self._extract_tool_use_ids(messages[i].get('content'))
            has_match = False
            for tid in tool_use_ids:
                if tid in pending_tool_use_ids:
                    has_match = True
                    pending_tool_use_ids.discard(tid)
            if has_match:
                proposed_idx = i
            if not pending_tool_use_ids:
                break

        return proposed_idx

    @staticmethod
    def _extract_tool_result_ids(content) -> list[str]:
        """从消息内容中提取 tool_result 的 tool_use_id"""
        if not isinstance(content, list):
            return []
        ids = []
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'tool_result':
                tid = block.get('tool_use_id')
                if tid:
                    ids.append(tid)
        return ids

    @staticmethod
    def _extract_tool_use_ids(content) -> list[str]:
        """从消息内容中提取 tool_use 的 id"""
        if not isinstance(content, list):
            return []
        ids = []
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'tool_use':
                tid = block.get('id')
                if tid:
                    ids.append(tid)
        return ids

    # ----------------------------------------------------------------
    # 摘要生成（带超时和重试）
    # ----------------------------------------------------------------

    async def _generate_summary_safe(
        self, messages: list[dict], summarizer: Callable
    ) -> str | None:
        """
        生成摘要，带超时保护和重试。

        Returns:
            摘要文本，失败返回 None
        """
        content = self._messages_to_text(messages)
        log.info(f'[智能压缩] 生成摘要 - {len(content)} 字符')

        if len(content) > self.config.max_batch_chars:
            prompt = None  # 分批模式在内部处理
            return await self._generate_batch_summary_safe(content, summarizer)

        max_chars = self.config.max_summary_tokens * 3 // 2
        prompt = build_summary_prompt(content, max_chars)

        return await self._call_summarizer_safe(prompt, summarizer)

    async def _call_summarizer_safe(
        self, prompt: str, summarizer: Callable
    ) -> str | None:
        """
        调用摘要生成器，带超时和重试。

        Returns:
            摘要文本，失败返回 None
        """
        last_error = None
        max_attempts = 1 + self.config.summary_max_retries

        for attempt in range(max_attempts):
            try:
                async with asyncio.timeout(self.config.summary_timeout):
                    result = await summarizer(prompt, self.config.summary_model)

                if result:
                    if attempt > 0:
                        log.info(f'[智能压缩] 摘要生成第 {attempt + 1} 次尝试成功')
                    log.info(
                        f'[智能压缩][内部调用] model={self.config.summary_model} '
                        f'input_chars={len(prompt)} output_chars={len(result)}'
                    )
                    return result

                log.warning(f'[智能压缩] 摘要生成返回空结果 (attempt {attempt + 1}/{max_attempts})')
                last_error = ValueError('empty summary result')

            except asyncio.TimeoutError:
                log.warning(
                    f'[智能压缩] 摘要生成超时 ({self.config.summary_timeout}s) '
                    f'(attempt {attempt + 1}/{max_attempts})'
                )
                last_error = TimeoutError(f'summary generation timed out after {self.config.summary_timeout}s')

            except Exception as e:
                log.warning(
                    f'[智能压缩] 摘要生成异常: {e} '
                    f'(attempt {attempt + 1}/{max_attempts})'
                )
                last_error = e

            # 重试前等待（指数退避：1s, 2s, ...）
            if attempt < max_attempts - 1:
                wait = (attempt + 1) * 1.0
                log.info(f'[智能压缩] {wait}s 后重试...')
                await asyncio.sleep(wait)

        log.error(f'[智能压缩] 摘要生成最终失败 ({max_attempts} 次尝试): {last_error}')
        return None

    async def _generate_batch_summary_safe(
        self, content: str, summarizer: Callable
    ) -> str | None:
        """分批生成摘要（带安全保护）"""
        batches = []
        while content:
            end = min(self.config.max_batch_chars, len(content))
            batches.append(content[:end])
            content = content[end:]

        log.info(f'[智能压缩] 分批处理 {len(batches)} 批')
        max_chars_per_batch = max(500, self.config.max_summary_tokens * 3 // 2 // len(batches))

        summaries = []
        for i, batch in enumerate(batches):
            prompt = build_batch_summary_prompt(batch, i + 1, len(batches), max_chars_per_batch)
            result = await self._call_summarizer_safe(prompt, summarizer)

            if result is None:
                log.warning(f'[智能压缩] 批次 {i + 1}/{len(batches)} 失败，中止分批摘要')
                return None

            summaries.append(result)
            log.debug(f'[智能压缩] 批次 {i + 1}/{len(batches)} 完成')

        parts = []
        for i, summary in enumerate(summaries):
            parts.append(f'【第 {i + 1} 部分】')
            parts.append(summary)
        return '\n\n'.join(parts)

    # ----------------------------------------------------------------
    # 消息转文本
    # ----------------------------------------------------------------

    def _messages_to_text(self, messages: list[dict]) -> str:
        """将消息转换为文本"""
        parts = []
        user_msg_count = 0

        for msg in messages:
            role = msg.get('role', 'unknown')
            if role == 'user':
                user_msg_count += 1
                parts.append(f'[用户消息 #{user_msg_count}]: ')
            else:
                parts.append(f'[{role}]: ')

            content = msg.get('content', '')
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                parts.append(self._extract_text_content(content))
            else:
                parts.append(str(content))
            parts.append('\n\n')

        return ''.join(parts)

    def _extract_text_content(self, content: list) -> str:
        """从复杂内容块中提取文本"""
        texts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = block.get('type')
            if block_type == 'text':
                text = block.get('text', '')
                if text:
                    texts.append(text)
            elif block_type == 'tool_use':
                name = block.get('name', '')
                tid = block.get('id', '')
                input_data = block.get('input', {})
                keys = ', '.join(input_data.keys()) if isinstance(input_data, dict) else ''
                texts.append(f'[调用工具: {name}({keys}) id={tid}]')
            elif block_type == 'tool_result':
                tid = block.get('tool_use_id', '')
                result_content = self._extract_tool_result_text(block.get('content'))
                truncated = self._truncate_tool_result(result_content)
                texts.append(f'[工具结果 {tid}]:\n{truncated}')
        return '\n'.join(texts)

    def _extract_tool_result_text(self, content) -> str:
        """从工具结果内容提取文本"""
        if content is None:
            return ''
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    texts.append(item.get('text', ''))
                elif isinstance(item, str):
                    texts.append(item)
            return '\n'.join(texts)
        return str(content)

    def _truncate_tool_result(self, content: str) -> str:
        """智能裁剪工具结果（保留头尾）"""
        if len(content) <= self.config.max_tool_result_length:
            return content

        head = content[: self.config.keep_head_chars]
        tail = content[-self.config.keep_tail_chars :]
        omitted = len(content) - self.config.keep_head_chars - self.config.keep_tail_chars

        return f'{head}\n\n... [省略 {omitted} 字符] ...\n\n{tail}'

    # ----------------------------------------------------------------
    # 压缩后消息构建
    # ----------------------------------------------------------------

    @staticmethod
    def _build_compressed_messages(
        blocks: list[SummaryBlock], keep_messages: list[dict]
    ) -> list[dict]:
        """构建压缩后的消息列表"""
        summary_parts = [
            '[历史对话摘要 - 结构化压缩]',
            SUMMARY_PREAMBLE,
            '',
        ]
        for i, block in enumerate(blocks):
            summary_parts.append(
                f'=== 摘要块 {i + 1} (消息 {block.msg_start_idx + 1}-{block.msg_end_idx}) ==='
            )
            summary_parts.append(block.summary)
            summary_parts.append('')
        summary_parts.append('[摘要结束，以下是最近的对话]')

        summary_text = '\n'.join(summary_parts)

        compressed = [
            {'role': 'user', 'content': summary_text},
            {
                'role': 'assistant',
                'content': f'好的，我已了解之前的对话上下文（共 {len(blocks)} 个摘要块）。请继续。',
            },
            *keep_messages,
        ]
        return compressed
