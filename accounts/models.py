from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # OneToOne filed will create a unique index make sure no multiple UserProfile
    # linked to the same user
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # Django has a ImageField, but try not to use it in case it causing other problems
    # Use FileFiled can achive same goal cause we save it as file anyway and use
    # Url to access the file
    avatar = models.FileField(null=True)
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} {self.nickname}'


def get_profile(user):
    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile, _ = UserProfile.objects.get_or_create(user=user)
    setattr(user, '_cached_user_profile', profile)
    return profile


# 给 User Model 增加了一个 profile 的property 方法方便访问
User.profile = property(get_profile)
