from rest_framework import serializers
from marketplace.models import Product, Order, Variation

from django.conf import settings


class CreateProductSerializer(serializers.Serializer):
    """Serializer for creating new products.
    """

    name = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
    labels = serializers.JSONField(required=True)
    description = serializers.CharField()
    owner = serializers.CharField(required=True)
   

    def create(self, validated_data):

        return validated_data


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating orders.
    """


    variation_and_quantity = serializers.JSONField(required=True)
    total_amount = serializers.CharField(required=True)
    order_state = serializers.CharField(default=None)
    owner = serializers.CharField(required=True)

    def create(self, validated_data):

        return validated_data

class PurchaseOrderSerializer(serializers.Serializer):

    payment_reference = serializers.CharField()
    order_state = serializers.CharField()

    def create(self, validated_data):
        return validated_data

class VariationSerializer(serializers.ModelSerializer):

    class Meta :
        model = Variation
        fields = ['var_id', 'type', 'value', 'price', 'number_in_stock']

class ProductCategorySearchSerializer(serializers.ModelSerializer):
    """Serializer for searching products.
    """

    variations = VariationSerializer(source='variation_set', many=True, read_only=True)
   

    class Meta:
        model = Product
        fields = ['prod_id', 'name', 'category', 'description', 'owner', 'variations']

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data['id'] = data['prod_id']
        keys_to_pop = ['prod_id']
        for key in keys_to_pop:
            data.pop(key, None)
        return data


