from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from likes.models import Like
from tweets.constants import TWEET_PHOTO_STATUS_CHOICES, TweetPhotoStatus
from utils.time_helpers import utc_now


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'), )
        ordering = ('user', '-created_at')

    def __str__(self):
        return f'{self.user} says {self.content} at {self.created_at}'

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        from accounts.services import UserService
        return UserService.get_user_through_cache(self.user_id)


class TweetPhoto(models.Model):
    # Define foreign key to Tweet
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # Who posted this photo. Although we can get this information from tweet,
    # but redundancy is good for performance imporvement and data integrity
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # Photo file
    file = models.FileField()
    order = models.IntegerField(default=0)

    # Photo status
    # using integer field to make it easier for future updates
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # Soft delete for photos
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'
