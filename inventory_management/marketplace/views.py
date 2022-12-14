from django.shortcuts import render
from django.db.models import F

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings

from marketplace.serializers import (
    ProductCategorySearchSerializer,
    CreateOrderSerializer,
    CreateProductSerializer,
    PurchaseOrderSerializer
)
from marketplace.utils import ExternalJWTAuthentication, CustomPagination, convert_order_state_to_int
from marketplace.models import Order, Product, Variation

# Create your views here.

class CreateProductAPIView(APIView):
    """
    Create product
    """

    serializer_class = CreateProductSerializer

    # authentication_classes = (ExternalJWTAuthentication, )

    @swagger_auto_schema(request_body=CreateProductSerializer)
    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()

        try: 
            Product.objects.get(owner=validated_data['owner'], name=validated_data['name'], category=validated_data['category'])
            return Response(
                {
                    'status': False,
                    'message': 'Product already exists, try updating.'
                },
                status=status.HTTP_200_OK
            )
        except Product.DoesNotExist :
            product = Product.objects.create(
                name=validated_data['name'],
                prod_id=Product().generate_product_id(),
                category=validated_data['category'],
                description=validated_data['description'] if validated_data['description'] else None, 
                owner=validated_data['owner'],
               
            )
            for variant in validated_data['labels']:
                print(variant)
                temp = Variation.objects.create(
                    product=product,
                    var_id=Variation().generate_variation_id(),
                    type=validated_data['labels'][variant]['type'],
                    value=validated_data['labels'][variant]['value'],
                    price=validated_data['labels'][variant]['price'],
                    quantity=validated_data['labels'][variant]['number_in_stock'],
                    number_in_stock=validated_data['labels'][variant]['number_in_stock']
                )
            
            return Response(
                {
                    'status': True,
                    'message': 'Product - {} added successfully'.format(product.name),
                    'product_id': product.prod_id
                }, 
                status=status.HTTP_200_OK,
            )
        except Exception as e :
            return Response(
                {
                    'status': False,
                    'message': 'An error occured, try again later'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EditProductAPIview(APIView):
    """
    Update the quantity of a product of update or update given properties of a product
    """

    serializer_class = CreateProductSerializer

    # authentication_classes = (ExternalJWTAuthentication, )

    @swagger_auto_schema(request_body=CreateProductSerializer)
    def post(self, request, prod_id):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.save()

        try:
            product = Product.objects.get(prod_id=prod_id)

            product.name = validated_data['name'] if validated_data['name'] else product.name
            product.category = validated_data['category'] if validated_data['category'] else product.category
            product.description = validated_data['description'] if validated_data['description'] else product.description
            
            product.save()

            for item in validated_data['labels']:
              
                queryset = Variation.objects.filter(
                    product=product, 
                    type=validated_data['labels'][item]['type'], 
                    value=validated_data['labels'][item]['value'], 
                )
                if queryset.exists():
                    queryset.update(
                        price=validated_data['labels'][item]['price'],
                        quantity=F('quantity') + validated_data['labels'][item]['number_in_stock'], 
                        number_in_stock=F('number_in_stock') + validated_data['labels'][item]['number_in_stock']
                    )
                else :
                    Variation.objects.create(
                        product=product,
                        var_id=Variation().generate_variation_id(),
                        type=validated_data['labels'][item]['type'],
                        value=validated_data['labels'][item]['value'],
                        price=validated_data['labels'][item]['price'],
                        quantity=validated_data['labels'][item]['number_in_stock'],
                        number_in_stock=validated_data['labels'][item]['number_in_stock']
                    )
            return Response(
                {
                    'status': True,
                    'message': 'Product updated successfully'
                },
                status=status.HTTP_200_OK
            )

        except Product.DoesNotExist :
            return Response(
                {
                    'status': False,
                    'message': "Product not found"
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {
                    'status': False,
                    'message': 'An error occured, try again later'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteProductAPIView(APIView):

    # authentication_classes = (ExternalJWTAuthentication,)

    def post(self, request, prod_id):

        try:
            product = Product.objects.get(prod_id=prod_id)
            product.soft_delete()

            return Response(
                {
                    'status': True,
                    'message': 'Product deleted successfully'
                },
                status=status.HTTP_200_OK
            )

        except Product.DoesNotExist :
            return Response(
                {
                    'status': False,
                    'message': "Product not found"
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {
                    'status': False,
                    'message': 'An error occured, try again later'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductAPIListView(ListAPIView):
    """
    Endpoint for fetching all products or by their categories 
    
    """
    # authentication_classes = (ExternalJWTAuthentication, )
    serializer_class = ProductCategorySearchSerializer
    lookup_url_kwarg = 'category'
    pagination_class = CustomPagination

    def get(self, request, category=None):
        if category:

            # queryset = Product.objects.filter(category=category, is_deleted=False).order_by('variation__quantity', 'variation__number_in_stock')
            queryset = Product.objects.filter(category=category, is_deleted=False)

            paginate_queryset = self.paginate_queryset(queryset)
            temp = self.serializer_class(paginate_queryset, many=True).data
            response = self.get_paginated_response(temp)
            
            return Response(data=response.data, status=status.HTTP_200_OK)
        
        # queryset = Product.objects.filter(is_deleted=False).order_by('variation__quantity', '-variation__number_in_stock')
        queryset = Product.objects.filter(is_deleted=False)
        paginate_queryset = self.paginate_queryset(queryset)
        temp = self.serializer_class(paginate_queryset, many=True).data
        response = self.get_paginated_response(temp)
        
        return Response(data=response.data, status=status.HTTP_200_OK)


class ProductDetailAPIView(APIView):

    # authentication_classes = (ExternalJWTAuthentication,)

    def get(self, request, prod_id):

        related_list = []
        related_data = {}
        try: 
            product = Product.objects.get(prod_id=prod_id, is_deleted=False)
            related_products = Product.objects.filter(
                category=product.category,
                is_deleted=False
                ).exclude(id=product.id
                )[:10]

            product_data = {
                'id': product.prod_id,
                'name': product.name,
                'category': product.category,
                'description': product.description,
                'owner': product.owner,
                'variations': product.variation_set.all().values('var_id', 'type', 'value', 'price', 'number_in_stock'),
                
            }

            for item in related_products:

                related_data = {
                    'id': item.prod_id,
                    'name': item.name,
                    'category': item.category,
                    'owner': item.owner,
                    'variations': item.variation_set.values('var_id', 'type', 'value', 'price', 'number_in_stock'),
                   
                }
                related_list.append(related_data)

            return Response(
                {'status': True, 'data': product_data, "similar_products":related_data},
                status=status.HTTP_200_OK,
            )

        except Product.DoesNotExist :
            return Response(
                {
                    'status': False,
                    'message': "Product not found"
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            print(e)
            return Response(
                {
                    'status': False,
                    'message': 'An error occured, try again later'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreateOrderAPIView(APIView):
    """
    Add product to cart
    """

    serializer_class = CreateOrderSerializer

    # authentication_classes = (ExternalJWTAuthentication, )

    @swagger_auto_schema(request_body=CreateOrderSerializer)
    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()
        if not validated_data['order_state'] in ['paid', 'carted', 'cancelled', 'completed']:
            return Response(
                {
                    'status':False,
                    'message': 'order state not recognized ensure it is in the following [paid, carted, cancelled, completed]',
                },
                status=status.HTTP_200_OK
            )

        try: 
            order = Order.objects.create(
                order_id=Order().generate_order_id(),
                owner=validated_data['owner'],
                variation_and_quantity=validated_data['variation_and_quantity'],
                total_amount=validated_data['total_amount'],
                order_state=convert_order_state_to_int(validated_data['order_state']),
            )
            # update the number in stock of all products in the order
            
            
            for item in validated_data['variation_and_quantity']:
                Variation.objects.filter(
                    var_id=validated_data['variation_and_quantity'][item]['var_id']
                    ).update(number_in_stock=F('number_in_stock') - validated_data['variation_and_quantity'][item]['quantity'])
            
            return Response(
                {
                    'status': True,
                    'message': 'Product added to cart successfully',
                    'order_id': order.order_id
                },
                status=status.HTTP_200_OK
            )

        except Exception as e :
            print(e)
            return Response(
                {
                    'status': False,
                    'message': 'An error occured, try again later'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PurchaseOrderAPIView(APIView):
    
    serializer_class = PurchaseOrderSerializer
    authentication_class = (ExternalJWTAuthentication, )

    @swagger_auto_schema(request_body=PurchaseOrderSerializer)
    def post(self, request, order_id):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.save()

        if not validated_data['order_state'] in ['paid', 'carted', 'cancelled', 'completed']:
            return Response(
                {
                    'status':False,
                    'message': 'order state not recognized ensure it is in the following [paid, carted, cancelled, completed]',
                },
                status=status.HTTP_200_OK
            )

        try:
            order = Order.objects.get(order_id=order_id)

            order.payment_reference = validated_data['payment_reference']
            order.order_state = convert_order_state_to_int(validated_data['order_state'])
            order.save()

            return Response(
                {
                    'status': True,
                    'message': 'Product purchased successfully',
                    'order_id': order.order_id
                },
                status=status.HTTP_200_OK
            )

        except Order.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "Order not found"
                },
                status=status.HTTP_200_OK
            )
        except Exception as e :
            return Response(
                {
                    'status': False,
                    'message': 'An error occured, try again later'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class CancelOrderAPIView(APIView):
    
    # serializer_class = PurchaseOrderSerializer
    # authentication_class = (ExternalJWTAuthentication, )

    def post(self, request, order_id):

        
        try:
            order = Order.objects.get(order_id=order_id)

            order.order_state = convert_order_state_to_int('cancelled')
            order.save()

            # Release the product back and update number in stock
            for item in order.variation_and_quantity:
                Variation.objects.filter(var_id=order.variation_and_quantity[item]['var_id']
                ).update(number_in_stock=F('number_in_stock') + order.variation_and_quantity[item]['quantity'])


            return Response(
                {
                    'status': True,
                    'message': 'Order cancelled successfully',
                    'order_id': order.order_id
                },
                status=status.HTTP_200_OK
            )

        except Order.DoesNotExist:
            return Response(
                {
                    'status': False,
                    'message': "Order not found"
                },
                status=status.HTTP_200_OK
            )
        except Exception as e :
            print(e)
            return Response(
                {
                    'status': False,
                    'message': 'An error occured, try again later'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )