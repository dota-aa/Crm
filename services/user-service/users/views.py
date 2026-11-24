from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, DestroyAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    UserUpdateDeleteSerializer,
    UserSafeUpdateSerializer,
    PermissionSerializer,
    RoleSerializer
)
from .models import (
    CustomPermission,
    Role
)
from .permissions import RoleBasePermission


User = get_user_model()


# ========================================================
# Health Check
# ========================================================
class HealthCheckView(APIView):
    """
    Check service status
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(data={
            "service": "user-service",
            "status": "ok",
        })


# ========================================================
#
# ========================================================
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Todo: send email for confirmation

        user = serializer.save()
        return Response(data=UserSerializer(user).data)


class TokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(instance=request.user)
        return Response(data=serializer.data)

    def patch(self, request):
        serializer = UserSafeUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(data=UserSerializer(instance=user).data)


# ========================================================
#
# ========================================================
class UserReadOnlyView(ReadOnlyModelViewSet):
    permission_classes = [RoleBasePermission]
    required_permissions = ['users:read']

    queryset = User.filtered_objects.all()
    serializer_class = UserSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['email', 'first_name', 'last_name']
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'last_name']


class UserUpdateView(UpdateAPIView):
    permission_classes = [RoleBasePermission]
    required_permissions = ['users:update']

    queryset = User.filtered_objects.all()
    serializer_class = UserUpdateDeleteSerializer


class UserDestroyView(DestroyAPIView):
    permission_classes = [RoleBasePermission]
    required_permissions = ['users:delete']

    queryset = User.filtered_objects.all()
    serializer_class = UserUpdateDeleteSerializer


class UserCreateView(CreateAPIView):
    permission_classes = [RoleBasePermission]
    required_permissions = ['users:create']

    queryset = User.filtered_objects.all()
    serializer_class = UserRegistrationView


# ========================================================
# Role and Permissions
# ========================================================
class PermissionView(ModelViewSet):
    permission_classes = [RoleBasePermission]
    required_permissions = ['permissions:all']

    queryset = CustomPermission.objects.all()
    serializer_class = PermissionSerializer

    def perform_create(self, serializer):
        serializer.save()
        cache.delete('users:permissions:all')

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete('users:permissions:all')
        cache.delete(f'users:permissions:{instance.pk}')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete('users:permissions:all')
        cache.delete(f'users:permissions:{instance.pk}')

    def retrieve(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        permission_id = kwargs.get(lookup_url_kwarg) or request.query_params.get('id')
        cache_key = f'users:permissions:{permission_id}'

        cache_data = cache.get(cache_key)
        # cache hit
        if cache_data:
            return Response(data=cache_data)

        # cache miss
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # set cache
        cache.set(cache_key, serializer.data)

        return Response(data=serializer.data)


    def list(self, request, *args, **kwargs):
        cache_key = 'users:permissions:all'

        cache_data = cache.get(cache_key)
        # cache hit
        if cache_data:
            return Response(data=cache_data)

        # cache miss
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        # set cache
        cache.set(cache_key, serializer.data)

        return Response(serializer.data)


class RoleView(ModelViewSet):
    permission_classes = [RoleBasePermission]
    required_permissions = ['roles:all']

    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def perform_create(self, serializer):
        serializer.save()
        cache.delete('users:roles:all')

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f'users:roles:{instance.pk}')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete('users:roles:all')
        cache.delete(f'users:roles:{instance.pk}')
