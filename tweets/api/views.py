from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from newsfeeds.services import NewsFeedService
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from utils.decorators import required_params
from utils.paginations import EndlessPagination


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_params(params=['user_id'])
    def list(self, request):
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        tweets = self.paginate_queryset(tweets)
        serializer = TweetSerializer(
            tweets,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(
            tweet,
            context={'request': request},
        )
        return Response(serializer.data)

    def create(self, request):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=400)
        # Save will call create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(
            TweetSerializer(tweet, context={'request': request}).data,
            status=201,
        )
