from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from utils.memcached_helper import MemchachedHelper


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )
    object_id = models.PositiveIntegerField()
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'), )
        index_together = (('content_type', 'object_id', 'created_at'), )

    def __str__(self):
        return '{} liked {} {} at {}'.format(
            self.user,
            self.content_type,
            self.object_id,
            self.created_at,
        )

    @property
    def cached_user(self):
        from accounts.services import UserService
        return MemchachedHelper.get_object_through_cache(User, self.user_id)
