"""主入口模块"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.input_validator import StockInput
from src.stock_searcher import StockSearcher
from src.report_generator import ReportGenerator, StockReport
from src.exceptions import ValidationException, SearchException, AnalysisException, ReportGenerationException
from src.config import BING_SEARCH_API_KEY, QWEN_API_KEY, DASHSCOPE_API_KEY


def main(stock_input_str: str) -> StockReport:
    """
    主流程：生成股票研究报告

    参数:
        stock_input_str: 股票代码或名称

    返回:
        StockReport: 结构化报告对象

    异常:
        ValidationException: 输入无效
        SearchException: 搜索失败
        AnalysisException: 分析失败
        ReportGenerationException: 报告生成失败
    """
    stock_input = StockInput(stock_input_str)

    searcher = StockSearcher(BING_SEARCH_API_KEY or "akshare_mode")
    search_results = searcher.search_all_dimensions(stock_input)

    generator = ReportGenerator(QWEN_API_KEY or DASHSCOPE_API_KEY)
    report = generator.generate_report(stock_input, search_results)

    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python src/main.py <股票代码或名称>")
        sys.exit(1)

    try:
        report = main(sys.argv[1])
        print(report.to_json())
    except ValidationException as e:
        print(f"输入验证失败: {e.message}")
    except SearchException as e:
        print(f"搜索失败: {e.message}")
    except AnalysisException as e:
        print(f"分析失败: {e.message}")
    except ReportGenerationException as e:
        print(f"报告生成失败: {e.message}")
