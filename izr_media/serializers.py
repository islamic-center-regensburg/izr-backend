from rest_framework import serializers
from .models import (
    Blog,
    ContentItem,
    Event,
    Gallery,
    GalleryImage,
    Hadith,
    PrayerConfig,
    Statement,
)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "title",
            "title_ar",
            "flyer",
            "flyer_ar",
            "flyerTV",
            "subtitle",
            "subtitle_ar",
            "description",
            "description_ar",
        ]


class HadithSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hadith
        fields = ["data_ar", "data_de", "hadith_ar", "hadith_de"]


from rest_framework import serializers
from .models import Token


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ["os", "token", "test2"]  # Fields to be serialized

    def create(self, validated_data):
        return Token.objects.create(**validated_data)  # Create a single token instance


class PrayerConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerConfig
        fields = [
            "asr",
            "dhuhr",
            "fajr",
            "isha",
            "jumaa",
            "maghrib",
            "tarawih",
            "day_correction",
            "ramadan",
        ]


class ContentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = ["id", "content_type", "text", "image", "v_image"]


class BlogSerializer(serializers.ModelSerializer):
    content_items = ContentItemSerializer(many=True)  # Serialize related content items

    class Meta:
        model = Blog
        fields = ["id", "title", "author", "created_at", "updated_at", "content_items"]


class StatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statement
        fields = ["id", "type", "content"]


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = [
            "image",
            "is_vertical",
        ]  # Include only the necessary fields

    # For displaying the full URL of the image
    image = serializers.ImageField(use_url=True)


class GallerySerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, read_only=True)  # Include related images

    class Meta:
        model = Gallery
        fields = [
            "id",
            "title",
            "description",
            "images",
            "created_at",
        ]  # Specify fields to be serialized
