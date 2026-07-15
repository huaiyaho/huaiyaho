"""
StockPilot V1.8.1 综合评分引擎

整合:
- 技术趋势
- 产业趋势
- 资金热度
- 风险扣分
"""


def calculate_score(technical=0, industry=0, capital=0, risk=0):
    """计算股票综合评分，满分100"""
    score = (
        technical * 0.30
        + industry * 0.35
        + capital * 0.25
        - risk * 0.10
    )
    return round(max(0, min(100, score)), 2)


def classify(score):
    if score >= 85:
        return "核心关注"
    if score >= 70:
        return "重点观察"
    if score >= 50:
        return "普通"
    return "规避"


def build_stock_score(stock):
    score = calculate_score(
        stock.get("technical", 0),
        stock.get("industry", 0),
        stock.get("capital", 0),
        stock.get("risk", 0),
    )
    return {
        "name": stock.get("name"),
        "score": score,
        "level": classify(score),
    }
