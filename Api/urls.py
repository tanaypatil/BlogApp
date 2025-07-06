from rest_framework import routers

from Api.viewsets import BlogViewSet, CommentViewSet, BlogUserViewSet

user_routes = BlogUserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
    'post': 'create'
})

router = routers.SimpleRouter()
router.register(r'blogs', BlogViewSet, basename='blog')
router.register(r'comments', CommentViewSet, basename='comment')
