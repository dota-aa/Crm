from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import CustomUserManager


nb = dict(null=True, blank=True)


class CustomPermission(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(max_length=225)

    class Meta:
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self) -> str:
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    description = models.TextField(max_length=225, **nb)
    permissions = models.ManyToManyField(CustomPermission, related_name='roles')

    class Meta:
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self) -> str:
        return self.name

    def get_permissions(self) -> list:
        """Get all permissions of a role"""
        permissions = []
        for permission in self.permissions.all():
            permissions.append(permission.name)

        return permissions


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateTimeField(**nb)

    roles= models.ManyToManyField(Role, related_name='users', **nb)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Managers
    objects = CustomUserManager(alive_only=False)
    filtered_objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = 'Crm User'
        verbose_name_plural = 'Crm Users'
        ordering = ("last_name", "first_name")
        unique_together = [['first_name', 'last_name']]

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @property
    def is_staff(self):
        return self.is_admin

    def delete(self, *args, **kwargs):
        """
        This method only works for a single object.

        If you want to delete a queryset of objects
        using .delete on them will permanently delete them.
        To solve this problem we need to override the default QuerySet of manager
        to manage delete and hard_delete method for query sets.

        """
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

    def recover(self):
        self.is_deleted = False
        self.save(update_fields=['is_deleted', 'updated_at'])
        
    def hard_delete(self):
        """
        This method only works for a single object.
        """
        super().delete()

    def has_permission(self, permission) -> bool:
        permissions = set()
        for role in self.roles.prefetch_related('permissions').all():
            permissions.update(role.get_permissions())

        return permission in permissions
