from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Store
from User.models import User
from User.serializers import UserSerializer



class StoreSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    # Accept user_id for write operations
    UserId = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)

    class Meta:
        model = Store
        fields = ['StoreUuid', 'StoreName', 'IsOpen', 'user', 'UserId', 'CreatedAt', 'UpdatedAt']

    