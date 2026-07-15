"""Market emotion cycle analyzer."""

class EmotionCycle:
    def analyze(self, market):
        up = market.get('up_count', 0)
        limit = market.get('limit_up', 0)
        down = market.get('down_count', 0)

        if limit > 80 and up > down * 2:
            return 'main_rise'
        if up > down:
            return 'repair'
        if down > up * 2:
            return 'retreat'
        return 'balance'
