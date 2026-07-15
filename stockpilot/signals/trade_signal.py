class TradeSignal:
    def generate(self, stock):
        score = stock.get('score', 0)
        if score >= 85:
            return 'strong_watch'
        if score >= 70:
            return 'watch'
        return 'avoid'
