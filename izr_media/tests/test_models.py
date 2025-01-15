from django.test import TestCase
from izr_media.models import *

class TestModels(TestCase):
    def test_hero_image_model(self):
        hero_image = HeroImage.objects.create(image='test_image.jpg')
        self.assertEqual(hero_image.image, 'test_image.jpg')