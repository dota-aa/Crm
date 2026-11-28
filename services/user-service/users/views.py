from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, DestroyAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample

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

    @extend_schema(
        tags=['users'],
        summary='Check user service status',
        description='Check if user service is responding.',
        responses={
            200: OpenApiResponse(description='The service is healthy.'),
        },
        examples=[
            OpenApiExample(
                'successful health check',
                value={"service": "", "status": "ok"},
                status_codes=["200"]
            )
        ]
    )
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

    @extend_schema(
        tags=['users'],
        summary='register a user',
        description='An api to register a user by email',
        request=UserRegistrationSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(
                description='invalid fields, missing required fields, or invalid data type'
            )
        },
        examples=[
            OpenApiExample(
                'user registration request',
                value={
                    "email": "test@test.com",
                    "first_name": "test",
                    "last_name": "test",
                    "password": "test",
                    "confirm_password": "test"
                },
                request_only=True
            ),
            OpenApiExample(
                'user registration response',
                value={
                    "pk": 1,
                    "email": "test@test.com",
                    "first_name": "test",
                    "last_name": "test",
                    "date_of_birth": "2000-2-2T3:12:12",
                    "is_active": True,
                    "is_admin": False,
                    "updated_at": "2000-2-2T3:12:12",
                    "created_at": "2000-2-2T3:12:12"
                }
            )
        ]
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Todo: send email for confirmation

        user = serializer.save()
        return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)


class TokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['users'],
        summary='Users details',
        description="Every authenticated user can see and update its detail",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(
                description='this endpoint is only for authenticated users'
            )
        },
    )
    def get(self, request):
        serializer = UserSerializer(instance=request.user)
        return Response(data=serializer.data)

    @extend_schema(
        tags=['users'],
        summary='Users details',
        description="Every authenticated user can see and change its detail",
        responses={
            200: UserSerializer,
            400: OpenApiResponse(
                description='invalid fields, missing required fields, or invalid data type'
            ),
            401: OpenApiResponse(
                description='this endpoint is only for authenticated users'
            ),
        },
    )
    def patch(self, request):
        serializer = UserSafeUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(data=UserSerializer(instance=user).data)


# ========================================================
#
# ========================================================
@extend_schema_view(
    list=extend_schema(
        tags=['users'],
        summary='List all users',
        description='List all users excluding soft deleted users',
        responses={
            200: UserSerializer(many=True)
        },
    ),
    retrieve=extend_schema(
        tags=['users'],
        summary='Retrieve a user',
        description='Retrieve a users by its pk(id)',
        responses={
            200: UserSerializer
        },
    )
)
class UserReadOnlyView(ReadOnlyModelViewSet):
    permission_classes = [RoleBasePermission]
    required_permissions = ['users:read']

    queryset = User.filtered_objects.all()
    serializer_class = UserSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['email', 'first_name', 'last_name']
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'last_name']


@extend_schema_view(
    put=extend_schema(
        tags=["users"],
        summary='Update users data',
        description='A user with `users:update` permission can change other users data',
        request=UserUpdateDeleteSerializer,
        responses={
            200: UserUpdateDeleteSerializer
        },
    ),
    patch=extend_schema(
        tags=["users"],
        summary='Update users data',
        description='A user with `users:update` permission can change other users data(this endpoint is only for partial updates)',
        request=UserUpdateDeleteSerializer,
        responses={
            200: UserUpdateDeleteSerializer
        },
    ),
)
class UserUpdateView(UpdateAPIView):
    permission_classes = [RoleBasePermission]
    required_permissions = ['users:update']

    queryset = User.filtered_objects.all()
    serializer_class = UserUpdateDeleteSerializer

@extend_schema_view(
    delete=extend_schema(
        tags=['users'],
        summary='Delete users',
        description='A user with `users:delete` permission can delete other users',
        responses={
            204: OpenApiResponse(
                description='User deleted.'
            )
        }
    )
)
class UserDestroyView(DestroyAPIView):
    permission_classes = [RoleBasePermission]
    required_permissions = ['users:delete']

    queryset = User.filtered_objects.all()
    serializer_class = UserUpdateDeleteSerializer


@extend_schema_view(
    post=extend_schema(
        tags=['users'],
        summary='Create user',
        description='A user with `users:create` permission can create user without otp confirmation',
        responses={
            201: UserRegistrationSerializer
        }
    )
)
class UserCreateView(CreateAPIView):
    permission_classes = [RoleBasePermission]
    required_permissions = ['users:create']

    queryset = User.filtered_objects.all()
    serializer_class = UserRegistrationSerializer


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
        cache.delete('users:permissions:all')
        cache.delete(f'users:permissions:{instance.id}')
        instance.delete()

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

        cache.delete('users:roles:all')
        cache.delete(f'users:roles:{instance.id}')
        instance.delete()
