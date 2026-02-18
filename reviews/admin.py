from django.contrib import admin
from .models import Product, Category, Article, Click


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name","slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "price", "category", "image", "clicks", "rating", "asin")
    search_fields = ("name","slug")
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("name",)}
    list_display_links = ("name", "slug", "price", "category", "image")

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("products",)

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ("product", "created_at", "ip_address")
    list_filter = ("product", "created_at")
    search_fields = ("product__name", "ip_address", "user_agent")
    readonly_fields = ("product", "created_at", "ip_address", "user_agent")