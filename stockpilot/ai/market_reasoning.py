"""AI reasoning interface for StockPilot reports."""

class MarketReasoning:
    def summarize(self, data):
        return {
            'market': data.get('market_state'),
            'themes': data.get('hot_themes', []),
            'leaders': data.get('leaders', []),
            'risks': data.get('risks', [])
        }
