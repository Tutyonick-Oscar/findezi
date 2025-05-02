from django.contrib import admin

from .models import Country, Currency, DollarRate


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "code"]


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "country__name"]


@admin.register(DollarRate)
class DollarRateAdmin(admin.ModelAdmin):
    list_display = ["rate", "currency__name"]
