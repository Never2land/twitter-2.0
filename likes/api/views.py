from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from likes.api.serializers import LikeSerializer, LikeSerializerForCreate
from likes.models import Like
from utils.decorators import required_params


class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializerForCreate

    @required_params(method=['POST'], params=['content_type'])
    def create(self, request, *args, **kwargs):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        like = serializer.save()
        return Response(
            LikeSerializer(like).data,
            status=status.HTTP_201_CREATED,
        )