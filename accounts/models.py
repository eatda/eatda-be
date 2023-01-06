from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models


# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, social_id, email):
        # id 존재 확인
        if not social_id:
            raise ValueError('Users must have social_id')

        user = self.model(
            id=social_id,
            email=email
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, social_id=None, email=None):
        superuser = self.create_user(
            id=social_id,
            email=email,
        )

        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=50, unique=True, null=False, blank=False, primary_key=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['id']

    def __str__(self):
        return self.email
