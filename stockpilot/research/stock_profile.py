"""Generate structured stock research profiles."""


class StockProfile:
    def build(self, stock):
        return {
            "code": stock.get("code"),
            "name": stock.get("name"),
            "themes": stock.get("themes", []),
            "logic": stock.get("logic", []),
            "risks": stock.get("risks", []),
        }
