from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ValidationError
from datetime import time


# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    title_ar = models.CharField(max_length=255, blank=True, null=True)
    enabled = models.BooleanField(default=True)
    flyer = models.ImageField(upload_to="izr_media/")
    flyer_ar = models.ImageField(upload_to="izr_media/")
    flyerTV = models.ImageField(upload_to="izr_media/")
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    subtitle_ar = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    description_ar = models.TextField()

    def __str__(self):
        return self.title or "Unnamed Event"


class Hadith(models.Model):
    data_ar = models.CharField(max_length=255)  # Arabic data
    data_de = models.CharField(max_length=255)  # German data
    hadith_ar = models.TextField()  # Arabic hadith
    hadith_de = models.TextField()  # German hadith

    def __str__(self):
        return self.hadith_de  # or return self.hadith_ar, depending on preference


class Token(models.Model):
    os = models.CharField(max_length=50)  # Operating system (e.g., 'ios', 'android')
    token = models.TextField()  # The actual token value
    test2 = models.BooleanField(default=False)  # Dummy key

    def __str__(self):
        return f"Token for OS: {self.os}, test2: {self.test2}"


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class PrayerCalculationConfig(models.Model):
    isha_angle = models.FloatField(
        validators=[MinValueValidator(12), MaxValueValidator(18)], default=0.0
    )  # Angle for prayer calculation
    fajr_angle = models.FloatField(
        validators=[MinValueValidator(12), MaxValueValidator(18)], default=0.0
    )  # Angle for prayer calculation
    
    jumaa_time = models.TimeField(
        default=time(12, 0)
    )  # Time for Juma prayer (12:00 PM)

    tarawih_time = models.TimeField(
        default=time(20, 30)
    )  # Time for Tarawih prayer (8:30 PM)

    default_longitude = models.FloatField(
        default=12.102841
    )  # Default longitude value for prayer calculation
    default_latitude = models.FloatField(
        default=49.007734
    )  # Default latitude value for prayer calculation

    correction_day = models.IntegerField(
        default=1
    )  # +/- day correction for Hijri calendar
    ramadan = models.CharField(
        max_length=3, choices=[("on", "On"), ("off", "Off")], default="off"
    )

    def save(self, *args, **kwargs):
        if not self.pk and PrayerCalculationConfig.objects.exists():
            raise ValidationError(
                "You can only create one Prayer Calculation Configuration instance."
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Prayer Times Calculations"

    @classmethod
    def get_solo_instance(cls):
        """Retrieve the single instance of this model, or create it if it doesn't exist."""
        obj, created = cls.objects.get_or_create(id=1)
        return obj

    class Meta:
        verbose_name = "Prayer Times Calculations"
        verbose_name_plural = "Prayer Times Calculations"



class PrayerConfig(models.Model):
    ASR = 15
    DHUHR = 15
    FAJR = 15
    ISHA = 5
    JUMAA = 0
    MAGHRIB = 5
    TARAWIH = 0

    PRAYER_TIME_CHOICES = [
        ("Asr", "Asr"),
        ("Dhuhr", "Dhuhr"),
        ("Fajr", "Fajr"),
        ("Isha", "Isha"),
        ("Jumaa", "Jumaa"),
        ("Maghrib", "Maghrib"),
        ("Tarawih", "Tarawih"),
    ]

    config_name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)
    asr = models.IntegerField(default=ASR)
    dhuhr = models.IntegerField(default=DHUHR)
    fajr = models.IntegerField(default=FAJR)
    isha = models.IntegerField(default=ISHA)
    jumaa = models.IntegerField(default=JUMAA)
    maghrib = models.IntegerField(default=MAGHRIB)

    def __str__(self):
        return f"PrayerConfig for Iqama Times"

    class Meta:
        verbose_name = "Iqama Times"
        verbose_name_plural = "Iqama Times"


# Main blog post model
class Blog(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# Abstract model for different types of content
class ContentItem(models.Model):
    ORDER_TYPE_CHOICES = [
        ("header", "Header"),
        ("paragraph", "Paragraph"),
        ("image", "Image"),
    ]

    blog = models.ForeignKey(
        Blog, related_name="content_items", on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField(default=0)  # To keep the content in order
    content_type = models.CharField(choices=ORDER_TYPE_CHOICES, max_length=50)
    text = models.TextField(blank=True, null=True)  # For headers and paragraphs
    image = models.ImageField(
        upload_to="blog_images/", blank=True, null=True
    )  # For images
    v_image = models.BooleanField(default=False, verbose_name="Vertical Image")

    class Meta:
        ordering = ["order"]  # To ensure the content is ordered by the "order" field

    def __str__(self):
        return f"{self.content_type} - {self.blog.title}"


class Gallery(models.Model):
    title = models.CharField(max_length=255, verbose_name="Gallery Title")
    description = models.TextField(
        blank=True, null=True, verbose_name="Gallery Description"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    gallery = models.ForeignKey(
        Gallery, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="gallery_images/", verbose_name="Upload Image")
    is_vertical = models.BooleanField(
        default=True, verbose_name="Is Vertical"
    )  # Boolean to toggle orientation
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image in {self.gallery.title}"


class Statement(models.Model):
    TYPE_CHOICES = [("about_us", "Über Uns"), ("statement", "Stellungnahme")]

    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(choices=TYPE_CHOICES, max_length=50, default="about_us")

    def __str__(self):
        return self.title
