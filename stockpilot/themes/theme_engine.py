"""StockPilot theme engine.

Initial theme classification layer for market sectors.
"""

DEFAULT_THEMES = {
    "AI算力": ["CPO", "光模块", "服务器", "液冷", "PCB"],
    "存储芯片": ["存储", "HBM", "DRAM", "NAND"],
    "半导体国产替代": ["光刻胶", "设备", "材料", "封测"],
    "机器人": ["减速器", "伺服", "机器视觉"],
}


class ThemeEngine:
    def __init__(self, themes=None):
        self.themes = themes or DEFAULT_THEMES

    def classify(self, stock_tags):
        result = []
        for theme, keywords in self.themes.items():
            for tag in stock_tags:
                if tag in keywords:
                    result.append(theme)
                    break
        return result

    def list_themes(self):
        return list(self.themes.keys())
