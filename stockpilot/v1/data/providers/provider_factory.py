"""Provider factory."""

from .mock_provider import get_sample_bars


def get_provider(name="mock"):
    if name == "mock":
        return get_sample_bars
    raise ValueError(f"Unsupported provider: {name}")
