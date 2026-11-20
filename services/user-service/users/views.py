from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserRegistrationSerializer, UserSerializer, CustomTokenObtainPairSerializer


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
