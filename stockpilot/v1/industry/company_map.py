"""
StockPilot V1.4.2
Industry company mapping engine
"""

COMPANY_MAP = {
    "688008": {
        "name": "澜起科技",
        "industries": ["AI存储", "DDR5", "内存接口"],
        "role": "核心公司",
        "importance": 90,
    },
    "603986": {
        "name": "兆易创新",
        "industries": ["存储芯片", "半导体"],
        "role": "核心公司",
        "importance": 85,
    },
    "300308": {
        "name": "中际旭创",
        "industries": ["CPO", "光模块", "AI算力"],
        "role": "产业龙头",
        "importance": 95,
    },
}


def get_company_profile(code):
    return COMPANY_MAP.get(code, {})


def find_by_industry(industry):
    return [
        company for company in COMPANY_MAP.values()
        if industry in company["industries"]
    ]
