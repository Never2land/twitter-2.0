from rest_framework import status
from rest_framework.test import APIClient

from friendships.models import Friendship
from newsfeeds.models import NewsFeed
from testing.testcases import TestCase

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEET_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_list(self):
        # Need to login to list newsfeeds
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Need to use GET to list newsfeeds
        response = self.user1_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        # No newsfeeds yet
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.data['newsfeeds'], [])

        # List tweet from self
        self.user1_client.post(POST_TWEET_URL, {'content': 'Hello World!'})
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)

        # List tweet from following
        self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        response = self.user2_client.post(
            POST_TWEET_URL, {'content': 'Hello World!'})
        expected_tweet_id = response.data['id']
        response = self.user1_client.get(NEWSFEEDS_URL)
        posted_tweet_id = response.data['newsfeeds'][0]['tweet']['id']
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(posted_tweet_id, expected_tweet_id)
