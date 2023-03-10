from notifications.models import Notification
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inbox.api.serializers import (
    NotificationSerializer,
    NotificationSerializerForUpdate,
)
from utils.decorators import required_params


class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated, )
    filterset_fields = ('unread',)

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(methods=['GET'], detail=False, url_path='unread-count')
    def unread_count(self, request, *args, **kwargs):
        # GET /api/notifications/unread-count
        count = self.get_queryset().filter(unread=True).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        # POST /api/notifications/mark-all-as-read
        marked_count = self.get_queryset().filter(unread=True).update(unread=False)
        return Response({'marked_count': marked_count},
                        status=status.HTTP_200_OK)

    @required_params(methods=['PUT'], params=['unread'])
    def update(self, request, *args, **kwargs):
        # serializer 的参数里面必须传入instance，这样在call serializer.save()
        # 的时候才会调用serializer的update方法， 否则会调用serializer的create方法
        serializer = NotificationSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(
            NotificationSerializer(serializer.instance).data,
            status=status.HTTP_200_OK,
        )
