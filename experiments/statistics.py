"""Descriptive statistics derived only from recorded nanosecond durations."""

from statistics import fmean, median, stdev


def _percentile(sorted_values: list[int], fraction: float) -> float:
    position = (len(sorted_values) - 1) * fraction
    low = int(position)
    high = min(low + 1, len(sorted_values) - 1)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (position - low)


def describe_ns(values: list[int]) -> dict[str, int | float]:
    """Return sample statistics in milliseconds; keep raw values in CSV as ns."""
    if not values or any(type(value) is not int or value <= 0 for value in values):
        raise ValueError("Durations must be positive integer nanoseconds.")
    ordered = sorted(values)
    to_ms = lambda value: value / 1_000_000
    return {
        "count": len(ordered),
        "mean_ms": to_ms(fmean(ordered)),
        "median_ms": to_ms(median(ordered)),
        "std_ms": to_ms(stdev(ordered)) if len(ordered) > 1 else 0.0,
        "min_ms": to_ms(ordered[0]),
        "max_ms": to_ms(ordered[-1]),
        "p25_ms": to_ms(_percentile(ordered, 0.25)),
        "p75_ms": to_ms(_percentile(ordered, 0.75)),
    }
