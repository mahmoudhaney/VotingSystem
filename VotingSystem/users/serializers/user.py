from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
import re

User = get_user_model()

class BasicUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    phone_number = serializers.CharField(required=False, validators=[UniqueValidator(queryset=User.objects.all())])
    address = serializers.CharField(required=False)

    def validate_phone_number(self, value):
        """
        Validate the format and uniqueness of phone_number.
        """
        if value:
            if not value.isdigit():
                raise ValidationError("Phone number must contain only digits.")
            if len(value) != 11:
                raise ValidationError("Phone number must be exactly 11 digits long.")
            if not value.startswith('01') or value[2] not in ['0', '1', '2', '5']:
                raise ValidationError("Invalid phone number format.")
        return value

    def validate_first_name(self, value):
        """
        Validate the format of first_name if it has a value.
        """
        if value:
            if not value.isalpha():
                raise ValidationError("First name must contain only alphabetic characters.")
        return value

    def validate_last_name(self, value):
        """
        Validate the format of last_name if it has a value.
        """
        if value:
            if not value.isalpha():
                raise ValidationError("Last name must contain only alphabetic characters.")
        return value

    def validate_address(self, value):
        """
        Validate the format of address using regex.
        """
        if value:
            pattern = r'^[a-zA-Z0-9, \-_()]+$'
            if not re.match(pattern, value):
                raise ValidationError("Address must contain only alphabetic characters, numbers, and , ) - ( _ ")
        return value

class UserSerializer(BasicUserSerializer):
    email = serializers.EmailField(required=False, validators=[UniqueValidator(queryset=User.objects.all())])
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'address', 'phone_number', 'id_proof_number']
        read_only_fields = ['username', 'id_proof_number']
