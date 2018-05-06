from datetime import timedelta, datetime


def date_range(start_date, end_date, day_step=1):
    """
    'end_date' excluded
    """
    for n in range(0, int((end_date - start_date).days), day_step):
        yield start_date + timedelta(n)


def get_one_month_before(date):
    year = date.year
    month = date.month
    day = date.day
    month -= 1
    if month == 0:
        month = 12
        year -= 1
    return datetime(year, month, day).date()


def get_n_month_before(date, n):
    while n > 0:
        date = get_one_month_before(date)
        n -= 1
    return date