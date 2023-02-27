from testing.testcases import TestCase
from rest_framework.test import APIClient


LIKES_BASE_URL = '/api/likes/'
LIKES_CANCEL_URL = '/api/likes/cancel/'
COMMENTS_LIST_API = '/api/comments/'
TWEETS_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEEDS_LIST_API = '/api/newsfeeds/'


class LikeApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    # def test_tweet_likes(self):
    #     tweet = self.create_tweet(self.user1)
    #     data = {'content_type': 'tweet', 'object_id': tweet.id}

    #     # Must login
    #     response = self.anonymous_client.post(LIKES_BASE_URL, data)
    #     self.assertEqual(response.status_code, 403)

    #     # Get is not allowed
    #     response = self.user1_client.get(LIKES_BASE_URL, data)
    #     self.assertEqual(response.status_code, 405)

    #     # Wrong content_type
    #     response = self.user1_client.post(LIKES_BASE_URL, {
    #         'content_type': 'wrong type',
    #         'object_id': tweet.id,
    #     })
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual('content_type' in response.data['errors'], True)

    #     # Wrong object_id
    #     response = self.user1_client.post(LIKES_BASE_URL, {
    #         'content_type': 'tweet',
    #         'object_id': -1,
    #     })
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual('object_id' in response.data['errors'], True)

    #     # Success like
    #     response = self.user1_client.post(LIKES_BASE_URL, data)
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(tweet.like_set.count(), 1)

    #     # Duplicate likes
    #     self.user1_client.post(LIKES_BASE_URL, data)
    #     self.assertEqual(tweet.like_set.count(), 1)
    #     self.user2_client.post(LIKES_BASE_URL, data)
    #     self.assertEqual(tweet.like_set.count(), 2)

    # def test_comment_likes(self):
    #     tweet = self.create_tweet(self.user1)
    #     comment = self.create_comment(self.user1, tweet)
    #     data = {'content_type': 'comment', 'object_id': comment.id}

    #     # Must login
    #     response = self.anonymous_client.post(LIKES_BASE_URL, data)
    #     self.assertEqual(response.status_code, 403)

    #     # Get is not allowed
    #     response = self.user1_client.get(LIKES_BASE_URL, data)
    #     self.assertEqual(response.status_code, 405)

    #     # Wrong content_type
    #     response = self.user1_client.post(LIKES_BASE_URL, {
    #         'content_type': 'wrong type',
    #         'object_id': comment.id,
    #     })
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual('content_type' in response.data['errors'], True)

    #     # Wrong object_id
    #     response = self.user1_client.post(LIKES_BASE_URL, {
    #         'content_type': 'comment',
    #         'object_id': -1,
    #     })
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual('object_id' in response.data['errors'], True)

    #     # Success like
    #     response = self.user1_client.post(LIKES_BASE_URL, data)
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(comment.like_set.count(), 1)

    #     # Duplicate likes
    #     self.user1_client.post(LIKES_BASE_URL, data)
    #     self.assertEqual(comment.like_set.count(), 1)
    #     self.user2_client.post(LIKES_BASE_URL, data)
    #     self.assertEqual(comment.like_set.count(), 2)

    # def test_cancel(self):
    #     tweet = self.create_tweet(self.user1)
    #     comment = self.create_comment(self.user2, tweet)
    #     like_comment_data = {
    #         'content_type': 'comment',
    #         'object_id': comment.id,
    #     }
    #     like_tweet_data = {'content_type': 'tweet', 'object_id': tweet.id}
    #     self.user1_client.post(LIKES_BASE_URL, like_comment_data)
    #     self.user2_client.post(LIKES_BASE_URL, like_tweet_data)

    #     # Must login
    #     response = self.anonymous_client.post(
    #         LIKES_CANCEL_URL, like_comment_data)
    #     self.assertEqual(response.status_code, 403)

    #     # Must use `post`
    #     response = self.user1_client.get(LIKES_CANCEL_URL, like_comment_data)
    #     self.assertEqual(response.status_code, 405)

    #     # Wrong content_type
    #     response = self.user1_client.post(LIKES_CANCEL_URL, {
    #         'content_type': 'wrong type',
    #         'object_id': comment.id,
    #     })
    #     self.assertEqual(response.status_code, 400)

    #     # Wrong object_id
    #     response = self.user1_client.post(LIKES_CANCEL_URL, {
    #         'content_type': 'comment',
    #         'object_id': -1,
    #     })
    #     self.assertEqual(response.status_code, 400)

    #     # User2 has not liked the comment before
    #     response = self.user2_client.post(LIKES_CANCEL_URL, like_comment_data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['deleted'], 0)
    #     self.assertEqual(tweet.like_set.count(), 1)
    #     self.assertEqual(comment.like_set.count(), 1)

    #     # Successful cancel
    #     response = self.user1_client.post(LIKES_CANCEL_URL, like_comment_data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['deleted'], 1)
    #     self.assertEqual(tweet.like_set.count(), 1)
    #     self.assertEqual(comment.like_set.count(), 0)

    #     # User1 has not liked the tweet before
    #     response = self.user1_client.post(LIKES_CANCEL_URL, like_tweet_data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['deleted'], 0)
    #     self.assertEqual(tweet.like_set.count(), 1)
    #     self.assertEqual(comment.like_set.count(), 0)

    #     # Successful cancel
    #     response = self.user2_client.post(LIKES_CANCEL_URL, like_tweet_data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['deleted'], 1)
    #     self.assertEqual(tweet.like_set.count(), 0)
    #     self.assertEqual(comment.like_set.count(), 0)

    def test_likes_in_comments_api(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)

        # Test anonymous user
        response = self.anonymous_client.get(
            COMMENTS_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)

        # Test comments list api
        response = self.user2_client.get(
            COMMENTS_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.create_like(self.user2, comment)
        response = self.user2_client.get(
            COMMENTS_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # Test tweet detail api
        self.create_like(self.user1, comment)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 2)

    def test_likes_in_tweets_api(self):
        tweet = self.create_tweet(self.user1)

        # Test anonymous user
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], False)
        self.assertEqual(response.data['likes_count'], 0)

        # Test tweet detail api
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], False)
        self.assertEqual(response.data['likes_count'], 0)
        self.create_like(self.user2, tweet)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], True)
        self.assertEqual(response.data['likes_count'], 1)

        # Test tweet list api
        self.create_like(self.user1, tweet)
        response = self.user2_client.get(
            TWEETS_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tweets'][0]['has_liked'], True)
        self.assertEqual(response.data['tweets'][0]['likes_count'], 2)

        # Test newsfeeds list api
        self.create_like(self.user1, tweet)
        self.create_newsfeed(self.user2, tweet)
        response = self.user2_client.get(NEWSFEEDS_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['newsfeeds']
                         [0]['tweet']['has_liked'], True)
        self.assertEqual(response.data['newsfeeds']
                         [0]['tweet']['likes_count'], 2)

        # Test likes detail api
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['likes_count'], 2)
        self.assertEqual(response.data['likes']
                         [0]['user']['id'], self.user1.id)
        self.assertEqual(response.data['likes']
                         [1]['user']['id'], self.user2.id)
