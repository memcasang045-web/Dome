"""异常类定义 - 约束: C6.1, C6.2, C6.3"""

class StockReportException(Exception):
    """基础异常类"""
    error_code: str = ""

    def __init__(self, message: str, error_code: str = ""):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ValidationException(StockReportException):
    """输入验证异常"""
    error_code: str = "ERR_INVALID_INPUT"


class SearchException(StockReportException):
    """搜索异常"""
    error_code: str = "ERR_SEARCH_FAILED"


class AnalysisException(StockReportException):
    """分析异常"""
    error_code: str = "ERR_ANALYSIS_FAILED"


class ReportGenerationException(StockReportException):
    """报告生成异常"""
    error_code: str = "ERR_REPORT_GENERATION"
