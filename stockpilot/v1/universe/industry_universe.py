"""
StockPilot Full Industry Universe

全行业产业分类框架，不局限于单一热点方向。
用于行业轮动、产业链映射、事件受益分析。
"""

INDUSTRY_UNIVERSE = {
    "technology": {
        "semiconductor": ["芯片设计", "半导体设备", "半导体材料", "封装测试"],
        "ai": ["AI算力", "服务器", "光模块", "数据中心", "人工智能应用"],
        "consumer_electronics": ["手机产业链", "面板", "声学", "精密制造"],
        "software": ["软件服务", "工业软件", "网络安全", "云计算"]
    },
    "advanced_manufacturing": {
        "robot": ["人形机器人", "工业机器人", "机器视觉", "自动化设备"],
        "equipment": ["通用设备", "专用设备", "高端装备"],
        "new_material": ["金属材料", "复合材料", "先进材料"]
    },
    "energy": {
        "new_energy": ["光伏", "风电", "储能", "新能源车"],
        "traditional_energy": ["煤炭", "石油石化", "天然气"],
        "power": ["电网设备", "电力运营"]
    },
    "automobile": {
        "vehicle": ["整车", "新能源汽车"],
        "parts": ["汽车零部件", "智能驾驶", "汽车电子"]
    },
    "healthcare": {
        "medicine": ["创新药", "仿制药", "中药"],
        "medical_device": ["医疗器械", "医疗服务"]
    },
    "consumer": {
        "food": ["食品饮料", "农业"],
        "retail": ["零售", "消费服务"],
        "home": ["家居", "家电"]
    },
    "finance": {
        "bank": ["银行"],
        "insurance": ["保险"],
        "broker": ["证券"],
        "real_estate": ["房地产" ]
    },
    "infrastructure": {
        "construction": ["建筑工程", "基建"],
        "transport": ["交通运输", "物流"],
        "communication": ["通信基础设施"]
    },
    "military": {
        "defense": ["航空航天", "军工电子", "船舶制造"]
    }
}


def get_all_industries():
    result = []
    for category in INDUSTRY_UNIVERSE.values():
        for items in category.values():
            result.extend(items)
    return result


def find_theme(keyword):
    matches = []
    for category in INDUSTRY_UNIVERSE.values():
        for theme, tags in category.items():
            if keyword in tags:
                matches.append(theme)
    return matches
