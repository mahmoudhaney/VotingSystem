from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import JWTLoginSerializer, SignUpSerializer, PasswordChangeSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class JWTLoginView(TokenObtainPairView):
    serializer_class = JWTLoginSerializer

class SignupView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = (AllowAny,)

class PasswordChangeView(generics.UpdateAPIView):
    """
    Change User Password
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(instance=self.object, data=request.data)
        if serializer.is_valid():
            self.object = serializer.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)