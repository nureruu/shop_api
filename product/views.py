from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Product, Review, Category
from rest_framework.viewsets import ModelViewSet
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer, ProductWithReviewsSerializer, CategoryWithCountSerializer
from django.db.models import Count
from .permissions import IsSuperUserOrReadOnly, IsStaffOrReadOnly, IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]
    def list(self, request, *args, **kwargs):
        queryset = Category.objects.annotate(products_count=Count('products'))
        serializer = CategoryWithCountSerializer(queryset, many=True)
        return Response(serializer.data)
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryWithCountSerializer
        return CategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]
    @action(detail=False, methods=['get'], url_path='reviews')
    def products_with_reviews(self, request):
        products = Product.objects.prefetch_related('reviews').all()
        serializer = ProductWithReviewsSerializer(products, many=True)
        return Response(serializer.data)
    

class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)