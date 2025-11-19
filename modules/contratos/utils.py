from datetime import datetime

def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def parse_int(value):
    try:
        return int(value) if value else None
    except (ValueError, TypeError):
        return None

def parse_float(value):
    try:
        return float(value) if value else None
    except (ValueError, TypeError):
        return None

def parse_bool(value):
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'y', 't')
    return bool(value)