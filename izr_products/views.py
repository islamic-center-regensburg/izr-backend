import json
from django.shortcuts import render
from rest_framework.response import Response

# Create your views here.
from rest_framework import generics
from .models import AboutMe, Blog, HeroImage, Imprint, LastProduct, Poem, Product
from .serializers import (
    AboutMeSerializer,
    HeroImageSerializer,
    LastProductSerializer,
    PoemSerializer,
    ProductSerializer,
    BlogSerializer,
    ImprintSerializer,
)


class ProductListDe(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Only return events where enabled is True
        return Product.objects.filter(language="de")

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Modify the response data to wrap it in a custom key
        return Response({"products": response.data})


class ProductListEn(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Only return events where enabled is True
        return Product.objects.filter(language="en")

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Modify the response data to wrap it in a custom key
        return Response({"products": response.data})


class LastProductListEn(generics.ListAPIView):
    queryset = LastProduct.objects.all()
    serializer_class = LastProductSerializer

    def get_queryset(self):
        # Only return events where enabled is True
        return LastProduct.objects.filter(language="en")

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Modify the response data to wrap it in a custom key
        return Response({"last_product": response.data})


class LastProductListDe(generics.ListAPIView):
    queryset = LastProduct.objects.all()
    serializer_class = LastProductSerializer

    def get_queryset(self):
        # Only return events where enabled is True
        return LastProduct.objects.filter(language="de")

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Modify the response data to wrap it in a custom key
        return Response({"last_product": response.data})


class HeroImageList(generics.ListAPIView):
    queryset = HeroImage.objects.all()
    serializer_class = HeroImageSerializer


class PoemListDe(generics.ListAPIView):
    queryset = Poem.objects.all()
    serializer_class = PoemSerializer

    def get_queryset(self):
        # Only return events where enabled is True
        return Poem.objects.filter(language="de")

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Modify the response data to wrap it in a custom key
        return Response({"poems": response.data})


class PoemListEn(generics.ListAPIView):
    queryset = Poem.objects.all()
    serializer_class = PoemSerializer

    def get_queryset(self):
        # Only return events where enabled is True
        return Poem.objects.filter(language="en")

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Modify the response data to wrap it in a custom key
        return Response({"poems": response.data})


class ImprintAPI(generics.ListAPIView):
    queryset = Imprint.objects.all()
    serializer_class = ImprintSerializer


class BlogPostListCreateViewDe(generics.ListCreateAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        # Only return events where enabled is True
        return Blog.objects.filter(language="de")

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Modify the response data to wrap it in a custom key
        return Response({"blogs": response.data})


class BlogPostListCreateViewEn(generics.ListCreateAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        # Only return events where enabled is True
        return Blog.objects.filter(language="en")

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Modify the response data to wrap it in a custom key
        return Response({"blogs": response.data})


from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .serializers import MessageSerializer
from django.http import JsonResponse


@csrf_exempt
def create_message(request):
    if request.method == "POST":
        # Parse JSON data if Content-Type is application/json
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST  # Use form data if not JSON

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AboutMeAPI(generics.ListAPIView):
    queryset = AboutMe.objects.all()
    serializer_class = AboutMeSerializer
