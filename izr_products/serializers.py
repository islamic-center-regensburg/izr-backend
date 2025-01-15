from rest_framework import serializers
from .models import AboutMe, Blog, ContentItem, HeroImage, Imprint, LastProduct, Poem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "photo", "description", "price", "amazon_link"]


class HeroImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroImage
        fields = "__all__"


class LastProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastProduct
        fields = ["id", "name", "photo", "poem", "price", "amazon_link"]


class PoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poem
        fields = ["content", "book_name"]


class ContentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = ["id", "content_type", "text", "image", "v_image"]


class ImprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imprint
        fields = "__all__"


class BlogSerializer(serializers.ModelSerializer):
    content_items = ContentItemSerializer(many=True)  # Serialize related content items

    class Meta:
        model = Blog
        fields = [
            "id",
            "type",
            "language",
            "title",
            "author",
            "created_at",
            "updated_at",
            "content_items",
        ]


from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["name", "email", "message", "date"]


class AboutMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutMe
        fields = ["title_en", "title_de", "content_en", "content_de", "updated_at"]
