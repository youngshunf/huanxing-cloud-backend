"""HASN 社区模块（hasn_community）。

从原 hasn 巨型模块拆分而来，承载社区帖子/文章/评论/关注/点赞/收藏等能力。
对外路由前缀 /api/v1/community/*（app / agent 等 scope），与身份表（HasnHumans/HasnAgents
留在 hasn 模块）通过跨模块 import 协作：社区 → 身份、runtime → 社区，无循环依赖。
"""
