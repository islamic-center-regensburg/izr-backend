from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Blog,
    CalculationMethod,
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
    # Display these fields in the list view
    list_display = ("os", "token", "test2")
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
    )
    list_editable = (
        "enabled",
        "asr",
        "dhuhr",
        "fajr",
        "isha",
        "jumaa",
        "maghrib",
    )


@admin.register(PrayerCalculationConfig)
class PrayerCalculationConfigAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        "config_name",
        "default_latitude",
        "default_longitude",
        "isha_angle",
        "fajr_angle",
        "jumaa_time",
    )

    # Fields to include in the edit form
    fieldsets = (
        ("General Configuration", {
            "fields": (
                "config_name",
                "default_latitude",
                "default_longitude",
            ),
        }),
        ("Jumaa & Ramadan", {
            "fields": (
                "jumaa_time",
                "tarawih_time",
                "ramadan",
            ),
        }),
        ("Tuning Parameters", {
            "fields": (
                "imsak_tune",
                "fajr_tune",
                "sunrise_tune",
                "dhuhr_tune",
                "asr_tune",
                "maghrib_tune",
                "sunset_tune",
                "isha_tune",
                "midnight_tune",
            ),
        }),
        ("Prayer Calculation Angles", {
            "fields": (
                "isha_angle",
                "fajr_angle",
            ),
        }),
    )

    # Prevent adding new instances (since only one instance is allowed)
    def has_add_permission(self, request):
        return False

    # Prevent deleting the instance (since only one instance is allowed)
    def has_delete_permission(self, request, obj=None):
        return False


class ContentItemInline(admin.TabularInline):
    model = ContentItem
    extra = 1  # How many extra empty fields to display
    fields = ["content_type", "text", "image", "v_image"]
    # You might want to manually order in the admin
    readonly_fields = ["order"]


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


@admin.register(CalculationMethod)
class CalculationMethodAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ("name", "short_name", "method_id")

    # Fields to include in the search bar
    search_fields = ("name", "short_name", "method_id")

    # Fields to filter by in the sidebar
    list_filter = ("method_id",)

    # Fields to display in the edit form
    fieldsets = (
        ("General Information", {
            "fields": ("name", "short_name", "method_id"),
        }),
    )
