from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase
from utils.paginations import EndlessPagination

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEET_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
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
        self.assertEqual(response.data['results'], [])

        # List tweet from self
        self.user1_client.post(POST_TWEET_URL, {'content': 'Hello World!'})
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 1)

        # List tweet from following
        self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        response = self.user2_client.post(
            POST_TWEET_URL, {'content': 'Hello World!'})
        expected_tweet_id = response.data['id']
        response = self.user1_client.get(NEWSFEEDS_URL)
        posted_tweet_id = response.data['results'][0]['tweet']['id']
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(posted_tweet_id, expected_tweet_id)

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        followed_user = self.create_user('followed_user')
        newsfeeds = []
        for _ in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            newsfeed = self.create_newsfeed(self.user1, tweet)
            newsfeeds.append(newsfeed)

        newsfeeds = newsfeeds[::-1]

        # Pull the first page
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(response.data['results'][1]['id'], newsfeeds[1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'], newsfeeds[page_size - 1].id)

        # Pull the second page
        response = self.user1_client.get(
            NEWSFEEDS_URL,
            {'created_at__lt': newsfeeds[page_size - 1].created_at, },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results']
                         [0]['id'], newsfeeds[page_size].id)
        self.assertEqual(response.data['results']
                         [1]['id'], newsfeeds[page_size + 1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'], newsfeeds[2 * page_size - 1].id)

        # Pull the lastet tweets
        response = self.user1_client.get(
            NEWSFEEDS_URL, {'created_at__gt': newsfeeds[0].created_at, })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        new_tweet = self.create_tweet(followed_user, 'new tweet')
        new_newsfeed = self.create_newsfeed(self.user1, new_tweet)
        response = self.user1_client.get(
            NEWSFEEDS_URL, {'created_at__gt': newsfeeds[0].created_at, })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed.id)

    def test_user_cache(self):
        profile = self.user2.profile
        profile.nickname = 'new nickname'
        profile.save()

        self.assertEqual(self.user1.username, 'user1')
        self.create_newsfeed(self.user2, self.create_tweet(self.user1))
        self.create_newsfeed(self.user2, self.create_tweet(self.user2))

        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['tweet']['user']['username'], 'user2')
        self.assertEqual(results[0]['tweet']['user']
                         ['nickname'], 'new nickname')
        self.assertEqual(results[1]['tweet']['user']['username'], 'user1')

        self.user1.username = 'new user1 name'
        self.user1.save()
        profile.nickname = 'new user2 nickname'
        profile.save()

        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['tweet']['user']['username'], 'user2')
        self.assertEqual(results[0]['tweet']['user']
                         ['nickname'], 'new user2 nickname')
        self.assertEqual(results[1]['tweet']['user']
                         ['username'], 'new user1 name')

    def test_tweet_cache(self):
        tweet = self.create_tweet(self.user1, 'new tweet')
        self.create_newsfeed(self.user2, tweet)

        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['tweet']['user']['username'], 'user1')
        self.assertEqual(results[0]['tweet']['content'], 'new tweet')

        # Update username
        self.user1.username = 'new user1 name'
        self.user1.save()
        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']
                         ['username'], 'new user1 name')

        # Update tweet content
        tweet.content = 'new tweet content'
        tweet.save()
        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['tweet']['content'], 'new tweet content')
