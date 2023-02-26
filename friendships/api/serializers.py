from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at',)


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at',)


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
