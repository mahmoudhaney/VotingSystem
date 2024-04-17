from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
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

class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, style={'input_type' : 'password'}, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type' : 'password'})
    phone_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    id_proof_number = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'password2', 'phone_number', 'address', 'id_proof_number')
        extra_kwargs = {
            'first_name' : {'required' : True},
            'last_name' : {'required' : True},
            'email' : {'required' : True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields don't match."})


        if attrs.get('phone_number'):
            if not attrs['phone_number'].strip():
                raise serializers.ValidationError({"phone_number": "Phone number cannot be empty"})
            if User.objects.filter(phone_number=attrs['phone_number']).exists():
                raise serializers.ValidationError({"phone_number": "This phone number is already used"})

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
            raise serializers.ValidationError({"old_password": "Wrong password."})

        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password2": "Password fields don't match."})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
