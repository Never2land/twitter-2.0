from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from testing.testcases import TestCase
from tweets.models import Tweet, TweetPhoto
from utils.paginations import EndlessPagination

# Caution: has to add '/' at end to avoid 301 redirect
TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'
TWEET_RETRIEVE_API = '/api/tweets/{}/'


class TweetApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]

    def test_list_api(self):
        # User_id required
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # Normal request
        response = self.anonymous_client.get(
            TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        response = self.anonymous_client.get(
            TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['results']), 2)
        # Check order
        self.assertEqual(response.data['results'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['results'][1]['id'], self.tweets2[0].id)

    def test_retrieve_api(self):
        # tweet with id=-1 does not exist
        response = self.anonymous_client.get(TWEET_RETRIEVE_API.format(-1))
        self.assertEqual(response.status_code, 404)

        # Retrive tweet with comments
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(self.user1, tweet, 'comment1')
        self.create_comment(self.user2, tweet, 'comment2')
        self.create_comment(
            self.user2, self.create_tweet(self.user2), 'comment3')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)

    def test_create_api(self):
        # Not logged in
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403)

        # Content required
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)
        # Content cannot be empty
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)
        # Content cannot be too long
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': '0' * 255
        })
        self.assertEqual(response.status_code, 400)

        # Normal request
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my first tweet!'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_create_with_files(self):
        # Upload empty file list
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'a selfie',
            'files': [],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # Upload one file
        file = SimpleUploadedFile(
            name='selfie.jpg',
            content=str.encode('fake image content'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'a selfie',
            'files': [file],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 1)

        # Upload multiple files
        file1 = SimpleUploadedFile(
            name='selfie1.jpg',
            content=str.encode('fake image content'),
            content_type='image/jpeg',
        )
        file2 = SimpleUploadedFile(
            name='selfie2.jpg',
            content=str.encode('fake image content'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': '2 selfies',
            'files': [file1, file2],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 3)
        retrive_url = TWEET_RETRIEVE_API.format(response.data['id'])
        response = self.user1_client.get(retrive_url)
        self.assertEqual(len(response.data['photo_urls']), 2)
        self.assertEqual('selfie1' in response.data['photo_urls'][0], True)
        self.assertEqual('selfie2' in response.data['photo_urls'][1], True)

        # Upload too many files
        files = []
        for i in range(10):
            files.append(SimpleUploadedFile(
                name=f'selfie{i}.jpg',
                content=str.encode('fake image content'),
                content_type='image/jpeg',
            ))
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': '10 selfies',
            'files': files,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TweetPhoto.objects.count(), 3)

    def test_pagination(self):
        page_size = EndlessPagination.page_size

        # Create 2 * page_size tweets
        for i in range(2 * page_size - len(self.tweets1)):
            self.tweets1.append(self.create_tweet(self.user1, f'tweet{i}'))

        tweets = self.tweets1[::-1]

        # Pull the first page
        response = self.anonymous_client.get(
            TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], tweets[0].id)
        self.assertEqual(response.data['results'][1]['id'], tweets[1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'], tweets[page_size - 1].id)

        # Pull the second page
        response = self.anonymous_client.get(TWEET_LIST_API, {
            'user_id': self.user1.id,
            'created_at__lt': tweets[page_size - 1].created_at,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results']
                         [0]['id'], tweets[page_size].id)
        self.assertEqual(response.data['results']
                         [1]['id'], tweets[page_size + 1].id)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'], tweets[2 * page_size - 1].id)

        # Pull the lastet tweets
        response = self.anonymous_client.get(TWEET_LIST_API, {
            'user_id': self.user1.id,
            'created_at__gt': tweets[0].created_at,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        new_tweet = self.create_tweet(self.user1, 'new tweet')
        response = self.anonymous_client.get(TWEET_LIST_API, {
            'user_id': self.user1.id,
            'created_at__gt': tweets[0].created_at,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_tweet.id)
