"""Calendar-free ISS timekeeping primitives."""

from datetime import datetime, timezone
import time


ISS_EPOCH = datetime(2000, 1, 1, tzinfo=timezone.utc)
ISS_EPOCH_LABEL = "2000-01-01 00:00:00.000000000 TAI"
ISS_REFERENCE_FRAME = "solar-system-barycentric"
ISS_SCALE_NAME = "Interplanetary Stardate Syncrometer Scale"
ISS_SCALE_DESIGNATION = "ISS"
NANOSECONDS_PER_SECOND = 1_000_000_000
AVERAGE_YEAR_NS = 31_556_952_000_000_000


def _as_utc(dt=None):
    now = dt or datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def get_iss_time_ns(dt=None):
    """Return continuous nanoseconds from the immutable ISS epoch."""
    if dt is None:
        return time.time_ns() - int(ISS_EPOCH.timestamp() * NANOSECONDS_PER_SECOND)

    now = _as_utc(dt)
    delta = now - ISS_EPOCH
    return (delta.days * 86_400 * NANOSECONDS_PER_SECOND
            + delta.seconds * NANOSECONDS_PER_SECOND
            + delta.microseconds * 1_000)


def get_stardate(dt=None):
    """Return a display-only stardate derived from ``iss_time_ns``."""
    return round(get_iss_time_ns(dt) / NANOSECONDS_PER_SECOND, 9)


def format_iss_time(iss_time_ns=None, precision='milliseconds', mission_elapsed_ns=None):
    """Format the authoritative ISS nanosecond value for human display.

    The display uses average-year arithmetic only. It does not consult a
    calendar, leap-year table, leap-second table, timezone, or location.
    """
    raw_ns = get_iss_time_ns() if iss_time_ns is None else int(iss_time_ns)
    sign = '-' if raw_ns < 0 else ''
    raw_ns = abs(raw_ns)
    years, remainder_ns = divmod(raw_ns, AVERAGE_YEAR_NS)
    fractional_thousand = (remainder_ns * 1000) // AVERAGE_YEAR_NS

    # Map the continuous fractional year to a 365.25-day display cycle.
    display_day_ns = (remainder_ns * 1461 * 86_400 * NANOSECONDS_PER_SECOND) // (4 * AVERAGE_YEAR_NS)
    display_day_ns %= 86_400 * NANOSECONDS_PER_SECOND
    hours, remainder = divmod(display_day_ns, 3_600 * NANOSECONDS_PER_SECOND)
    minutes, remainder = divmod(remainder, 60 * NANOSECONDS_PER_SECOND)
    seconds, nanoseconds = divmod(remainder, NANOSECONDS_PER_SECOND)

    if precision == 'nanoseconds':
        subsecond = f".{nanoseconds:09d}"
    elif precision == 'seconds':
        subsecond = ''
    else:
        subsecond = f".{nanoseconds // 1_000_000:03d}"

    display = f"{ISS_SCALE_DESIGNATION} {sign}{years:02d}.{fractional_thousand:03d} {hours:02d}:{minutes:02d}:{seconds:02d}{subsecond}"
    if mission_elapsed_ns is not None:
        met_seconds, met_ns = divmod(max(0, int(mission_elapsed_ns)), NANOSECONDS_PER_SECOND)
        met_days, met_seconds = divmod(met_seconds, 86_400)
        met_hours, met_seconds = divmod(met_seconds, 3_600)
        met_minutes, met_seconds = divmod(met_seconds, 60)
        display += f"  |  MET {met_days:03d}/{met_hours:02d}:{met_minutes:02d}:{met_seconds:02d}"
        if precision == 'nanoseconds':
            display += f".{met_ns:09d}"
        elif precision != 'seconds':
            display += f".{met_ns // 1_000_000:03d}"
    return display


def get_julian_date():
    """
    Calculate Julian date from current time
    """
    now = datetime.now(timezone.utc)
    a = (14 - now.month) // 12
    y = now.year + 4800 - a
    m = now.month + 12 * a - 3
    jdn = now.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn + (now.hour - 12) / 24 + now.minute / 1440 + now.second / 86400


