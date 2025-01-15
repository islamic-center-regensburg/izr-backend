from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Blog,
    ContentItem,
    Event,
    Gallery,
    GalleryImage,
    Hadith,
    PrayerCalculationConfig,
    PrayerConfig,
    Statement,
    Token,
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "enabled")
    search_fields = ("title", "title_ar", "subtitle", "subtitle_ar")


@admin.register(Hadith)
class HadithAdmin(admin.ModelAdmin):
    list_display = ("hadith_de",)  # Columns to display in the admin list view
    search_fields = (
        "data_ar",
        "data_de",
        "hadith_ar",
        "hadith_de",
    )  # Enable search for these fields


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("os", "token", "test2")  # Display these fields in the list view
    search_fields = ("os", "token")  # Enable search by os and token fields


@admin.register(PrayerConfig)
class PrayerConfigAdmin(admin.ModelAdmin):
    list_display_links = (
        "config_name",
    )  # Makes this field clickable to access the object
    list_display = (
        "config_name",
        "enabled",
        "asr",
        "dhuhr",
        "fajr",
        "isha",
        "jumaa",
        "maghrib",
        "tarawih",
        "day_correction",
        "ramadan",
    )
    list_editable = (
        "enabled",
        "asr",
        "dhuhr",
        "fajr",
        "isha",
        "jumaa",
        "maghrib",
        "tarawih",
        "day_correction",
        "ramadan",
    )


@admin.register(PrayerCalculationConfig)
class PrayerCalculationConfigAdmin(admin.ModelAdmin):
    list_display = (
        "calculation_angle",
        "default_longitude",
        "default_latitude",
    )
    search_fields = (
        "calculation_angle",
        "default_longitude",
        "default_latitude",
    )  # Searchable fields
    ordering = ("calculation_angle",)  # Default ordering
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "calculation_angle",
                    "default_longitude",
                    "default_latitude",
                )
            },
        ),
    )


class ContentItemInline(admin.TabularInline):
    model = ContentItem
    extra = 1  # How many extra empty fields to display
    fields = ["content_type", "text", "image", "v_image"]
    readonly_fields = ["order"]  # You might want to manually order in the admin


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    inlines = [ContentItemInline]
    list_display = ("title", "author", "created_at", "updated_at")


@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "type",
        "content",
    )
    search_fields = ("title",)


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    inlines = [GalleryImageInline]
    list_display = ("title", "created_at")
