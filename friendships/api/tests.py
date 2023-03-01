from rest_framework.test import APIClient

from friendships.models import Friendship
from testing.testcases import TestCase
from utils.paginations import FriendshipPagination

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

    def test_follow(self):
        # Create followings and followers for user1
        for i in range(2):
            follower = self.create_user(f'user1_test_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.user1)
        for i in range(3):
            following = self.create_user(f'user1_test_following{i}')
            Friendship.objects.create(from_user=self.user1, to_user=following)

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
        # Create followings and followers for user1
        for i in range(2):
            follower = self.create_user(f'user1_test_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.user1)
        for i in range(3):
            following = self.create_user(f'user1_test_following{i}')
            Friendship.objects.create(from_user=self.user1, to_user=following)

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
        # Create followings and followers for user1
        for i in range(2):
            follower = self.create_user(f'user1_test_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.user1)
        for i in range(3):
            following = self.create_user(f'user1_test_following{i}')
            Friendship.objects.create(from_user=self.user1, to_user=following)

        url = FOLLOWINGS_URL.format(self.user1.id)

        # Need to GET to get followings
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 405)

        # Normal get followings
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

        # Check if the followings are in correct order
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']
        self.assertEqual(ts0 > ts1 > ts2, True)
        self.assertEqual(response.data['results']
                         [0]['user']['username'], 'user1_test_following2')
        self.assertEqual(response.data['results']
                         [1]['user']['username'], 'user1_test_following1')
        self.assertEqual(response.data['results']
                         [2]['user']['username'], 'user1_test_following0')

    def test_followers(self):
        # Create followings and followers for user1
        for i in range(2):
            follower = self.create_user(f'user1_test_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.user1)
        for i in range(3):
            following = self.create_user(f'user1_test_following{i}')
            Friendship.objects.create(from_user=self.user1, to_user=following)

        url = FOLLOWERS_URL.format(self.user1.id)

        # Need to GET to get followers
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 405)

        # Normal get followers
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

        # Check if the followers are in correct order
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(response.data['results']
                         [0]['user']['username'], 'user1_test_follower1')
        self.assertEqual(response.data['results']
                         [1]['user']['username'], 'user1_test_follower0')

    def test_followers_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size

        # create 2 pages of followers
        for i in range(page_size * 2):
            follower = self.create_user(f'user1_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.user1)
            if follower.id % 2 == 0:
                Friendship.objects.create(
                    from_user=self.user2, to_user=follower)

        url = FOLLOWERS_URL.format(self.user1.id)
        self._test_friendship_pagination(url, max_page_size, page_size)

        # anonymous user hasn't followed anyone
        response = self.anonymous_client.get(url)
        for reuslt in response.data['results']:
            self.assertEqual(reuslt['has_followed'], False)

        # user2 has followed users with even id
        response = self.user2_client.get(url)
        for reuslt in response.data['results']:
            if reuslt['user']['id'] % 2 == 0:
                self.assertEqual(reuslt['has_followed'], True)
            else:
                self.assertEqual(reuslt['has_followed'], False)

    def test_followings_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size

        # create 2 pages of followings
        for i in range(page_size * 2):
            following = self.create_user(f'user1_following{i}')
            Friendship.objects.create(from_user=self.user1, to_user=following)
            if following.id % 2 == 0:
                Friendship.objects.create(
                    from_user=self.user2, to_user=following)

        url = FOLLOWINGS_URL.format(self.user1.id)
        self._test_friendship_pagination(url, max_page_size, page_size)

        # anonymous user hasn't followed anyone
        response = self.anonymous_client.get(url)
        for reuslt in response.data['results']:
            self.assertEqual(reuslt['has_followed'], False)

        # user2 has followed half of the followings
        response = self.user2_client.get(url)
        for reuslt in response.data['results']:
            if reuslt['user']['id'] % 2 == 0:
                self.assertEqual(reuslt['has_followed'], True)
            else:
                self.assertEqual(reuslt['has_followed'], False)

        # user1 has followed all of the followings
        response = self.user1_client.get(url)
        for reuslt in response.data['results']:
            self.assertEqual(reuslt['has_followed'], True)

    def _test_friendship_pagination(self, url, max_page_size, page_size):
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['has_next_page'], False)

        # Page 3 should be empty
        response = self.anonymous_client.get(url, {'page': 3})
        self.assertEqual(response.status_code, 404)

        # Test user cannot customize page size exceeds max_page_size
        response = self.anonymous_client.get(
            url, {'page': 1, 'page_size': max_page_size + 1})
        self.assertEqual(len(response.data['results']), max_page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        # Test user can customize page size
        response = self.anonymous_client.get(url, {'page': 1, 'page_size': 2})
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['total_pages'], page_size)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)
