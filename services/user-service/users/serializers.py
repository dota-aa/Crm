import keyword

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser as User, CustomPermission, Role


class UserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # make all fields read only
        for field in self.fields:
            self.fields[field].read_only = True

    class Meta:
        model = User
        fields = (
            'pk',
            'first_name', 'last_name',
            'email', 'date_of_birth',
            'is_active', 'is_admin',
            'updated_at', 'created_at',
        )


class UserSafeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'date_of_birth',
        )


class UserUpdateDeleteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def update(self, instance, validated_data):
        """
        Default behavior saves raw password.
        """
        password = validated_data.pop('password', None)

        if password:
            instance.set_password(raw_password=password)

        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=64, write_only=True)
    confirm_password = serializers.CharField(max_length=64, write_only=True)


    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'confirm_password')

    def create(self, validated_data):
        """Use objects.create_user to hash the password"""
        return User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )

    def validate_email(self, value):
        """Check if email is unique"""
        # all users excluding soft deleted ones
        if User.filtered_objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        """
        first_name and last_name must be unique together.
        password and confirm_password must be same.

        """
        # check first_name and last_name
        # (this will be checked by serializers itself too as we have defined it in the model)
        users = User.filtered_objects.filter(
            first_name=attrs['first_name'], last_name=attrs['last_name'],
        )
        if users.exists():
            raise serializers.ValidationError("first_name and last_name must be unique together.")

        password = attrs.get('password')
        confirm_password = attrs.pop('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("Passwords must match.")

        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # add necessary tokens

        return token


# ========================================================
# Role and Permissions
# ========================================================
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
