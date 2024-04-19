from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .user import BasicUserSerializer
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer to add custom claims/payload to the token
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = str(user.email)
        return token

class JWTLoginSerializer(CustomTokenObtainPairSerializer):
    pass

class SignUpSerializer(BasicUserSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type' : 'password'}, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type' : 'password'})
    id_proof_number = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'password2', 'phone_number', 'address', 'id_proof_number')
        extra_kwargs = {
            'email' : {'required' : True},
        }

    def validate_id_proof_number(self, value):
        """
        Validate the format and length of id_proof_number.
        """
        if not value.isdigit():
            raise serializers.ValidationError("ID proof number must contain only digits.")
        if len(value) != 14:
            raise serializers.ValidationError("ID proof number must be exactly 14 digits long.")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['password'] != attrs['password2']:
            raise ValidationError({"password2": "Password fields don't match."})
        attrs.pop('password2')
        return attrs

    def create(self, validated_data):
        try:
            return User.objects.create_user(**validated_data)
        except IntegrityError as e:
            raise ValidationError({"error": str(e)})

    def to_representation(self, instance):
        refresh_token = CustomTokenObtainPairSerializer.get_token(user=instance)
        tokens = {
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token)
        }
        return tokens

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise ValidationError({"old_password": "Wrong password."})

        if attrs['new_password'] != attrs['new_password2']:
            raise ValidationError({"new_password2": "Password fields don't match."})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
