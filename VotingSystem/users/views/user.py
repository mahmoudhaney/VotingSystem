from rest_framework import generics, permissions
from users.serializers.user import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user