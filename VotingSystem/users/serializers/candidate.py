from rest_framework import serializers
from users.models import Candidate
from elections.models import Election
from rest_framework.exceptions import ValidationError
import re

class CandidateSerializer(serializers.ModelSerializer):
    election_uuid = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Candidate
        fields = ['name', 'bio', 'photo', 'election', 'election_uuid', 'uuid']
        read_only_fields = ['election', 'uuid']
    
    def validate_name(self, value):
        """
        Validate the format of name.
        """
        if not value.replace(' ', '').isalpha():         
            raise ValidationError("Name must contain only alphabetic characters and spaces")
        return value
    
    def validate_bio(self, value):
        """
        Validate the format of bio.
        """
        if value:
            pattern = r'^[a-zA-Z0-9, \-_()]+$'
            if not re.match(pattern, value):
                raise ValidationError("Bio must contain only alphabetic characters, numbers, and , ) - ( _ ")
        return value
    
    def validate_photo(self, value):
        """
        Validate the uploaded photo size.
        """
        if value.size > 5 * 1024 * 1024:
            raise ValidationError("Image size must be less than or equal to 5MB.")
        return value
    
    def validate(self, attrs):
        try:
            election = Election.objects.get(uuid=attrs['election_uuid'])
        except Election.DoesNotExist:           
            raise ValidationError({"election_uuid": "No election found with the given UUID."})

        if not election.is_active:
            raise ValidationError({"election_uuid": "Election must be active."})

        attrs['election'] = election
        attrs['admin'] = self.context['request'].user
        attrs.pop('election_uuid')
        return attrs

    def to_representation(self, instance):
        """
        Override the representation to exclude the election field.
        """
        representation = super().to_representation(instance)
        representation.pop('election')
        return representation

