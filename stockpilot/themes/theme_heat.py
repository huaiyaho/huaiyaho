"""StockPilot theme heat engine v0.3.1"""


class ThemeHeatEngine:
    """
    Calculate theme popularity from market statistics.
    
    Factors:
    - price strength
    - active stock ratio
    - turnover change
    - leading stock strength
    - limit-up activity
    """

    def calculate(self, theme_data):
        score = 0
        score += theme_data.get("change_score", 0) * 0.30
        score += theme_data.get("breadth_score", 0) * 0.20
        score += theme_data.get("volume_score", 0) * 0.20
        score += theme_data.get("leader_score", 0) * 0.20
        score += theme_data.get("limit_score", 0) * 0.10

        return round(score, 2)

    def rank(self, themes):
        for theme in themes:
            theme["heat"] = self.calculate(theme)
        return sorted(themes, key=lambda x: x["heat"], reverse=True)
