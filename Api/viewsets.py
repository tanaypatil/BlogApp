from rest_framework import viewsets, permissions
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet

from Api.models import Blog, Comment, BlogUser
from Api.permissions import IsAuthorOrReadOnly, IsUserOrReadOnly, IsSelfOrReadOnly, AllowUnauthenticatedOnly
from Api.serializers import BlogSerializer, CommentSerializer, BlogUserSerializer


class BlogUserViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = BlogUser.objects.all()
    serializer_class = BlogUserSerializer

    lookup_field = None

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        if self.action in ('retrieve', 'update', 'partial_update', 'destroy'):
            return BlogUser.objects.filter(pk=self.request.user.pk)
        else:
            return self.queryset

    def get_permissions(self):
        if self.action == 'create':
            return [AllowUnauthenticatedOnly()]
        return [permissions.IsAuthenticated(), IsSelfOrReadOnly()]


class BlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.action in ('list', 'retrieve', 'create'):
            return self.queryset.all()
        return self.queryset.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsUserOrReadOnly()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        if self.action in ('list', 'retrieve', 'create'):
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
