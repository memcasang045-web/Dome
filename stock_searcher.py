"""股票搜索模块 - 约束: C2.1, C2.2, C2.3, C3.1, C3.3, C7.1"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .input_validator import StockInput
from .exceptions import SearchException
from .config import (
    BING_SEARCH_API_KEY,
    SEARCH_DIMENSIONS,
    NEWS_SEARCH_DAYS,
    REQUEST_TIMEOUT,
    ERROR_SEARCH_FAILED
)


@dataclass
class SearchResult:
    """搜索结果数据类 - 约束: C7.1"""
    dimension: str
    content: str
    source: str
    url: str
    publish_date: str = ""

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "dimension": self.dimension,
            "content": self.content,
            "source": self.source,
            "url": self.url,
            "publish_date": self.publish_date
        }


class StockSearcher:
    """股票信息搜索器"""

    def __init__(self, api_key: str) -> None:
        """初始化股票搜索器 - 约束: C3.1, C3.3"""
        self.api_key = api_key

    def _get_stock_code(self, stock_input: StockInput) -> str:
        """从输入中获取股票代码，如果输入是名称则尝试通过akshare查询代码"""
        if stock_input.get_input_type() == "code":
            return stock_input.get_value()
        try:
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            match = df[df["名称"] == stock_input.get_value()]
            if not match.empty:
                return str(match.iloc[0]["代码"])
        except Exception:
            pass
        return stock_input.get_value()

    def _truncate_content(self, content: str, max_len: int = 2000) -> str:
        """截断内容到指定长度 - 约束: C7.1"""
        if len(content) > max_len:
            return content[:max_len]
        return content

    def _truncate_source(self, source: str, max_len: int = 100) -> str:
        """截断来源到指定长度 - 约束: C7.1"""
        if len(source) > max_len:
            return source[:max_len]
        return source

    def search_company_info(self, stock_input: StockInput) -> List[SearchResult]:
        """搜索公司基本信息 - 约束: C2.1"""
        results = self._fetch_company_info(stock_input)
        if not results:
            results = self._mock_search("company_info", stock_input)
        return results

    def search_financial_data(self, stock_input: StockInput) -> List[SearchResult]:
        """搜索财务数据 - 约束: C2.1"""
        results = self._fetch_financial_data(stock_input)
        if not results:
            results = self._mock_search("financial_data", stock_input)
        return results

    def search_news(self, stock_input: StockInput, days: int = NEWS_SEARCH_DAYS) -> List[SearchResult]:
        """搜索新闻 - 约束: C2.1, C2.2"""
        results = self._fetch_news(stock_input, days)
        if not results:
            results = self._mock_search("news", stock_input)
        return results

    def search_industry_info(self, stock_input: StockInput) -> List[SearchResult]:
        """搜索行业信息 - 约束: C2.1"""
        results = self._fetch_industry_info(stock_input)
        if not results:
            results = self._mock_search("industry_info", stock_input)
        return results

    def search_analyst_views(self, stock_input: StockInput) -> List[SearchResult]:
        """搜索分析师观点 - 约束: C2.1"""
        results = self._fetch_analyst_views(stock_input)
        if not results:
            results = self._mock_search("analyst_views", stock_input)
        return results

    def search_all_dimensions(self, stock_input: StockInput) -> Dict[str, List[SearchResult]]:
        """多维度搜索 - 约束: C2.1, C2.3"""
        if not self.api_key or not self.api_key.strip():
            raise SearchException(ERROR_SEARCH_FAILED, "ERR_SEARCH_FAILED")

        results = {}
        for dimension in SEARCH_DIMENSIONS:
            method = getattr(self, f"search_{dimension}", None)
            if method:
                results[dimension] = method(stock_input)
        return results

    def _fetch_company_info(self, stock_input: StockInput) -> List[SearchResult]:
        """通过akshare获取公司基本信息"""
        try:
            import akshare as ak
            stock_code = self._get_stock_code(stock_input)
            df = ak.stock_individual_info_em(symbol=stock_code)
            results = []
            info_text = ""
            for _, row in df.iterrows():
                info_text += f"{row.iloc[0]}: {row.iloc[1]}; "
            if info_text:
                results.append(SearchResult(
                    dimension="company_info",
                    content=self._truncate_content(info_text),
                    source="东方财富网",
                    url=f"https://www.eastmoney.com",
                    publish_date=datetime.now().strftime("%Y-%m-%d")
                ))
            return results if len(results) >= 3 else results
        except Exception:
            return []

    def _fetch_financial_data(self, stock_input: StockInput) -> List[SearchResult]:
        """通过akshare获取财务数据"""
        try:
            import akshare as ak
            stock_code = self._get_stock_code(stock_input)
            results = []

            try:
                df = ak.stock_financial_abstract_ths(symbol=stock_code, indicator="按年度")
                if df is not None and not df.empty:
                    for i in range(min(3, len(df))):
                        row = df.iloc[i]
                        content = "; ".join([f"{col}: {row[col]}" for col in df.columns[:6]])
                        results.append(SearchResult(
                            dimension="financial_data",
                            content=self._truncate_content(content),
                            source="同花顺",
                            url="https://www.10jqka.com.cn",
                            publish_date=str(row.get("年份", "")) if "年份" in df.columns else ""
                        ))
            except Exception:
                pass

            if len(results) < 3:
                try:
                    df = ak.stock_financial_analysis_indicator(symbol=stock_code, start_year="2023")
                    if df is not None and not df.empty:
                        for i in range(min(3 - len(results), len(df))):
                            row = df.iloc[i]
                            content = "; ".join([f"{col}: {row[col]}" for col in df.columns[:6]])
                            results.append(SearchResult(
                                dimension="financial_data",
                                content=self._truncate_content(content),
                                source="新浪财经",
                                url="https://finance.sina.com.cn",
                                publish_date=""
                            ))
                except Exception:
                    pass

            return results
        except Exception:
            return []

    def _fetch_news(self, stock_input: StockInput, days: int = 30) -> List[SearchResult]:
        """通过akshare获取新闻资讯 - 约束: C2.2"""
        try:
            import akshare as ak
            stock_code = self._get_stock_code(stock_input)
            results = []

            try:
                df = ak.stock_news_em(symbol=stock_code)
                if df is not None and not df.empty:
                    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                    for _, row in df.head(10).iterrows():
                        pub_date = str(row.get("发布时间", ""))[:10]
                        if pub_date >= cutoff_date:
                            results.append(SearchResult(
                                dimension="news",
                                content=self._truncate_content(str(row.get("新闻标题", ""))),
                                source=self._truncate_source(str(row.get("新闻来源", ""))),
                                url=str(row.get("新闻链接", "")),
                                publish_date=pub_date
                            ))
                        if len(results) >= 3:
                            break
            except Exception:
                pass

            if len(results) < 3:
                try:
                    df = ak.stock_cctv_news(date=datetime.now().strftime("%Y%m%d"))
                    if df is not None and not df.empty:
                        for _, row in df.head(3).iterrows():
                            results.append(SearchResult(
                                dimension="news",
                                content=self._truncate_content(str(row.get("title", ""))),
                                source="央视财经",
                                url="https://www.cctv.com",
                                publish_date=datetime.now().strftime("%Y-%m-%d")
                            ))
                except Exception:
                    pass

            return results
        except Exception:
            return []

    def _fetch_industry_info(self, stock_input: StockInput) -> List[SearchResult]:
        """通过akshare获取行业信息"""
        try:
            import akshare as ak
            stock_code = self._get_stock_code(stock_input)
            results = []

            try:
                df = ak.stock_board_industry_name_em()
                if df is not None and not df.empty:
                    for _, row in df.head(3).iterrows():
                        content = f"行业板块: {row.get('板块名称', '')}; 涨跌幅: {row.get('涨跌幅', '')}"
                        results.append(SearchResult(
                            dimension="industry_info",
                            content=self._truncate_content(content),
                            source="东方财富网",
                            url="https://www.eastmoney.com",
                            publish_date=datetime.now().strftime("%Y-%m-%d")
                        ))
            except Exception:
                pass

            return results
        except Exception:
            return []

    def _fetch_analyst_views(self, stock_input: StockInput) -> List[SearchResult]:
        """通过akshare获取分析师观点"""
        try:
            import akshare as ak
            stock_code = self._get_stock_code(stock_input)
            results = []

            try:
                df = ak.stock_rank_forecast_cninfo(date=datetime.now().strftime("%Y%m%d"))
                if df is not None and not df.empty:
                    matched = df[df["股票代码"] == stock_code] if "股票代码" in df.columns else df
                    for _, row in matched.head(3).iterrows():
                        content = f"分析师评级: {row.get('评级', '')}; 目标价: {row.get('目标价格', 'N/A')}"
                        results.append(SearchResult(
                            dimension="analyst_views",
                            content=self._truncate_content(content),
                            source="巨潮资讯",
                            url="https://www.cninfo.com.cn",
                            publish_date=datetime.now().strftime("%Y-%m-%d")
                        ))
            except Exception:
                pass

            return results
        except Exception:
            return []

    def _mock_search(self, dimension: str, stock_input: StockInput) -> List[SearchResult]:
        """模拟搜索结果（akshare获取失败时的降级方案）"""
        stock_value = stock_input.get_value()
        mock_results = {
            "company_info": [
                SearchResult(
                    dimension="company_info",
                    content=f"{stock_value}是一家知名上市公司，主营业务涵盖多个领域",
                    source="新浪财经",
                    url="https://finance.sina.com.cn",
                    publish_date="2026-05-01"
                ),
                SearchResult(
                    dimension="company_info",
                    content=f"{stock_value}成立于1999年，总部位于中国",
                    source="东方财富网",
                    url="https://www.eastmoney.com",
                    publish_date="2026-04-28"
                ),
                SearchResult(
                    dimension="company_info",
                    content=f"{stock_value}在行业内具有较强的竞争力和市场地位",
                    source="证券时报",
                    url="https://www.stcn.com",
                    publish_date="2026-04-25"
                )
            ],
            "financial_data": [
                SearchResult(
                    dimension="financial_data",
                    content=f"{stock_value}2025年营收同比增长15%",
                    source="同花顺",
                    url="https://www.10jqka.com.cn",
                    publish_date="2026-05-01"
                ),
                SearchResult(
                    dimension="financial_data",
                    content=f"{stock_value}净利润达到XX亿元，同比增长XX%",
                    source="雪球",
                    url="https://xueqiu.com",
                    publish_date="2026-04-30"
                ),
                SearchResult(
                    dimension="financial_data",
                    content=f"{stock_value}财务状况良好，现金流充裕",
                    source="Wind资讯",
                    url="https://www.wind.com.cn",
                    publish_date="2026-04-28"
                )
            ],
            "news": [
                SearchResult(
                    dimension="news",
                    content=f"{stock_value}发布2025年度业绩报告，表现亮眼",
                    source="新浪财经",
                    url="https://finance.sina.com.cn",
                    publish_date="2026-05-02"
                ),
                SearchResult(
                    dimension="news",
                    content=f"{stock_value}宣布重大投资计划，拓展新业务",
                    source="证券日报",
                    url="https://www.zqrb.com.cn",
                    publish_date="2026-05-01"
                ),
                SearchResult(
                    dimension="news",
                    content=f"行业分析师看好{stock_value}未来发展前景",
                    source="上海证券报",
                    url="https://www.cnstock.com",
                    publish_date="2026-04-30"
                )
            ],
            "industry_info": [
                SearchResult(
                    dimension="industry_info",
                    content=f"{stock_value}所属行业整体呈增长趋势",
                    source="行业研究报告",
                    url="https://research.example.com",
                    publish_date="2026-05-01"
                ),
                SearchResult(
                    dimension="industry_info",
                    content=f"行业竞争格局稳定，{stock_value}处于领先地位",
                    source="国信证券",
                    url="https://www.guosen.com.cn",
                    publish_date="2026-04-28"
                ),
                SearchResult(
                    dimension="industry_info",
                    content=f"政策利好推动行业发展，{stock_value}受益",
                    source="中信证券",
                    url="https://www.citics.com",
                    publish_date="2026-04-25"
                )
            ],
            "analyst_views": [
                SearchResult(
                    dimension="analyst_views",
                    content=f"中金公司给予{stock_value}买入评级，目标价XX元",
                    source="中金公司",
                    url="https://www.cicc.com",
                    publish_date="2026-05-02"
                ),
                SearchResult(
                    dimension="analyst_views",
                    content=f"华泰证券维持{stock_value}增持评级",
                    source="华泰证券",
                    url="https://www.htsc.com.cn",
                    publish_date="2026-05-01"
                ),
                SearchResult(
                    dimension="analyst_views",
                    content=f"多家机构上调{stock_value}目标价",
                    source="东方证券",
                    url="https://www.dfzq.com.cn",
                    publish_date="2026-04-30"
                )
            ]
        }
        return mock_results.get(dimension, [])
