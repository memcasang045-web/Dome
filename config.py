"""配置模块 - 约束: C3.3, C2.1, C2.2, C3.1, C3.2, C5.1, C6.1, C6.2, C6.3"""

import os
from typing import List

# API配置 - 约束: C3.3
BING_SEARCH_API_KEY: str = os.getenv("BING_SEARCH_API_KEY", "")
DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
QWEN_API_KEY: str = DASHSCOPE_API_KEY or os.getenv("QWEN_API_KEY", "")
QWEN_MODEL: str = "qwen3.5-plus"
QWEN_API_URL: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 搜索配置 - 约束: C2.1, C2.2
SEARCH_DIMENSIONS: List[str] = [
    "company_info",
    "financial_data",
    "news",
    "industry_info",
    "analyst_views"
]
NEWS_SEARCH_DAYS: int = 30

# 性能配置 - 约束: C3.1, C3.2, C5.1
REQUEST_TIMEOUT: int = 30
QWEN_TIMEOUT: int = 60
MAX_TOTAL_TIME: int = 60

# 错误消息 - 约束: C6.1, C6.2, C6.3
ERROR_INVALID_INPUT: str = "输入无效，请输入有效的股票代码或名称"
ERROR_SEARCH_FAILED: str = "搜索失败，请检查网络连接后重试"
ERROR_ANALYSIS_FAILED: str = "分析失败，请稍后重试"
