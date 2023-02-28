from notifications.models import Notification
from rest_framework.test import APIClient

from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATIONS_URL = '/api/notifications/'


class NotificationTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        self.tweet = self.create_tweet(self.user1)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.user2_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.user2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)


class NotificationsAPITests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        self.tweet = self.create_tweet(self.user1)

    def test_unread_count(self):
        self.user2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.tweet.id,
        })

        url = NOTIFICATIONS_URL + 'unread-count/'
        # Must login to get unread_count
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 403)

        # Must be the owner of the notification to get unread_count
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 0)

        # Get unread_count
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.user1, self.tweet, '1')
        self.user2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.user1_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)

        # Mark just one as read
        notification = Notification.objects.first()
        notification.unread = False
        notification.save()
        response = self.user1_client.get(NOTIFICATIONS_URL)
        self.assertEqual(response.data['count'], 2)
        response = self.user1_client.get(NOTIFICATIONS_URL, {'unread': True})
        self.assertEqual(response.data['count'], 1)
        response = self.user1_client.get(NOTIFICATIONS_URL, {'unread': False})
        self.assertEqual(response.data['count'], 1)

    def test_mark_all_as_read(self):
        self.user2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.tweet.id,
        })
        comment = self.create_comment(self.user1, self.tweet, '1')
        self.user2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = NOTIFICATIONS_URL + 'unread-count/'
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = NOTIFICATIONS_URL + 'mark-all-as-read/'

        # Must use get
        response = self.user1_client.get(mark_url)
        self.assertEqual(response.status_code, 405)

        # User must be the owner of the notification
        response = self.user2_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 0)
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        # Mark all as read
        response = self.user1_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)
