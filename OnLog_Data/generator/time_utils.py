# generator/time_utils.py

from datetime import datetime, timezone, timedelta
import random

def generate_times(base_time: datetime):
    """
    returns:
      time, gwTime, nsTime, received_at (ISO8601 with ns)
    """

    base = base_time

    # gwTime - time: 0 ~ 수십 µs
    gw_time = base + timedelta(microseconds=random.randint(0, 50))

    # nsTime - gwTime: +2 ~ +6 ms
    ns_time = gw_time + timedelta(milliseconds=random.uniform(2, 6))

    # received_at ≈ time
    received_at = base

    return (
        base.isoformat(),
        gw_time.isoformat(),
        ns_time.isoformat(),
        received_at.isoformat(),
    )

def dr_to_sf(dr: int) -> int:
    # DR 0 → SF12, DR 5 → SF7
    return 12 - dr
