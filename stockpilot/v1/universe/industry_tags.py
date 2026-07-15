"""
StockPilot V1.9.5 Industry Tag Library

Industry and theme mapping for A-share research.
"""

INDUSTRY_TAGS = {
    "AI算力": {
        "tags": ["CPO", "光模块", "PCB", "液冷", "服务器"],
        "keywords": ["AI", "算力", "高速互联"]
    },
    "AI存储": {
        "tags": ["DDR5", "HBM", "存储芯片", "内存接口"],
        "keywords": ["存储", "半导体"]
    },
    "先进封装": {
        "tags": ["Chiplet", "玻璃基板", "封测", "材料"],
        "keywords": ["封装", "晶圆"]
    },
    "半导体设备": {
        "tags": ["光刻", "刻蚀", "清洗", "检测"],
        "keywords": ["设备", "国产替代"]
    },
    "机器人": {
        "tags": ["人形机器人", "机器视觉", "减速器", "伺服"],
        "keywords": ["具身智能"]
    }
}


def get_theme(name):
    return INDUSTRY_TAGS.get(name, {})


def list_themes():
    return list(INDUSTRY_TAGS.keys())
