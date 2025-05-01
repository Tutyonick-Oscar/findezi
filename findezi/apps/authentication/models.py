import auto_prefetch

"""_summary_
used for Handling case-insensitive usernames and email with PostgreSQL
"""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.postgres.fields import CICharField, CIEmailField
from django.db import models
from django.utils.translation import gettext_lazy as _

from findezi.apps.core.models import BaseModel

from .managers.accounts import AccountManager


class Role(models.Model):
    class RoleChoices(models.TextChoices):
        SIMPLE_USER = "SU", _("Simple_user")
        CORPORATE = "C", _("Corporate")
        ADMIN = "AD", _("Administrator")

    name = models.CharField(max_length=2, choices=RoleChoices.choices)

    def __str__(self):
        return self.name


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    image = models.ImageField(upload_to="profiles", null=True, blank=True)
    # role = auto_prefetch.ForeignKey(
    #     Role, on_delete=models.PROTECT, related_name="users", blank=True
    # )
    created_by = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = AccountManager()

    class Meta(BaseModel.Meta):

        # require postgresql to work
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(deleted_at=None),
                name="unique_undeleted_user",
            )
        ]
        indexes = [
            models.Index(
                fields=("deleted_at",),
                name="indexing_undeleted_users",
                condition=models.Q(deleted_at=None),
            )
        ]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
        self.username = self.username.lower()


class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blacklisted token from {self.blacklisted_at}"
