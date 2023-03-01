from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService


class FollowingUserUdSetMixin:

    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return set()
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id,
        )
        return user_id_set


class FollowerSerializer(serializers.ModelSerializer, FollowingUserUdSetMixin):
    user = UserSerializerForFriendship(source='from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed',)

    def get_has_followed(self, obj):
        return obj.from_user_id in self.following_user_id_set


class FollowingSerializer(serializers.ModelSerializer, FollowingUserUdSetMixin):
    user = UserSerializerForFriendship(source='to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed',)

    def get_has_followed(self, obj):
        return obj.to_user_id in self.following_user_id_set


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField(write_only=True)
    to_user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id', 'created_at',)

    def validate(self, data):
        # Check if the user is trying to follow non-existing user
        if not User.objects.filter(id=data['to_user_id']).exists():
            raise ValidationError({
                'message': 'User not found.'
            })

        # Check if the user is trying to follow himself/herself
        if data['from_user_id'] == data['to_user_id']:
            raise ValidationError({
                'message': 'You cannot follow yourself.'
            })

        # Check if the friendship already exists
        if Friendship.objects.filter(
            from_user_id=data['from_user_id'],
            to_user_id=data['to_user_id'],
        ).exists():
            raise ValidationError({
                'message': 'You have already followed this user.'
            })
        return data

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )
