from django.conf import settings

from .models import Category
from .seo import absolute_url

def categories_nav(request):
    return {
        "nav_categories": Category.objects.all(),
        "site_name": settings.SITE_NAME,
        "site_url": settings.SITE_URL,
        "site_description": settings.SITE_DESCRIPTION,
        "default_og_image": absolute_url("/static/image.jpg"),
    }
