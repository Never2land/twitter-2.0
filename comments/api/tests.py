from rest_framework.test import APIClient

from comments.models import Comment
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        self.tweet = self.create_tweet(self.user1)

    def test_list(self):
        # Missing tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # With tweet_id
        # No comments at first
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # Comments should be ordered by created_at time
        self.create_comment(self.user1, self.tweet, '1')
        self.create_comment(self.user2, self.tweet, '2')
        self.create_comment(self.user2, self.create_tweet(self.user2), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '1')
        self.assertEqual(response.data['comments'][1]['content'], '2')

        # user_id does not affect filter results
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.user1.id,
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_create(self):
        # Must login to create comment
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # Cannot create comment with no args
        response = self.user1_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # Cannot create comment with empty content
        response = self.user1_client.post(
            COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # Cannot create comment with no tweet_id
        response = self.user1_client.post(COMMENT_URL, {'content': 'test'})
        self.assertEqual(response.status_code, 400)

        # Cannot create comment with non-exist tweet_id
        response = self.user1_client.post(
            COMMENT_URL, {'tweet_id': 2, 'content': 'test'})
        self.assertEqual(response.status_code, 400)

        # Cannot create comment with too long content
        response = self.user1_client.post(
            COMMENT_URL, {'tweet_id': self.tweet.id, 'content': 'a' * 141})
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # Normal create
        response = self.user1_client.post(
            COMMENT_URL,
            {
                'tweet_id': self.tweet.id,
                'content': 'test',
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], 'test')

    def test_destroy(self):
        # Must login to destroy comment
        comment = self.create_comment(self.user1, self.tweet)
        response = self.anonymous_client.delete(
            COMMENT_DETAIL_URL.format(comment.id))
        self.assertEqual(response.status_code, 403)

        # Cannot destroy comment with non-exist comment_id
        response = self.user1_client.delete(COMMENT_DETAIL_URL.format(999))
        self.assertEqual(response.status_code, 404)

        # Cannot destroy comment with non-owner
        comment = self.create_comment(self.user2, self.tweet)
        response = self.user1_client.delete(
            COMMENT_DETAIL_URL.format(comment.id))
        self.assertEqual(response.status_code, 403)

        # Normal destroy
        comment = self.create_comment(self.user1, self.tweet)
        response = self.user1_client.delete(
            COMMENT_DETAIL_URL.format(comment.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.filter(id=comment.id).exists(), False)

    def test_update(self):
        # Must login to update comment
        comment = self.create_comment(self.user1, self.tweet)
        response = self.anonymous_client.put(
            COMMENT_DETAIL_URL.format(comment.id),
            {'content': 'new content'},
        )
        self.assertEqual(response.status_code, 403)

        # Cannot update comment with non-exist comment_id
        response = self.user1_client.put(
            COMMENT_DETAIL_URL.format(2),
            {'content': 'new content'},
        )
        self.assertEqual(response.status_code, 404)

        # Cannot update comment with non-owner
        comment = self.create_comment(self.user2, self.tweet)
        response = self.user1_client.put(
            COMMENT_DETAIL_URL.format(comment.id),
            {'content': 'new content'},
        )
        self.assertEqual(response.status_code, 403)

        # Cannot update comment with empty content
        comment = self.create_comment(self.user1, self.tweet)
        response = self.user1_client.put(
            COMMENT_DETAIL_URL.format(comment.id),
            {'content': ''},
        )
        self.assertEqual(response.status_code, 400)

        # Cannot update comment with too long content
        comment = self.create_comment(self.user1, self.tweet)
        response = self.user1_client.put(
            COMMENT_DETAIL_URL.format(comment.id),
            {'content': 'a' * 141},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # Normal update
        comment = self.create_comment(self.user1, self.tweet)
        response = self.user1_client.put(
            COMMENT_DETAIL_URL.format(comment.id),
            {'content': 'new content'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['content'], 'new content')
