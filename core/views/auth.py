from rest_framework import generics, permissions, response, status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from core.serializers.auth import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        data = {
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        return response.Response(data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return response.Response(UserSerializer(request.user).data)
