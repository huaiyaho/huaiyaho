"""
StockPilot V1.9.8
Event -> Industry -> Stock beneficiary mapping engine.

The first version provides a rule based framework. Later versions can replace
rules with learned mappings from historical events.
"""


class BeneficiaryMapper:
    def __init__(self):
        self.rules = {
            "ai_server_demand": {
                "industries": ["server", "optical_module", "pcb", "liquid_cooling"],
                "levels": ["A", "A", "B", "B"]
            },
            "memory_cycle_up": {
                "industries": ["memory", "semiconductor_equipment", "chip_test"],
                "levels": ["A", "B", "B"]
            },
            "commodity_price_up": {
                "industries": ["resource", "materials", "equipment"],
                "levels": ["A", "B", "C"]
            },
            "rate_cut": {
                "industries": ["brokerage", "growth", "consumer"],
                "levels": ["A", "B", "B"]
            }
        }

    def map_event(self, event):
        rule = self.rules.get(event)
        if not rule:
            return {
                "event": event,
                "beneficiaries": []
            }

        return {
            "event": event,
            "beneficiaries": [
                {
                    "industry": industry,
                    "grade": grade
                }
                for industry, grade in zip(rule["industries"], rule["levels"])
            ]
        }
