"""
StockPilot V1.9.9
Company Beneficiary Mapper

Maps industry/event impact into specific companies.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class CompanyBenefit:
    code: str
    name: str
    industry: str
    benefit_level: str
    relevance: float
    elasticity: float

    @property
    def score(self):
        return round(self.relevance * 0.6 + self.elasticity * 0.4, 2)


class CompanyMapper:
    def __init__(self):
        self.database = []

    def add_company(self, company: CompanyBenefit):
        self.database.append(company)

    def map_event(self, industry, limit=10):
        result = [
            c for c in self.database
            if c.industry == industry
        ]
        return sorted(
            result,
            key=lambda x: x.score,
            reverse=True
        )[:limit]


if __name__ == '__main__':
    mapper = CompanyMapper()
    mapper.add_company(
        CompanyBenefit(
            code='000000',
            name='example',
            industry='AI',
            benefit_level='A',
            relevance=90,
            elasticity=85
        )
    )
