from datetime import datetime


def is_consecutive_dates(start_date, end_date):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    delta = (end_dt - start_dt).days
    return delta == 1
