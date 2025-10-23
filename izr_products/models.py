from django.db import models

# Create your models here.



class Product(models.Model):
    LANG_CHOICES = [("en", "EN"), ("de", "DE")]
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to="product_photos/")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amazon_link = models.URLField(max_length=500)
    language = models.CharField(choices=LANG_CHOICES, max_length=50, default="de")

    def __str__(self):
        return self.name


class LastProduct(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to="product_photos/")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amazon_link = models.URLField(max_length=500)
    poem = models.TextField()
    LANG_CHOICES = [("en", "EN"), ("de", "DE")]
    language = models.CharField(choices=LANG_CHOICES, max_length=50, default="de")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Last Product"
        verbose_name_plural = "Last Product"


class Poem(models.Model):
    LANG_CHOICES = [("en", "EN"), ("de", "DE")]
    content = models.TextField()
    book_name = models.CharField(max_length=50)
    language = models.CharField(choices=LANG_CHOICES, max_length=50, default="de")

    def __str__(self):
        return self.book_name

    class Meta:
        verbose_name = "Home Page Poem"
        verbose_name_plural = "Home Page Poem"


# Main blog post model
class Blog(models.Model):
    TYPE_CHOICES = [("blog", "Blog"), ("project", "Project")]
    LANG_CHOICES = [("en", "EN"), ("de", "DE")]
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    type = models.CharField(choices=TYPE_CHOICES, max_length=50, default="blog")
    language = models.CharField(choices=LANG_CHOICES, max_length=50, default="de")
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


from django.db import models


class Imprint(models.Model):
    title = models.CharField(
        verbose_name="Title", max_length=255, default="Imprint Deutsch"
    )
    angaben_gem_tmg = models.TextField(verbose_name="Angaben gem. § 5 TMG")
    kontaktaufnahme = models.TextField(verbose_name="Kontaktaufnahme")
    haftung_inhalte = models.TextField(verbose_name="Haftung für Inhalte")
    haftung_externe_links = models.TextField(
        verbose_name="Haftungsbeschränkung für externe Links"
    )
    urheberrecht = models.TextField(verbose_name="Urheberrecht")
    widerrufsrecht = models.TextField(verbose_name="Widerrufsrecht")
    folgen_widerruf = models.TextField(verbose_name="Folgen des Widerrufs")
    ausschluss_erloeschensgruende = models.TextField(
        verbose_name="Ausschluss- bzw. Erlöschensgründe"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    def __str__(self):
        return f"Imprint last updated on {self.updated_at}"


class HeroImage(models.Model):
    image = models.ImageField(verbose_name="Hero Image")

    def __str__(self):
        return f"Hero Image"


class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"



class AboutMe(models.Model):
    title_en = models.CharField(verbose_name="Title (English)", max_length=255)
    title_de = models.CharField(verbose_name="Title (German)", max_length=255)
    content_en = models.TextField(verbose_name="Content (English)")
    content_de = models.TextField(verbose_name="Content (German)")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name = "About Me"
        verbose_name_plural = "About Me"

    def __str__(self):
        return f"About Me - Last updated: {self.updated_at}"

