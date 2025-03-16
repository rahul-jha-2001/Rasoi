# from .models import Product,Category
# from rest_framework.exceptions import ValidationError
# import uuid
# from rest_framework import serializers
# from .utils  import is_valid_uuid


# class category_serializer(serializers.ModelSerializer):
#     subcategories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

#     def validate(self, data):
#         store_uuid = data.get("store_uuid")
#         if not data:
#             raise ValidationError({"Detail": "No data provided."})

#         if not is_valid_uuid(store_uuid):
#             raise ValidationError({"store_uuid": "Not a vaild UUID."})
#         return data    
#     class Meta:
#         model =  Category
#         fields = "__all__"

# class product_serializer(serializers.ModelSerializer):
#     category_uuid = serializers.UUIDField(write_only =True)
#    # category = category_serializer()
    
#     def create(self, validated_data):
        
#         category_uuid = validated_data.pop('category_uuid')
#         try:
#             category = Category.objects.get(category_uuid=category_uuid)
#         except Category.DoesNotExist:
#             raise serializers.ValidationError({"category_uuid": "Category not found."})
        
#         # Create the product with the retrieved category
#         product = Product.objects.create(category=category, **validated_data)
#         return product
    
#     def update(self, instance, validated_data):
#         # Use get() to handle possible missing data
#         instance.name = validated_data.get('name', instance.name)
#         instance.price = validated_data.get('price', instance.price)
#         instance.is_available = validated_data.get('is_available', instance.is_available)
#         instance.description = validated_data.get('description', instance.description)
#         instance.image = validated_data.get('image', instance.image)

#         # Validate category if being updated
#         category_uuid = validated_data.get('category_uuid', None)
#         if category_uuid:
#             try:
#                 category = Category.objects.get(category_uuid=category_uuid)
#                 instance.category = category
#             except Category.DoesNotExist:
#                 raise serializers.ValidationError({"category_uuid": "Invalid category UUID."})

#         instance.save()
#         return instance
    
#     def validate(self, data):
#         if not data:
#             raise serializers.ValidationError({"detail": "No data provided."})

#         store_id = data.get("store_id")
#         if not is_valid_uuid(store_id):
#             raise serializers.ValidationError({"store_id": "Not a valid UUID."})

#         return data
    
#     class Meta:
#         model = Product
#         fields = ["product_uuid","store_id", "name", "is_available", "price", "description", "image","category_uuid","category"]