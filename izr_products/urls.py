from django.urls import path
from .views import (
    BlogPostListCreateViewEn,
    BlogPostListCreateViewDe,
    HeroImageList,
    LastProductListDe,
    LastProductListEn,
    create_message,
    PoemListEn,
    PoemListDe,
    ProductListDe,
    ProductListEn,
    ImprintAPI,
    AboutMeAPI,
)

urlpatterns = [
    path("products/de", ProductListDe.as_view(), name="product-list-de"),
    path("products/en", ProductListEn.as_view(), name="product-list-en"),
    path("last_product/de", LastProductListDe.as_view(), name="last-product-de"),
    path("last_product/en", LastProductListEn.as_view(), name="last-product-en"),
    path("poem/de", PoemListDe.as_view(), name="poem-de"),
    path("poem/en", PoemListEn.as_view(), name="poem-en"),
    path("hero/", HeroImageList.as_view(), name="hero-image"),
    path("imprint/", ImprintAPI.as_view(), name="imprint"),
    path("blog/en", BlogPostListCreateViewEn.as_view(), name="blog-post-list-en"),
    path("blog/de", BlogPostListCreateViewDe.as_view(), name="blog-post-list-de"),
    path("messages/", create_message, name="create_message"),
    path("about_me/", AboutMeAPI.as_view(), name="about_me"),
]
