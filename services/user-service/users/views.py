from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, DestroyAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    UserUpdateDeleteSerializer,
    UserSafeUpdateSerializer
)
from .permissions import CustomPermission


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
    permission_classes = [CustomPermission]
    required_permissions = ['users:read']

    queryset = User.filtered_objects.all()
    serializer_class = UserSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['email', 'first_name', 'last_name']
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'last_name']


class UserUpdateView(UpdateAPIView):
    permission_classes = [CustomPermission]
    required_permissions = ['users:update']

    queryset = User.filtered_objects.all()
    serializer_class = UserUpdateDeleteSerializer


class UserDestroyView(DestroyAPIView):
    permission_classes = [CustomPermission]
    required_permissions = ['users:delete']

    queryset = User.filtered_objects.all()
    serializer_class = UserUpdateDeleteSerializer


class UserCreateView(CreateAPIView):
    permission_classes = [CustomPermission]
    required_permissions = ['users:create']

    queryset = User.filtered_objects.all()
    serializer_class = UserRegistrationView
