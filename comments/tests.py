from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def test_comment(self):
        user = self.create_user('admin')
        tweet = self.create_tweet(user)
        comment = self.create_comments(user, tweet)
        self.assertNotEqual(comment.__str__(), None)
