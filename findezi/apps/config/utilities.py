from decimal import Decimal

from django.apps import apps


def currency_exchange(from_currency, to_currency, amount):
    DollarRate = apps.get_model("config", "DollarRate")
    try:
        from_rate = DollarRate.objects.get(currency=from_currency)
        to_rate = DollarRate.objects.get(currency=to_currency)
    except Exception as e:
        raise ValueError(f"ERROR : {str(e)}")
    # multiple decimal convertion to check
    in_dollar = Decimal(str(amount)) / from_rate.rate
    return in_dollar * to_rate.rate
