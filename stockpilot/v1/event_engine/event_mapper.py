"""
StockPilot V1.9.6 Event Driven Industry Mapper

Map external events to industry chains and candidate stocks.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class EventImpact:
    event: str
    industry: str
    impact_level: str
    logic: str


class EventMapper:
    def __init__(self):
        self.rules = {
            "commodity_up": ["resource", "materials"],
            "ai_demand_up": ["semiconductor", "computing", "communication"],
            "rate_cut": ["finance", "growth", "consumption"],
        }

    def analyze(self, event_type: str) -> List[EventImpact]:
        industries = self.rules.get(event_type, [])
        return [
            EventImpact(
                event=event_type,
                industry=i,
                impact_level="watch",
                logic="event to industry transmission"
            )
            for i in industries
        ]
