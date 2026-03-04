"""Token 估算工具
@author Guardian

从 gateway.py 的 _estimate_input_tokens 提取为独立函数，
供压缩器和网关共用。
"""


def estimate_input_tokens(messages: list[dict], system: str | list | None = None) -> int:
    """
    快速估算输入 token 数（无需调用 tokenizer，按字符数粗算）

    中文字符按 ~1.5 chars/token，ASCII 按 ~4 chars/token
    """
    char_count_cjk = 0
    char_count_ascii = 0

    def _count(text: str) -> None:
        nonlocal char_count_cjk, char_count_ascii
        if not text:
            return
        for ch in text:
            if ord(ch) > 0x2E80:
                char_count_cjk += 1
            else:
                char_count_ascii += 1

    def _extract_text(content) -> None:
        """从 str / list[dict] / dict 中提取文本并计数"""
        if content is None:
            return
        if isinstance(content, str):
            _count(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    _count(block.get('text') or '')
                    # 工具调用/结果也包含文本
                    if block.get('type') == 'tool_result':
                        _extract_text(block.get('content'))
                elif isinstance(block, str):
                    _count(block)
        elif isinstance(content, dict):
            _count(content.get('text') or '')

    if system:
        _extract_text(system)

    for msg in messages:
        content = msg.get('content', '') if isinstance(msg, dict) else getattr(msg, 'content', '')
        _extract_text(content)

    estimated = int(char_count_cjk / 1.5 + char_count_ascii / 4) + len(messages) * 4
    return estimated
