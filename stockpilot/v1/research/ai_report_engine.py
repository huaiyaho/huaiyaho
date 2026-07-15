"""StockPilot AI research report generator v1.5.1"""


def generate_report(stock, industry, scores, risks):
    return {
        "stock": stock,
        "industry_position": industry.get("position", "unknown"),
        "theme": industry.get("theme", []),
        "logic": industry.get("logic", []),
        "technical_score": scores.get("technical", 0),
        "industry_score": scores.get("industry", 0),
        "risk_level": risks.get("level", "unknown"),
        "summary": _summary(stock, scores, risks),
    }


def _summary(stock, scores, risks):
    total = scores.get("total", 0)
    risk = risks.get("level", "unknown")

    if total >= 85 and risk != "high":
        action = "重点关注"
    elif total >= 70:
        action = "观察等待"
    else:
        action = "暂不关注"

    return {
        "action": action,
        "score": total,
        "risk": risk,
    }
