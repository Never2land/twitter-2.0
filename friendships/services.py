from friendships.models import Friendship


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
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()
