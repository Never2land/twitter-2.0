from rest_framework.test import APIClient

from friendships.models import Friendship
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        # Create followings and followers for user1
        for i in range(2):
            follower = self.create_user(f'user1_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.user1)
        for i in range(3):
            following = self.create_user(f'user1_following{i}')
            Friendship.objects.create(from_user=self.user1, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.user2.id)

        # need to login to follow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # Need to POST to follow
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 405)

        # Cannot follow yourself
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 400)

        # Normal follow
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 201)

        # Cannot follow twice
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 400)

        # Check data if user2 follows user1
        count = Friendship.objects.count()
        response = self.user2_client.post(FOLLOW_URL.format(self.user1.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.user2.id)

        # need to login to unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # Need to POST to unfollow
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 405)

        # Cannot unfollow yourself
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 400)

        # Normal unfollow
        Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        count = Friendship.objects.count()
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # Unfollow twice will result in 'deleted' to be 0
        count = Friendship.objects.count()
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.user1.id)

        # Need to GET to get followings
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 405)

        # Normal get followings
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)

        # Check if the followings are in correct order
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1 > ts2, True)
        self.assertEqual(response.data['followings']
                         [0]['user']['username'], 'user1_following2')
        self.assertEqual(response.data['followings']
                         [1]['user']['username'], 'user1_following1')
        self.assertEqual(response.data['followings']
                         [2]['user']['username'], 'user1_following0')

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.user1.id)

        # Need to GET to get followers
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 405)

        # Normal get followers
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)

        # Check if the followers are in correct order
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(response.data['followers']
                         [0]['user']['username'], 'user1_follower1')
        self.assertEqual(response.data['followers']
                         [1]['user']['username'], 'user1_follower0')
