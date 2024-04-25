from rest_framework import generics, permissions
from users.serializers import CandidateSerializer

class CandidateCreateView(generics.CreateAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAdminUser]
