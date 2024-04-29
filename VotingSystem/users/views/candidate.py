from rest_framework import generics, permissions
from users.models import Candidate
from users.serializers import CandidateSerializer
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status

class CandidateCreateView(generics.CreateAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAdminUser]

class CandidateRetrieveView(generics.RetrieveAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Retrieves the candidate for the specified UUID.

        Returns a queryset of Candidate objects filtered by the
        uuid from the request's URL kwargs.

        Raises a NotFound exception if the candidate is not found.
        """
        uuid = self.kwargs.get('candidate_uuid')
        try:
            return Candidate.objects.get(uuid=uuid)
        except Candidate.DoesNotExist:
            raise NotFound('Candidate not found.')

    def retrieve(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)
        except NotFound as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
