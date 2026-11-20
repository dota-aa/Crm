from django.contrib.auth.models import BaseUserManager
from django.db.models import QuerySet


class CustomUserManager(BaseUserManager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeleteQuerySet(model=self.model, using=self._db).exclude(is_deleted=True)
        return SoftDeleteQuerySet(model=self.model, using=self._db)

    def create_user(self, first_name, last_name, email, password):
        if not first_name:
            raise ValueError("User must have a first_name")

        if not last_name:
            raise ValueError("User must have a last_name")

        if not email:
            raise ValueError("User must have an email")

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        user.set_password(password)

        # Todo: delete is_active after handling email confirmation
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, password):
        user = self.create_user(first_name, last_name, email, password)
        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        """Delete method to manage how query sets will be deleted"""
        return super().update(is_deleted=True)

    def recover(self):
        """Recover the soft deleted user"""
        return super().update(is_deleted=False)

    def hard_delete(self):
        """Hard Delete method to manage how query sets will be deleted permanently"""
        return super().delete()
