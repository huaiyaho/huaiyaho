"""
StockPilot V1.7.3 Data Adapter
统一行情数据入口。

设计目标：
- 屏蔽不同行情来源差异
- 支持同花顺导出CSV
- 支持未来接入 stock-sdk / API
- 为扫描、回测、Dashboard提供统一数据格式
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class MarketBar:
    code: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float = 0


class DataAdapter:
    """统一行情适配器"""

    def normalize(self, rows: List[Dict[str, Any]]) -> List[MarketBar]:
        result = []

        for row in rows:
            result.append(
                MarketBar(
                    code=str(row.get("code", "")),
                    date=str(row.get("date", datetime.now().date())),
                    open=float(row.get("open", 0)),
                    high=float(row.get("high", 0)),
                    low=float(row.get("low", 0)),
                    close=float(row.get("close", 0)),
                    volume=float(row.get("volume", 0)),
                    amount=float(row.get("amount", 0)),
                )
            )

        return result

    def from_csv(self, rows: List[Dict[str, Any]]) -> List[MarketBar]:
        """解析同花顺/其他软件导出的CSV数据"""
        return self.normalize(rows)

    def from_api(self, payload: Dict[str, Any]) -> List[MarketBar]:
        """未来接入行情API"""
        return self.normalize(payload.get("data", []))
