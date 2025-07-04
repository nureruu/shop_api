from rest_framework import serializers
from .models import Category, Product, Review

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название категории не может быть пустым.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Название категории должно быть не менее 2 символов.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category']
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название товара не может быть пустым.")
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название товара должно быть не менее 3 символов.")
        return value
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Описание должно быть не менее 10 символов.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше 0.")
        return value
class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = '__all__'
    def validate_text(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Отзыв должен содержать не менее 5 символов.")
        return value

    def validate_stars(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value
class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'rating', 'reviews']

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(r.stars for r in reviews) / reviews.count(), 2)
        return None
class CategoryWithCountSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']
