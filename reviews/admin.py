from django.contrib import admin
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name","slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "price", "category", "image", "clicks")
    search_fields = ("name","slug")
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("name",)}
    list_display_links = ("name", "slug", "price", "category", "image")
