import uuid
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models


# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, social_id=None, password=None):
        # social_id 존재 확인
        if not social_id:
            raise ValueError('Users must have social_id')
        # email 존재 확인
        if not email:
            raise ValueError('Users must have email')

        user = self.model(
            social_id=social_id,
            email=email
        )
        # password 존재 한다면
        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, social_id=None, password=None):
        superuser = self.create_user(
            social_id=social_id,
            email=email,
            password=password
        )

        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    class SocialProviderType(models.TextChoices):  # 제공 업체
        KAKAO = 'kakao'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    social_id = models.CharField(max_length=64, unique=True)
    social_provider = models.CharField(max_length=64, choices=SocialProviderType.choices, default=SocialProviderType.KAKAO)
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    password = models.CharField(max_length=128, blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['social_id']

    def __str__(self):
        return self.email


class Group(models.Model):
    code = models.CharField(max_length=10, unique=True)
