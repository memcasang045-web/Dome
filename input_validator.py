"""输入验证模块 - 约束: C1.1, C1.2, C1.3"""

import re
from typing import Optional
from .exceptions import ValidationException
from .config import ERROR_INVALID_INPUT


def validate_stock_code(code: str) -> bool:
    """
    验证股票代码格式
    约束: C1.1 - 股票代码必须为6位数字
    """
    pattern = re.compile(r'^[0-9]{6}$')
    return bool(pattern.match(code))


def is_stock_code(user_input: str) -> bool:
    """
    判断输入是否为股票代码
    约束: C1.3
    """
    return validate_stock_code(user_input)


class StockInput:
    """股票输入对象"""
    
    def __init__(self, user_input: str) -> None:
        """
        初始化股票输入
        约束: C1.1, C1.2, C1.3
        """
        if not user_input or not user_input.strip():
            raise ValidationException(ERROR_INVALID_INPUT, "ERR_INVALID_INPUT")
        
        self._value = user_input.strip()
        self._input_type = self._determine_input_type()
        
        if not self.is_valid():
            raise ValidationException(ERROR_INVALID_INPUT, "ERR_INVALID_INPUT")
    
    def _determine_input_type(self) -> str:
        """确定输入类型"""
        if is_stock_code(self._value):
            return "code"
        elif self._is_stock_name(self._value):
            return "name"
        return "invalid"
    
    def _is_stock_name(self, name: str) -> bool:
        """验证股票名称格式 - 约束: C1.2"""
        pattern = re.compile(r'^[a-zA-Z\u4e00-\u9fa5]{2,20}$')
        return bool(pattern.match(name))
    
    def get_input_type(self) -> str:
        """获取输入类型"""
        return self._input_type
    
    def get_value(self) -> str:
        """获取原始输入值"""
        return self._value
    
    def is_valid(self) -> bool:
        """验证输入是否有效"""
        return self._input_type in ("code", "name")