def get_market_times():
    """
    Get current market session information
    """
    now = datetime.now(timezone.utc)
    market_sessions = {
        'tokyo': {'open': 0, 'close': 9},  # UTC hours
        'london': {'open': 8, 'close': 17},
        'new_york': {'open': 14, 'close': 21}
    }
    
    current_hour = now.hour
    active_markets = []
    
    for market, times in market_sessions.items():
        if times['open'] <= current_hour < times['close']:
            active_markets.append(market)
    
    return {
        'current_utc': now.isoformat(),
        'active_markets': active_markets,
        'all_sessions': market_sessions
    }


def format_timestamp(dt=None, format_type='iso'):
    """
    Format timestamp in various formats
    """
    dt = _as_utc(dt)
    
    formats = {
        'iso': dt.isoformat(),
        'stardate': f"Stardate {get_stardate(dt):.9f}",
        'julian': f"JD {get_julian_date():.6f}",
        'human': dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    
    return formats.get(format_type, formats['iso'])


def current_timecodes():
    """
    Get all current time representations for anchoring
    Returns the complete set of time values used by the service.
    """
    now = _as_utc()
    iss_time_ns = get_iss_time_ns(now)
    
    return {
        'iss_time_ns': iss_time_ns,
        'scale_name': ISS_SCALE_NAME,
        'scale_designation': ISS_SCALE_DESIGNATION,
        'epoch': ISS_EPOCH_LABEL,
        'reference_frame': ISS_REFERENCE_FRAME,
        'iso_timestamp': now.isoformat(),
        'unix_timestamp_ns': int(now.timestamp() * NANOSECONDS_PER_SECOND),
        'stardate': get_stardate(now),
        'julian_date': get_julian_date(),
        'unix_timestamp': int(now.timestamp()),
        'human_readable': now.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'market_info': get_market_times(),
        'anchor_hash': _generate_time_anchor_hash(now)
    }


def canonical_timestamp(mission_epoch_ns=None, proper_time_ns=None, clock_id='ISS-PRIMARY-ATOMIC-01', source='ISS', _timecodes=None):
    """Build the canonical four-time timestamp envelope."""
    timecodes = _timecodes or current_timecodes()
    mission_elapsed_ns = (
        timecodes['iss_time_ns'] - mission_epoch_ns
        if mission_epoch_ns is not None else None
    )
    return {
        'iss_time_ns': timecodes['iss_time_ns'],
        'scale_name': timecodes['scale_name'],
        'scale_designation': timecodes['scale_designation'],
        'epoch': timecodes['epoch'],
        'reference_frame': timecodes['reference_frame'],
        'clock_id': clock_id,
        'uncertainty_ns': None,
        'proper_time_ns': proper_time_ns,
        'mission_elapsed_ns': mission_elapsed_ns,
        'relativistic_correction_ns': None,
        'source': source,
        'local_display_time': timecodes['iso_timestamp'],
        'epoch_timestamp_ns': timecodes['unix_timestamp_ns'],
        'standard_timestamp': timecodes['iso_timestamp'],
        'julian_timestamp': timecodes['julian_date'],
        'iss_timestamp': format_iss_time(timecodes['iss_time_ns']),
        'stardate': timecodes['stardate'],
        'human_display': format_iss_time(timecodes['iss_time_ns'], precision='milliseconds', mission_elapsed_ns=mission_elapsed_ns),
        'human_display_precise': format_iss_time(timecodes['iss_time_ns'], precision='nanoseconds', mission_elapsed_ns=mission_elapsed_ns),
    }


def _generate_time_anchor_hash(dt):
    """Generate a unique hash for time anchoring"""
    import hashlib
    
    # Combine multiple time representations for unique anchoring
    anchor_string = f"{get_iss_time_ns(dt)}-{get_julian_date()}"
    return hashlib.sha256(anchor_string.encode()).hexdigest()[:16]


def ensure_folder(folder_path: str) -> str:
    """
    Ensure a folder exists, create if it doesn't
    Returns the absolute path to the folder
    """
    import os
    folder_path = os.path.abspath(folder_path)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path
