from pprint import pprint

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import permissions
from rest_framework.generics import ListAPIView, CreateAPIView

from tweets.models import Tweet

from .pagination import StandardResultsPagination
from .serializers import TweetModelSerializer


class TweetListAPIView(ListAPIView):
    serializer_class = TweetModelSerializer
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        qs = Tweet.objects.all()
        query = self.request.GET.get('q')
        if query:
            return qs.filter(Q(content__icontains=query) | Q(user__username__icontains=query)).all()
        if self.kwargs.get('username'):  # tweets of the specified user
            return qs.filter(user__username__iexact=self.kwargs.get('username'))

        # tweets for home page
        current_user = self.request.user
        if current_user.is_authenticated():
            user_ids = [current_user.id]
            user_ids += current_user.profile.following.all()
            qs = qs.filter(user_id__in=user_ids).all()

        return qs


class TweetCreateAPIView(CreateAPIView):
    serializer_class = TweetModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        pprint(vars(serializer))
        serializer.save(user=self.request.user)
