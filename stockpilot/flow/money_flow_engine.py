"""StockPilot money flow engine
Tracks capital activity and abnormal volume.
"""

class MoneyFlowEngine:
    def analyze(self, bar):
        volume_ratio = bar.get('volume_ratio', 1)
        amount_change = bar.get('amount_change', 0)
        score = 0
        if volume_ratio > 1.5:
            score += 50
        if amount_change > 0:
            score += 50
        return {
            'money_score': score,
            'signal': 'active' if score >= 60 else 'normal'
        }
