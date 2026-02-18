from django.urls import path
from .views import ProductListView, ProductDetailView, ArticleListView, ArticleDetailView, HomePageView
from . import views

app_name = "reviews"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("products/", ProductListView.as_view(), name="product_list"),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("go/<slug:slug>/", views.affiliate_redirect, name="affiliate_redirect"),
    path("top/", views.TopProductsView.as_view(), name="top_products"),
    path("articles/", ArticleListView.as_view(), name="article_list"),
    path("articles/<slug:slug>/", ArticleDetailView.as_view(), name="article_detail"),
    path("analytics/", views.analytics_dashboard, name="analytics"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]