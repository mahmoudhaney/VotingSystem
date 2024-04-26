from rest_framework import generics, permissions
from .models import Election
from .serializers import ElectionSerializer, VoteSerializer
from users.serializers import CandidateSerializer, CandidateWithVotesSerializer
from django.db import transaction
from users.models import Candidate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from django.db.models import Sum

class ElectionListCreateView(generics.ListCreateAPIView):
    queryset = Election.objects.filter(is_active=False)
    serializer_class = ElectionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        elif self.request.method == 'GET':
            return [permissions.AllowAny()]

class ElectionCandidatesView(generics.RetrieveAPIView):
    serializer_class = CandidateSerializer

    def get_queryset(self):
        """
        Retrieves the candidates for the specified election.

        Returns a queryset of Candidate objects filtered by the
        election_uuid from the request's URL kwargs.

        Raises a NotFound exception if the election is not found.
        """
        election_uuid = self.kwargs.get('election_uuid')
        try:
            election = Election.objects.get(uuid=election_uuid)
            return Candidate.objects.filter(election=election)
        except Election.DoesNotExist:
            raise NotFound('Election not found.')

    def retrieve(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except NotFound as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

class ElectionDetailWithWinnerView(generics.RetrieveAPIView):
    serializer_class = ElectionSerializer

    def get_object(self):
        election_uuid = self.kwargs.get('election_uuid')
        try:
            return Election.objects.get(uuid=election_uuid)
        except Election.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        election = self.get_object()
        if not election:
            return Response({"detail": "Election not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the election is active
        if election.is_active:
            raise ValidationError("The election is currently active.")

        # Get all candidates for the election
        candidates = Candidate.objects.filter(election=election)
        candidates_serializer = CandidateWithVotesSerializer(candidates, many=True)

        # Determine the winner
        winner = candidates.order_by('-total_votes').first()
        winner_serializer = CandidateWithVotesSerializer(winner)

        # Calculate the total votes for the election
        election_total_votes = candidates.aggregate(total_votes=Sum('total_votes'))['total_votes'] or 0

        # Serialize the election data along with candidates and winner
        election_data = self.get_serializer(election).data
        election_data['candidates'] = candidates_serializer.data
        election_data['winner'] = winner_serializer.data
        election_data['election_total_votes'] = election_total_votes

        return Response(election_data)

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
