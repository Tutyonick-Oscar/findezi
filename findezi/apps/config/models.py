import auto_prefetch
from django.db import models
from django.utils.translation import gettext_lazy as _

from findezi.apps.core.models import BaseModel


class Country(BaseModel):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return f"{self.name} : {self.code}"

    class Meta(BaseModel.Meta):
        verbose_name = _("country")
        verbose_name_plural = _("countries")


class Currency(BaseModel):

    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, unique=True)
    symbol = models.CharField(max_length=5, blank=True, null=True)
    country = auto_prefetch.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="currencies"
    )

    def __str__(self):
        return f"{self.code} ({self.symbol})"

    class Meta(BaseModel.Meta):
        verbose_name = _("currency")
        verbose_name_plural = _("currencies")


class DollarRate(BaseModel):
    rate = models.DecimalField(decimal_places=3, max_digits=16)
    currency = auto_prefetch.OneToOneField(Currency, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.currency.name}"

    class Meta(BaseModel.Meta):
        verbose_name = _("Dollar Rate")
        verbose_name_plural = _("Dollar Rates")
