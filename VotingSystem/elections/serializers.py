from rest_framework import serializers
from .models import Vote, Election
from users.models import Candidate
from rest_framework.exceptions import ValidationError
import re
from datetime import datetime, timedelta

class ElectionSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Election
        fields = ['name', 'description', 'start_date', 'end_date', 'created_by', 'uuid']
        read_only_fields = ['uuid']

    def validate_name(self, value):
        """
        Validate the format of name EX: Election Name 2022
        """
        pattern = r'^[a-zA-Z ]+(?: (\d{4}))?$'
        match = re.match(pattern, value)
        if not match:
            raise serializers.ValidationError("Name must contain alphabetic characters, spaces, and optionally end with a four-digit year")

        year_str = match.group(1)
        if year_str:
            provided_year = int(year_str)
            current_year = datetime.now().year
            next_year = current_year + 1
            if provided_year not in {current_year, next_year}:
                raise serializers.ValidationError("Year must be related to the current or next year")
        return value

    def validate_description(self, value):
        """
        Validate the format of bio.
        """
        if value:
            pattern = r'^[a-zA-Z0-9, \-_()]+$'
            if not re.match(pattern, value):
                raise ValidationError("Bio must contain only alphabetic characters, numbers, and , ) - ( _ ")
        return value

    def validate(self, attrs):
        """
        Validate the 'start_date' and 'end_date' fields.
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        current_year = datetime.now().year
        next_year = current_year + 1
        if start_date.year not in {current_year, next_year} or end_date.year not in {current_year, next_year}:
            raise ValidationError("Start date and end date must be related to the current or next year")

        if end_date <= start_date:
            raise ValidationError("End date must be after start date")

        delta = end_date - start_date
        if not timedelta(days=2) <= delta <= timedelta(days=5):
            raise ValidationError("The difference between start date and end date must be between 2 and 5 days")

        return attrs

class VoteSerializer(serializers.ModelSerializer):
    election_uuid = serializers.UUIDField(write_only=True, required=True)
    candidate_uuid = serializers.UUIDField(write_only=True, required=True)
    voter = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Vote
        fields = ['election', 'candidate', 'voter', 'election_uuid', 'candidate_uuid']
        read_only_fields = ['election', 'candidate', 'voter']

    def validate(self, attrs):
        try:
            election = Election.objects.get(uuid=attrs['election_uuid'])
            if not election.is_active:
                raise ValidationError({"election_uuid": "Election must be active."})
        except Election.DoesNotExist:           
            raise ValidationError({"election_uuid": "No election found with the given UUID."})

        try:
            vote = Vote.objects.get(election=election, voter=self.context['request'].user)
            if vote:
                raise ValidationError({"voter": "You have already voted in this election."})
        except Vote.DoesNotExist:
            pass

        try:
            candidate = Candidate.objects.get(uuid=attrs['candidate_uuid'], election=election)
        except Candidate.DoesNotExist:
            raise ValidationError({"candidate": "This candidate not found for this election."})

        attrs['election'] = election
        attrs['candidate'] = candidate
        attrs.pop('election_uuid')
        attrs.pop('candidate_uuid')
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('election')
        representation.pop('candidate')
        representation['election_uuid'] = instance.election.uuid
        representation['candidate_uuid'] = instance.candidate.uuid
        return representation