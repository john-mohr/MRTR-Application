from datetime import date, timedelta

# Helper function for calculated transactions
def prorate(rent, e_date):
    return (date(e_date.year, e_date.month + 1, 1) - e_date).days * (rent / 30)
