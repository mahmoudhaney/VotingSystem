from rest_framework import generics, permissions
from .models import Election
from .serializers import ElectionSerializer
from .serializers import VoteSerializer
from django.db import transaction
from users.models import Candidate
from rest_framework.response import Response
from rest_framework import status

class ElectionListCreateView(generics.ListCreateAPIView):
    queryset = Election.objects.filter(is_active=False)
    serializer_class = ElectionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        elif self.request.method == 'GET':
            return [permissions.AllowAny()]

class VoteCreateView(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Ensure that all database operations within the post method are executed.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the candidate for which the vote is cast
        try:
            candidate = Candidate.objects.select_for_update().get(uuid=request.data['candidate_uuid'])
        except Candidate.DoesNotExist:
            return Response({"detail": "Candidate not found."}, status=status.HTTP_404_NOT_FOUND)

        # Increment the vote count for the candidate
        candidate.total_votes += 1
        candidate.save()

        # Create the vote
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
