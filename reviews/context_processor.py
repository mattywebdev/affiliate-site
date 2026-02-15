from .models import Category

def categories_nav(request):
    categories = Category.objects.all()
    return {'nav_categories': Category.objects.all()}