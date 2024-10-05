from rest_framework import serializers
from .models import User
from rest_framework.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("Email","PhoneNo","RestaurantName")

class LoginSerializer(serializers.Serializer):
    UserName = serializers.CharField()
    PassWord = serializers.CharField()

    def validate(self, attrs):
        return super().validate(attrs)

class RegisterSerializer(serializers.ModelSerializer):
    class Meta :
        model = User
        fields = ("Email","PhoneNo","RestaurantName","password")

    def validate(self, data):
        if not "Email" in data:
            raise ValidationError({
                "Email":"Email not Provided"
            })
        if not "PhoneNo" in data:
            raise ValidationError({
                "PhoneNo":"PhoneNo not Provided"
            })
        if not "RestaurantName" in data:
            raise ValidationError({
                "RestaurantName":"RestaurantName not Provided"
            })
        if not "password" in data:
            raise ValidationError({
                "password":"password not Provided"
            })
        password_validation.validate_password(data["password"])

        
        return super().validate(data)
    def create(self, validated_data):
        validated_data["username"] = validated_data["Email"]
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

        
        

            