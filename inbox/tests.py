from notifications.models import Notification

from inbox.services import NotificationService
from testing.testcases import TestCase


class NotificationServiceTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')
        self.tweet = self.create_tweet(self.user1)

    def test_send_comment_notification(self):
        # do not dispatch notification if user comments on his own tweet
        comment = self.create_comment(self.user1, self.tweet, '1')
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 0)

        # Dispatch notification if user comments on others' tweet
        comment = self.create_comment(self.user2, self.tweet, '1')
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_like_notification(self):
        # do not dispatch notification if user likes his own tweet
        like = self.create_like(self.user1, self.tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)

        # Dispatch notification if user likes others' tweet
        like = self.create_like(self.user2, self.tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 1)

        # Dispatch notification if user likes others' comment
        comment = self.create_comment(self.user1, self.tweet, '1')
        like = self.create_like(self.user2, comment)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 2)

        # do not dispatch notification if user likes his own comment
        comment = self.create_comment(self.user2, self.tweet, '1')
        like = self.create_like(self.user2, comment)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 2)
