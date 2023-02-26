from django.test import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def tests_hours_to_now(self):
        user = User.objects.create_user(username='user1')
        tweet = Tweet.objects.create(user=user, content='test')
        self.assertEqual(tweet.hours_to_now, 0)
        tweet.created_at = utc_now() - timedelta(hours=1)
        self.assertEqual(tweet.hours_to_now, 1)
        tweet.created_at = utc_now() - timedelta(hours=2)
        self.assertEqual(tweet.hours_to_now, 2)

        dandan = User.objects.create_user(username='dandan')
        tweet = Tweet.objects.create(user=dandan, content='wo yao qu guge')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)      
