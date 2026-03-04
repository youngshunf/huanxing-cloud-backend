"""摘要提示词模板
@author Guardian

沿用 claude-api 验证过的 9 节 XML 结构化摘要格式。
"""

SUMMARY_PREAMBLE = (
    '上下文已使用结构化9节算法压缩。所有关键技术细节、代码模式、'
    '架构决策和用户意图已保留，可无缝继续对话。'
)


def build_summary_prompt(content: str, max_chars: int) -> str:
    """
    构建摘要生成提示词

    Args:
        content: 待压缩的对话历史文本
        max_chars: 目标摘要最大字符数
    """
    return f"""你的任务是创建迄今为止对话的详细摘要，密切关注用户的明确请求和之前的操作。
该摘要应全面捕获技术细节、代码模式和架构决策，这些对于在不丢失上下文的情况下继续开发工作至关重要。

请按照以下 XML 结构生成摘要（控制在 {max_chars} 字以内）：

<summary>
  <primary_request>
    【主要请求和意图】
    详细描述用户的所有明确请求和意图，包括任何修订或澄清。
    按时间顺序列出，标注意图的变化。
  </primary_request>

  <technical_concepts>
    【关键技术概念】
    列出讨论的所有重要技术概念、技术栈和框架：
    - 概念名称: 说明及其在项目中的作用
  </technical_concepts>

  <files_and_code>
    【文件和代码部分】
    列举检查、修改或创建的具体文件，包含关键代码片段：
    - 文件路径: path/to/file
      操作: 创建/修改/删除/读取
      关键代码: [代码片段，保留完整的函数签名和核心逻辑]
  </files_and_code>

  <errors_and_fixes>
    【错误和修复】
    列出遇到的所有错误及其修复方法：
    - 错误描述: 具体错误信息
      原因分析: 为什么发生
      修复方法: 如何解决
  </errors_and_fixes>

  <problem_solving>
    【问题解决】
    记录已解决的问题和正在进行的故障排除工作，包括尝试过的方法。
  </problem_solving>

  <user_messages>
    【所有用户消息】
    按时间顺序列出所有用户消息的要点（排除工具结果），以理解意图变化：
    1. [消息要点]
    2. [消息要点]
  </user_messages>

  <pending_tasks>
    【待处理任务】
    概述明确要求但尚未完成的任务：
    - [ ] 任务描述
  </pending_tasks>

  <current_work>
    【当前工作】
    详细描述摘要请求前正在进行的具体工作：
    - 正在处理的文件和代码
    - 当前的实现状态
    - 遇到的阻塞点
  </current_work>

  <next_steps>
    【可选的下一步】
    列出与当前工作相关的建议后续步骤：
    1. 步骤描述
    2. 步骤描述
  </next_steps>
</summary>

【对话历史】
{content}

请直接输出 XML 格式的摘要，确保结构完整。"""


def build_batch_summary_prompt(batch_content: str, batch_num: int, total_batches: int, max_chars: int) -> str:
    """构建分批摘要提示词"""
    return f"""请将以下对话片段（第 {batch_num}/{total_batches} 部分）压缩为结构化的 XML 摘要。

【输出要求】
1. 使用 XML 格式，保持结构清晰
2. 保留关键技术细节、代码片段和用户意图
3. 控制在 {max_chars} 字以内

请按以下结构输出：
<batch_summary part="{batch_num}">
  <key_points>关键要点和决策</key_points>
  <files_changed>涉及的文件和代码变更</files_changed>
  <user_requests>用户的请求和反馈</user_requests>
  <progress>完成的工作和当前状态</progress>
</batch_summary>

【对话片段】
{batch_content}

请直接输出 XML 格式摘要。"""


def build_merge_summary_prompt(blocks_text: str, max_chars: int) -> str:
    """
    构建摘要块合并提示词（二次压缩）。

    当多个摘要块合计仍超限时，将它们合并为一个更精简的摘要。
    """
    return f"""你的任务是将多个对话摘要块合并为一个更精简的综合摘要。

这些摘要块是之前对话历史的增量压缩结果。现在需要将它们合并为一个整体摘要，
以减少总 token 数。请保留最关键的信息，删除重复和过时的内容。

【合并原则】
1. 保留最新的决策和结论，删除被推翻的旧决策
2. 合并重复的技术概念和文件引用
3. 保留所有待处理任务和当前工作状态
4. 代码片段只保留最终版本
5. 控制在 {max_chars} 字以内

请按以下 XML 结构输出：
<summary>
  <primary_request>用户的最终请求和意图（合并后）</primary_request>
  <technical_concepts>关键技术概念（去重后）</technical_concepts>
  <files_and_code>涉及的文件和关键代码（最终版本）</files_and_code>
  <errors_and_fixes>错误及修复（仅保留仍相关的）</errors_and_fixes>
  <problem_solving>问题解决过程（精简）</problem_solving>
  <user_messages>用户消息要点（按时间序，精简）</user_messages>
  <pending_tasks>待处理任务（仅未完成的）</pending_tasks>
  <current_work>当前正在进行的工作</current_work>
  <next_steps>建议的下一步</next_steps>
</summary>

【待合并的摘要块】
{blocks_text}

请直接输出合并后的 XML 格式摘要。"""
