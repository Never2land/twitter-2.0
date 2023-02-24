from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)  
from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # pk is the user id
        # GET /api/friendships/{user_id}/followers/
        friendships = Friendship.objects.filter(
            to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response({
            'user_id': pk,
            'followers': serializer.data,
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        # pk is the user id
        # GET /api/friendships/{user_id}/followings/
        friendships = Friendship.objects.filter(
            from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response({
            'user_id': pk,
            'followings': serializer.data,
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # pk is the user id
        # POST /api/friendships/{user_id}/follow/

        # create the friendship
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })

        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'success': True,
            'message': 'Followed',
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # pk is the user id
        # POST /api/friendships/{user_id}/unfollow/

        # Raise 404 if no user with id=pk
        unfollow_user = self.get_object()

        # Raise 400 if user tries to unfollow himself
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete friendship
        deleted, _ = Friendship.objects.filter(
            from_user_id=request.user.id,
            to_user_id=pk,
        ).delete()
        return Response({
            'success': True,
            'deleted': deleted,
            'message': 'Unfollowed',
        }, status=status.HTTP_200_OK)
        


    def list(self, request):
        # GET /api/friendships/
        return Response({
            'followings': [],
        }, status=status.HTTP_200_OK)
