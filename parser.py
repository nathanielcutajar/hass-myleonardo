from datetime import date, datetime


def as_float(value):
    """Return numeric sensor values while treating null/bad fields as unknown."""
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_date(value):
    """Return a date for API date buckets such as energy Stime."""
    if not isinstance(value, str):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def as_datetime(value):
    """Return a timezone-aware datetime for API timestamp fields."""
    if not isinstance(value, str):
        return None

    normalized = value.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        parsed_date = as_date(value)

        if parsed_date is None:
            return None

        parsed = datetime.combine(parsed_date, datetime.min.time())

    if parsed.tzinfo is None:
        parsed = parsed.astimezone()

    return parsed


def get_realtime_value(data, key):
    """Read a field from realtime responses, where data is a dictionary."""
    payload = (data or {}).get("data", {})

    if not isinstance(payload, dict):
        return None

    return payload.get(key)


def _bucket_sort_value(bucket):
    timestamp = bucket.get("Stime")

    if not isinstance(timestamp, str):
        return ""

    return timestamp


def get_latest_list_value(data, key):
    """Read a field from list responses, using the newest returned bucket."""
    payload = (data or {}).get("data", [])

    if not isinstance(payload, list) or not payload:
        return None

    buckets = [
        item
        for item in payload
        if isinstance(item, dict)
    ]

    if not buckets:
        return None

    latest = max(buckets, key=_bucket_sort_value)

    return latest.get(key)


def _transform_number(value, value_type):
    if value_type == "positive":
        return max(value, 0)

    if value_type == "negative_abs":
        return abs(min(value, 0))

    return value


def get_sensor_value(data, key, source, scale=1, value_type="number"):
    """Convert an API field into the final Home Assistant native value."""
    if source in ("realtime", "modbus"):
        value = get_realtime_value(data, key)
    else:
        value = get_latest_list_value(data, key)

    if value_type == "date":
        return as_date(value)

    if value_type == "timestamp":
        return as_datetime(value)

    number = as_float(value)

    if number is None:
        return None

    return round(_transform_number(number, value_type) * scale, 3)


def get_binary_sensor_value(
    data,
    key,
    source,
    value_type,
    threshold=0,
):
    """Convert a signed power field into an on/off status value."""
    if source in ("realtime", "modbus"):
        value = get_realtime_value(data, key)
    else:
        value = get_latest_list_value(data, key)

    number = as_float(value)

    if number is None:
        return None

    if value_type == "above":
        return number > threshold

    if value_type == "below":
        return number < -threshold

    return None
