from rest_framework import serializers
import uuid

class ProductSerializer(serializers.Serializer):
    Success  = serializers.BooleanField()
    ProductUuid = serializers.UUIDField()
    Name = serializers.CharField()
    IsAvailable = serializers.BooleanField()
    Price = serializers.FloatField()
    CategoryUuid = serializers.UUIDField()
    Description = serializers.CharField()
    ImageUrl = serializers.CharField()
 