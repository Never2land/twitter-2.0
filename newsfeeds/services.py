from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed

class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        # It's not allow to use for loop and query together
        # since it would result in slow query
        # for follower in FriendshipService.get_followers(tweet.user):
        #     newsfeed = NewsFeed.objects.create(
        #         user=follower,
        #         tweet=tweet,
        #     )

        # Corret way is to use bulk_create, it will combine all insert into one query
        # and it will be much faster
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
        