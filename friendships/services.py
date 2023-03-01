from django.conf import settings
from django.core.cache import caches

from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # get all friendships where to_user=user
        # select * from friendships where to_user_id = user.id
        # This way is not prefered because it will query the database N times
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # This way is also not perfered because selct_related will result
        # in table join operation, it joins the table friendships and users
        # by from_user. Which is really slow.
        # friendships = Friendship.objects.filter(
        #     to_user=user,
        # ).select_related('from_user')
        # return [Friendship.from_user for Friendship in friendships]

        # This way is prefered because it will query the database only once
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = set(
            {friendship.to_user_id for friendship in friendships})
        cache.set(key, user_id_set)
        return user_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)
