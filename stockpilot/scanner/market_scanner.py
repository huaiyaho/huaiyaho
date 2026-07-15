"""StockPilot market scanner.

Scan all available stocks, calculate scores and rank candidates.
"""


class MarketScanner:
    def __init__(self, database, scorer):
        self.database = database
        self.scorer = scorer

    def scan(self, stocks):
        results = []
        for stock in stocks:
            score = self.scorer.score(stock)
            results.append({
                "code": stock.get("code"),
                "name": stock.get("name"),
                "score": score
            })

        return sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )
