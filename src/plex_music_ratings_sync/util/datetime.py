def format_time(time_delta):
    """
    Format a timedelta into a human readable string.

    Args:
        time_delta: A datetime.timedelta object to format

    Returns:
        str: Formatted time string with appropriate units

    Examples:
        >>> from datetime import timedelta
        >>> format_time(timedelta(hours=1, minutes=30, seconds=45))
        '1h 30m 45s'
        >>> format_time(timedelta(minutes=2, seconds=30))
        '2m 30s'
        >>> format_time(timedelta(seconds=5, milliseconds=123))
        '5.123s'
        >>> format_time(timedelta(milliseconds=500))
        '500ms'
    """
    total_seconds = int(time_delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int(time_delta.microseconds / 1000)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    elif seconds > 0:
        return f"{seconds}.{milliseconds:03d}s"
    else:
        return f"{milliseconds}ms"
